#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

RESOURCE_FILE = re.compile(r'\.(?:safetensors|gguf|ckpt|pth|pt|bin)$', re.I)
WINDOWS_ABS = re.compile(r'^[A-Za-z]:[\\/]')
UNIX_HOME = re.compile(r'^/(?:home|Users)/[^/]+/')
DROP_KEYS = {'videopreview', 'preview', 'fullpath', 'output_path'}


def scrub(value, redactions: list[str], key: str = ''):
    if isinstance(value, dict):
        return {name: scrub(child, redactions, name) for name, child in value.items() if name.lower() not in DROP_KEYS}
    if isinstance(value, list):
        return [scrub(child, redactions, key) for child in value]
    if isinstance(value, str):
        if WINDOWS_ABS.search(value) or UNIX_HOME.search(value) or RESOURCE_FILE.search(value):
            return '__STORY_FILM_RESOURCE__'
        result = value
        for term in redactions:
            if term:
                result = re.sub(re.escape(term), 'SUBJECT', result, flags=re.I)
        return result
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description='Sanitize a preserved ComfyUI workflow into a portable topology blueprint.')
    parser.add_argument('source')
    parser.add_argument('output')
    parser.add_argument('--redact', action='append', default=[], help='Source-project text to replace with SUBJECT. Repeat as needed.')
    args = parser.parse_args()
    obj = scrub(json.loads(Path(args.source).read_text(encoding='utf-8')), args.redact)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
