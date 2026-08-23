#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import argparse, re
from pathlib import Path

from style_policy import is_comfyui_workflow_json

TEXT_EXT = {'.md', '.txt', '.fountain', '.json', '.jsonl', '.csv'}
WARN_PATTERNS = {
    'not just X but Y': re.compile(r'\bnot just\b.{0,80}\bbut\b', re.I),
    'a testament to': re.compile(r'\ba testament to\b', re.I),
    'a tapestry of': re.compile(r'\ba tapestry of\b', re.I),
    'delve into': re.compile(r'\bdelve into\b', re.I),
    'same as before shortcut': re.compile(r'\bsame as before\b', re.I),
    'as above shortcut': re.compile(r'\bas above\b', re.I),
    'previously described shortcut': re.compile(r'\bpreviously described\b', re.I),
}

def files(path: Path):
    if path.is_file():
        if path.suffix.lower() in TEXT_EXT:
            yield path
        return
    for p in path.rglob('*'):
        if p.is_file() and p.suffix.lower() in TEXT_EXT and '.git' not in p.parts:
            yield p

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('path')
    ap.add_argument('--strict-warnings', action='store_true')
    args = ap.parse_args()
    root = Path(args.path)
    errors, warnings = [], []
    for p in files(root):
        try:
            text = p.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        comfyui_workflow = is_comfyui_workflow_json(p, text)
        for i, line in enumerate(text.splitlines(), 1):
            if '\u2014' in line and not comfyui_workflow:
                errors.append(f'{p}:{i}: em dash')
            for label, rx in WARN_PATTERNS.items():
                if rx.search(line):
                    warnings.append(f'{p}:{i}: {label}')
    for x in errors:
        print('ERROR', x)
    for x in warnings:
        print('WARN ', x)
    if errors or (args.strict_warnings and warnings):
        raise SystemExit(1)
    print(f'OK: {len(errors)} errors, {len(warnings)} warnings')

if __name__ == '__main__':
    main()
