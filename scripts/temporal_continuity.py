#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def safe_project_path(root: Path, rel: str) -> Path | None:
    candidate = (root / rel).resolve()
    resolved_root = root.resolve()
    return candidate if candidate != resolved_root and resolved_root in candidate.parents else None


def has_audio_stream(path: Path, ffprobe: str = 'ffprobe') -> bool:
    proc = subprocess.run(
        [ffprobe, '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'json', str(path)],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    obj = json.loads(proc.stdout or '{}')
    return bool(obj.get('streams'))


def validate_project(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / '04_generation/temporal_continuity.jsonl'
    try:
        rows = read_rows(path)
    except Exception as exc:
        return [f'{path.relative_to(root)}: {exc}']
    for row_number, record in enumerate(rows, 1):
        tail = record.get('temporal_tail')
        if tail is None:
            continue
        if not isinstance(tail, dict):
            errors.append(f'row {row_number}: temporal_tail must be object')
            continue
        duration = tail.get('duration_seconds')
        if not isinstance(duration, (int, float)) or duration <= 0:
            errors.append(f'row {row_number}: positive duration_seconds required')
        if tail.get('audio_policy') != 'strip':
            errors.append(f'row {row_number}: visual continuity tail audio_policy must be strip')
        rel = tail.get('path')
        if isinstance(rel, str) and rel:
            candidate = safe_project_path(root, rel)
            if candidate is None:
                errors.append(f'row {row_number}: tail path escapes project')
            elif candidate.exists() and tail.get('sha256') and sha256(candidate) != tail['sha256']:
                errors.append(f'row {row_number}: tail sha256 mismatch')
    return errors


def extract(source: Path, output: Path, duration: float, ffmpeg: str = 'ffmpeg', ffprobe: str = 'ffprobe') -> str:
    if duration <= 0:
        raise ValueError('duration must be positive')
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [ffmpeg, '-y', '-sseof', f'-{duration:g}', '-i', str(source), '-map', '0:v:0', '-an', '-c:v', 'copy', str(output)],
        check=True,
    )
    if has_audio_stream(output, ffprobe=ffprobe):
        raise RuntimeError('extracted temporal tail still contains an audio stream')
    return sha256(output)


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate or extract visual-only temporal continuity tails.')
    sub = parser.add_subparsers(dest='command', required=True)
    validate = sub.add_parser('validate')
    validate.add_argument('project_dir')
    extract_parser = sub.add_parser('extract-tail')
    extract_parser.add_argument('source')
    extract_parser.add_argument('output')
    extract_parser.add_argument('--duration', type=float, required=True)
    extract_parser.add_argument('--ffmpeg', default='ffmpeg')
    extract_parser.add_argument('--ffprobe', default='ffprobe')
    args = parser.parse_args()

    if args.command == 'extract-tail':
        digest = extract(Path(args.source), Path(args.output), args.duration, args.ffmpeg, args.ffprobe)
        print(json.dumps({'path': args.output, 'sha256': digest, 'audio_policy': 'strip'}, indent=2))
        return 0

    errors = validate_project(Path(args.project_dir).resolve())
    for error in errors:
        print('ERROR', error)
    print('OK temporal continuity' if not errors else f'FAILED {len(errors)}')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
