#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from media_runtime import MediaRuntimeError, project_path, project_root, read_json

TOOLS = {
    'ffmpeg': ['ffmpeg'],
    'ffprobe': ['ffprobe'],
    'magick': ['magick'],
    'melt': ['melt'],
    'kdenlive': ['kdenlive'],
    'shotcut': ['shotcut'],
    'mutool': ['mutool'],
    'pdftotext': ['pdftotext'],
    'pdftoppm': ['pdftoppm'],
    'soffice': ['soffice'],
    'node': ['node'],
    'npm': ['npm'],
    'npx': ['npx'],
}

FFMPEG_QUERIES = {
    'filters': ['-hide_banner', '-filters'],
    'encoders': ['-hide_banner', '-encoders'],
    'decoders': ['-hide_banner', '-decoders'],
    'formats': ['-hide_banner', '-formats'],
    'protocols': ['-hide_banner', '-protocols'],
    'devices': ['-hide_banner', '-devices'],
    'hwaccels': ['-hide_banner', '-hwaccels'],
    'bsfs': ['-hide_banner', '-bsfs'],
    'pix_fmts': ['-hide_banner', '-pix_fmts'],
    'sample_fmts': ['-hide_banner', '-sample_fmts'],
    'layouts': ['-hide_banner', '-layouts'],
    'colors': ['-hide_banner', '-colors'],
}

MAGICK_LISTS = {
    'formats': 'format',
    'delegates': 'delegate',
    'policy': 'policy',
    'resources': 'resource',
    'colors': 'color',
    'colorspaces': 'colorspace',
    'fonts': 'font',
    'configure': 'configure',
    'modules': 'module',
    'mime': 'mime',
    'type': 'type',
}

MLT_QUERIES = {
    'all': None,
    'consumers': 'consumers',
    'filters': 'filters',
    'links': 'links',
    'producers': 'producers',
    'transitions': 'transitions',
    'profiles': 'profiles',
    'presets': 'presets',
}


def which(name: str) -> str | None:
    return shutil.which(name)


def run_capture(argv: list[str], cwd: Path | None = None, check: bool = False) -> dict[str, Any]:
    try:
        p = subprocess.run(argv, cwd=str(cwd) if cwd else None, text=True, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, check=False)
    except FileNotFoundError:
        return {'available': False, 'returncode': 127, 'output': ''}
    if check and p.returncode:
        raise MediaRuntimeError(f'command failed ({p.returncode}): {argv[0]}\n{p.stdout}')
    return {'available': True, 'returncode': p.returncode, 'output': p.stdout}


def first_line(text: str) -> str:
    return next((x.strip() for x in text.splitlines() if x.strip()), '')


def discover(deep: bool = False) -> dict[str, Any]:
    out: dict[str, Any] = {
        'schema_version': 1,
        'captured_at': datetime.now(timezone.utc).isoformat(),
        'tools': {},
    }
    for key in TOOLS:
        exe = which(key)
        rec: dict[str, Any] = {'available': bool(exe), 'executable': exe or ''}
        if exe:
            if key in {'ffmpeg', 'ffprobe'}:
                info = run_capture([exe, '-version'])
            elif key == 'magick':
                info = run_capture([exe, '-version'])
            elif key == 'melt':
                info = run_capture([exe, '--version'])
            elif key == 'kdenlive':
                info = run_capture([exe, '--version'])
            elif key in {'mutool', 'pdftotext', 'pdftoppm'}:
                info = run_capture([exe, '-v'])
            else:
                info = run_capture([exe, '--version'])
            rec['version_line'] = first_line(info['output'])
        out['tools'][key] = rec

    if deep and out['tools']['ffmpeg']['available']:
        exe = out['tools']['ffmpeg']['executable']
        out['ffmpeg'] = {name: run_capture([exe] + args)['output'] for name, args in FFMPEG_QUERIES.items()}
    if deep and out['tools']['magick']['available']:
        exe = out['tools']['magick']['executable']
        out['imagemagick'] = {name: run_capture([exe, '-list', value])['output'] for name, value in MAGICK_LISTS.items()}
    if deep and out['tools']['melt']['available']:
        exe = out['tools']['melt']['executable']
        out['mlt'] = {}
        for name, value in MLT_QUERIES.items():
            args = [exe, '-query'] + ([value] if value else [])
            out['mlt'][name] = run_capture(args)['output']
    return out


def guard_raw(tool: str, args: list[str], allow_overwrite: bool) -> None:
    if tool == 'magick' and args and args[0].lower() == 'mogrify' and not allow_overwrite:
        raise MediaRuntimeError('magick mogrify edits files in place; pass --allow-overwrite only when that is explicitly intended')
    if tool == 'ffmpeg' and '-y' in args and not allow_overwrite:
        raise MediaRuntimeError('ffmpeg -y overwrites output files; pass --allow-overwrite only when that is explicitly intended')
    if any('\x00' in a for a in args):
        raise MediaRuntimeError('NUL bytes are not allowed in command arguments')


def raw_run(tool: str, args: list[str], cwd: Path | None, allow_overwrite: bool) -> int:
    exe = which(tool)
    if not exe:
        raise MediaRuntimeError(f'{tool} is not installed or not on PATH')
    guard_raw(tool, args, allow_overwrite)
    # No shell is used. Shell metacharacters remain literal arguments.
    p = subprocess.run([exe] + args, cwd=str(cwd) if cwd else None)
    return int(p.returncode)


def query(tool: str, category: str | None, name: str | None) -> int:
    exe = which(tool)
    if not exe:
        raise MediaRuntimeError(f'{tool} is not installed or not on PATH')
    if tool == 'ffmpeg':
        if name:
            if not category:
                raise MediaRuntimeError('--name requires --category such as filters, encoders, decoders, muxers, demuxers, bsfs')
            singular = {
                'filters': 'filter', 'encoders': 'encoder', 'decoders': 'decoder',
                'muxers': 'muxer', 'demuxers': 'demuxer', 'bsfs': 'bsf'
            }.get(category, category.rstrip('s'))
            return raw_run(tool, ['-hide_banner', '-h', f'{singular}={name}'], None, False)
        args = FFMPEG_QUERIES.get(category or 'filters')
        if not args:
            raise MediaRuntimeError(f'unknown FFmpeg query category {category!r}')
        return raw_run(tool, args, None, False)
    if tool == 'magick':
        if name:
            return raw_run(tool, ['-help', name], None, False)
        value = MAGICK_LISTS.get(category or 'formats')
        if not value:
            raise MediaRuntimeError(f'unknown ImageMagick list category {category!r}')
        return raw_run(tool, ['-list', value], None, False)
    if tool == 'melt':
        value = MLT_QUERIES.get(category or 'all')
        args = ['-query'] + ([value] if value else [])
        if name:
            args = ['-query', name]
        return raw_run(tool, args, None, False)
    raise MediaRuntimeError('query supports ffmpeg, magick, or melt')


def looks_absolute_path(value: str) -> bool:
    return value.startswith('/') or bool(re.match(r'^[A-Za-z]:[\\/]', value))


def validate_manifest(root: Path, manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get('schema_version') != 1:
        errors.append('schema_version must be 1')
    steps = manifest.get('steps')
    if not isinstance(steps, list) or not steps:
        errors.append('steps must be a nonempty array')
        return errors
    ids: set[str] = set()
    for i, step in enumerate(steps, 1):
        prefix = f'step {i}'
        sid = step.get('step_id', '')
        if not re.fullmatch(r'TOOL-\d{3}', sid or ''):
            errors.append(f'{prefix}: step_id must be TOOL-###')
        elif sid in ids:
            errors.append(f'{prefix}: duplicate step_id {sid}')
        ids.add(sid)
        tool = step.get('tool')
        if tool not in {'ffmpeg', 'ffprobe', 'magick', 'melt'}:
            errors.append(f'{prefix}: unsupported tool {tool!r}')
        args = step.get('args')
        if not isinstance(args, list) or not all(isinstance(x, str) for x in args):
            errors.append(f'{prefix}: args must be an array of strings')
        for field in ('inputs', 'outputs'):
            values = step.get(field, [])
            if not isinstance(values, list):
                errors.append(f'{prefix}: {field} must be an array')
                continue
            for value in values:
                if not isinstance(value, str) or not value:
                    errors.append(f'{prefix}: {field} entries must be nonempty strings')
                elif looks_absolute_path(value):
                    errors.append(f'{prefix}: {field} path must be project-relative: {value}')
                else:
                    try:
                        project_path(root, value)
                    except Exception as exc:
                        errors.append(f'{prefix}: invalid {field} path {value}: {exc}')
        if tool == 'magick' and isinstance(args, list) and args and args[0].lower() == 'mogrify' and not step.get('allow_overwrite'):
            errors.append(f'{prefix}: mogrify requires allow_overwrite=true')
        if tool == 'ffmpeg' and isinstance(args, list) and '-y' in args and not step.get('allow_overwrite'):
            errors.append(f'{prefix}: ffmpeg -y requires allow_overwrite=true')
    return errors


def run_manifest(root: Path, manifest: dict[str, Any], dry_run: bool = False) -> dict[str, Any]:
    errors = validate_manifest(root, manifest)
    if errors:
        raise MediaRuntimeError('; '.join(errors))
    report: dict[str, Any] = {
        'schema_version': 1,
        'started_at': datetime.now(timezone.utc).isoformat(),
        'status': 'dry-run' if dry_run else 'running',
        'steps': [],
    }
    for step in manifest['steps']:
        exe = which(step['tool'])
        rec = {'step_id': step['step_id'], 'tool': step['tool'], 'args': step['args'], 'status': 'pending'}
        if not exe:
            rec['status'] = 'blocked'
            rec['reason'] = f"{step['tool']} is not installed or not on PATH"
            report['steps'].append(rec)
            report['status'] = 'blocked'
            break
        if dry_run:
            rec['status'] = 'dry-run'
            report['steps'].append(rec)
            continue
        for inp in step.get('inputs', []):
            p = project_path(root, inp)
            if not p.exists():
                rec['status'] = 'blocked'
                rec['reason'] = f'missing input {inp}'
                report['steps'].append(rec)
                report['status'] = 'blocked'
                return report
        guard_raw(step['tool'], step['args'], bool(step.get('allow_overwrite')))
        p = subprocess.run([exe] + step['args'], cwd=str(root), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        rec['returncode'] = p.returncode
        rec['output_tail'] = '\n'.join(p.stdout.splitlines()[-80:])
        if p.returncode:
            rec['status'] = 'failed'
            report['steps'].append(rec)
            report['status'] = 'failed'
            return report
        missing = [x for x in step.get('outputs', []) if not project_path(root, x).exists()]
        if missing:
            rec['status'] = 'failed'
            rec['reason'] = f'expected outputs missing: {missing}'
            report['steps'].append(rec)
            report['status'] = 'failed'
            return report
        rec['status'] = 'pass'
        report['steps'].append(rec)
    if report['status'] == 'running':
        report['status'] = 'pass'
    report['finished_at'] = datetime.now(timezone.utc).isoformat()
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description='Version-adaptive FFmpeg, FFprobe, MLT, and ImageMagick runtime bridge.')
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('discover', help='Discover installed media/editing runtimes and optionally their deep capabilities.')
    p.add_argument('--project')
    p.add_argument('--output', default='00_project/tool_capabilities.json')
    p.add_argument('--deep', action='store_true')

    p = sub.add_parser('query', help='Query the installed capability surface of FFmpeg, MLT, or ImageMagick.')
    p.add_argument('tool', choices=['ffmpeg', 'magick', 'melt'])
    p.add_argument('--category')
    p.add_argument('--name')

    p = sub.add_parser('run', help='Run one tool directly without a shell. Put tool arguments after --.')
    p.add_argument('tool', choices=['ffmpeg', 'ffprobe', 'magick', 'melt'])
    p.add_argument('--cwd')
    p.add_argument('--allow-overwrite', action='store_true')
    p.add_argument('args', nargs=argparse.REMAINDER)

    p = sub.add_parser('manifest', help='Validate or run a portable multi-step media-tool manifest.')
    p.add_argument('project_dir')
    p.add_argument('manifest')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--report', default='05_post/tool_runs/latest.json')

    args = ap.parse_args()
    if args.cmd == 'discover':
        data = discover(args.deep)
        if args.project:
            root = project_root(args.project)
            out = project_path(root, args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(data, indent=2))
        return 0
    if args.cmd == 'query':
        return query(args.tool, args.category, args.name)
    if args.cmd == 'run':
        raw_args = args.args[1:] if args.args and args.args[0] == '--' else args.args
        cwd = Path(args.cwd).expanduser().resolve() if args.cwd else None
        return raw_run(args.tool, raw_args, cwd, args.allow_overwrite)
    if args.cmd == 'manifest':
        root = project_root(args.project_dir)
        mp = project_path(root, args.manifest, must_exist=True)
        manifest = read_json(mp)
        errors = validate_manifest(root, manifest)
        if errors:
            for e in errors:
                print('ERROR', e)
            return 2
        report = run_manifest(root, manifest, args.dry_run)
        rp = project_path(root, args.report)
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(report, indent=2))
        return 0 if report['status'] in {'pass', 'dry-run'} else 2
    return 2


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except MediaRuntimeError as exc:
        print(f'ERROR {exc}')
        raise SystemExit(2)
