#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / 'VERSION'


def parse(v: str):
    if not re.fullmatch(r'\d{2}\.\d{2}\.\d{2}', v):
        raise ValueError(f'invalid version {v!r}; expected 00.00.00')
    return tuple(int(x) for x in v.split('.'))


def fmt(parts):
    return '.'.join(f'{n:02d}' for n in parts)


def main() -> int:
    ap = argparse.ArgumentParser(description='Increment Story-Film Skills patch version by exactly one.')
    ap.add_argument('--check-next', help='Verify that this value is exactly the next version without writing.')
    args = ap.parse_args()

    current = VERSION_FILE.read_text(encoding='utf-8').strip()
    major, minor, patch = parse(current)
    if patch >= 99:
        raise SystemExit('patch field is 99; project policy requires an explicit versioning decision before rollover')
    nxt = fmt((major, minor, patch + 1))

    if args.check_next:
        parse(args.check_next)
        if args.check_next != nxt:
            raise SystemExit(f'expected next version {nxt}, got {args.check_next}')
        print(nxt)
        return 0

    VERSION_FILE.write_text(nxt + '\n', encoding='utf-8')
    print(nxt)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
