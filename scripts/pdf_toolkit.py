#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from media_runtime import MediaRuntimeError
from document_companions import generate as generate_companion


def which(name: str) -> str | None:
    return shutil.which(name)


def discover() -> dict:
    tools = {}
    for name in ('mutool', 'pdftotext', 'pdftoppm', 'pdfimages', 'qpdf'):
        exe = which(name)
        rec = {'available': bool(exe), 'executable': exe or ''}
        if exe:
            argv = [exe, '-v'] if name == 'mutool' else [exe, '-v']
            p = subprocess.run(argv, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
            rec['version_line'] = next((x.strip() for x in p.stdout.splitlines() if x.strip()), '')
        tools[name] = rec
    try:
        import pypdf
        tools['pypdf'] = {'available': True, 'version': getattr(pypdf, '__version__', '')}
    except Exception:
        tools['pypdf'] = {'available': False}
    return {'schema_version': 1, 'tools': tools}


def require_pypdf():
    try:
        from pypdf import PdfReader, PdfWriter
    except Exception as exc:
        raise MediaRuntimeError('pypdf is required for this fallback operation') from exc
    return PdfReader, PdfWriter


def info(path: Path) -> dict:
    PdfReader, _ = require_pypdf()
    reader = PdfReader(str(path))
    meta = reader.metadata or {}
    return {
        'pages': len(reader.pages),
        'encrypted': bool(reader.is_encrypted),
        'metadata': {str(k): str(v) for k, v in meta.items()},
    }


def text_extract(path: Path, output: Path) -> None:
    exe = which('pdftotext')
    if exe:
        subprocess.run([exe, '-layout', str(path), str(output)], check=True)
        return
    PdfReader, _ = require_pypdf()
    reader = PdfReader(str(path))
    text = '\n\n'.join((page.extract_text() or '') for page in reader.pages)
    output.write_text(text, encoding='utf-8')


def render(path: Path, out_prefix: Path, dpi: int) -> list[str]:
    mutool = which('mutool')
    if mutool:
        pattern = str(out_prefix) + '-%03d.png'
        subprocess.run([mutool, 'draw', '-q', '-r', str(dpi), '-o', pattern, str(path)], check=True)
        return sorted(str(p) for p in out_prefix.parent.glob(out_prefix.name + '-*.png'))
    pdftoppm = which('pdftoppm')
    if not pdftoppm:
        raise MediaRuntimeError('render requires mutool or pdftoppm')
    subprocess.run([pdftoppm, '-png', '-r', str(dpi), str(path), str(out_prefix)], check=True)
    return sorted(str(p) for p in out_prefix.parent.glob(out_prefix.name + '-*.png'))


def merge(inputs: list[Path], output: Path) -> None:
    PdfReader, PdfWriter = require_pypdf()
    writer = PdfWriter()
    for path in inputs:
        reader = PdfReader(str(path))
        for page in reader.pages:
            writer.add_page(page)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('wb') as f:
        writer.write(f)


def split(path: Path, out_dir: Path) -> list[str]:
    PdfReader, PdfWriter = require_pypdf()
    reader = PdfReader(str(path))
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for i, page in enumerate(reader.pages, 1):
        writer = PdfWriter(); writer.add_page(page)
        out = out_dir / f'page-{i:03d}.pdf'
        with out.open('wb') as f:
            writer.write(f)
        outputs.append(str(out))
    return outputs


def rotate(path: Path, output: Path, degrees: int, pages: set[int] | None) -> None:
    PdfReader, PdfWriter = require_pypdf()
    reader = PdfReader(str(path)); writer = PdfWriter()
    for i, page in enumerate(reader.pages, 1):
        if pages is None or i in pages:
            page.rotate(degrees)
        writer.add_page(page)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('wb') as f:
        writer.write(f)


def clean(path: Path, output: Path) -> None:
    exe = which('mutool')
    if not exe:
        raise MediaRuntimeError('mutool clean requested but mutool is not installed')
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([exe, 'clean', str(path), str(output)], check=True)


def grep_text(path: Path, pattern: str) -> list[str]:
    exe = which('mutool')
    if exe:
        p = subprocess.run([exe, 'grep', pattern, str(path)], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if p.returncode not in {0, 1}:
            raise MediaRuntimeError(p.stderr.strip() or 'mutool grep failed')
        return [x for x in p.stdout.splitlines() if x.strip()]
    PdfReader, _ = require_pypdf()
    reader = PdfReader(str(path))
    q = pattern.lower()
    out = []
    for i, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ''
        for line in text.splitlines():
            if q in line.lower():
                out.append(f'{i}: {line}')
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description='Safe local PDF toolkit with optional MuPDF mutool support.')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('discover')
    p = sub.add_parser('info'); p.add_argument('input')
    p = sub.add_parser('text'); p.add_argument('input'); p.add_argument('output')
    p = sub.add_parser('render'); p.add_argument('input'); p.add_argument('out_prefix'); p.add_argument('--dpi', type=int, default=120)
    p = sub.add_parser('merge'); p.add_argument('output'); p.add_argument('inputs', nargs='+')
    p = sub.add_parser('split'); p.add_argument('input'); p.add_argument('out_dir')
    p = sub.add_parser('rotate'); p.add_argument('input'); p.add_argument('output'); p.add_argument('--degrees', type=int, choices=[90,180,270], required=True); p.add_argument('--pages')
    p = sub.add_parser('clean'); p.add_argument('input'); p.add_argument('output')
    p = sub.add_parser('grep'); p.add_argument('input'); p.add_argument('pattern')
    args = ap.parse_args()
    if args.cmd == 'discover':
        print(json.dumps(discover(), indent=2)); return 0
    if args.cmd == 'info':
        print(json.dumps(info(Path(args.input).expanduser().resolve()), indent=2)); return 0
    if args.cmd == 'text':
        out=Path(args.output).expanduser().resolve(); out.parent.mkdir(parents=True,exist_ok=True); text_extract(Path(args.input).expanduser().resolve(), out); print(out); return 0
    if args.cmd == 'render':
        print(json.dumps(render(Path(args.input).expanduser().resolve(), Path(args.out_prefix).expanduser().resolve(), args.dpi), indent=2)); return 0
    if args.cmd == 'merge':
        out=Path(args.output).expanduser().resolve(); merge([Path(x).expanduser().resolve() for x in args.inputs], out); generate_companion(out); print(json.dumps({'pdf':str(out),'markdown':str(out.with_suffix('.md'))}, indent=2)); return 0
    if args.cmd == 'split':
        outputs=split(Path(args.input).expanduser().resolve(), Path(args.out_dir).expanduser().resolve()); companions=[str(generate_companion(Path(x))) for x in outputs]; print(json.dumps({'pdfs':outputs,'markdown':companions}, indent=2)); return 0
    if args.cmd == 'rotate':
        pages = None if not args.pages else {int(x) for x in args.pages.split(',') if x.strip()}
        out=Path(args.output).expanduser().resolve(); rotate(Path(args.input).expanduser().resolve(), out, args.degrees, pages); generate_companion(out); print(json.dumps({'pdf':str(out),'markdown':str(out.with_suffix('.md'))}, indent=2)); return 0
    if args.cmd == 'clean':
        out=Path(args.output).expanduser().resolve(); clean(Path(args.input).expanduser().resolve(), out); generate_companion(out); print(json.dumps({'pdf':str(out),'markdown':str(out.with_suffix('.md'))}, indent=2)); return 0
    if args.cmd == 'grep':
        print('\n'.join(grep_text(Path(args.input).expanduser().resolve(), args.pattern))); return 0
    return 2


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (MediaRuntimeError, subprocess.CalledProcessError) as exc:
        print(f'ERROR {exc}')
        raise SystemExit(2)
