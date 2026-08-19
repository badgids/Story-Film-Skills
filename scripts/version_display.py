#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import argparse, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(r'^\d{2}\.\d{2}\.\d{2}$')

def display_version(canonical: str) -> str:
    canonical = canonical.strip()
    if not PATTERN.fullmatch(canonical):
        raise ValueError(f'invalid canonical version {canonical!r}; expected 00.00.00')
    return 'v' + '.'.join(str(int(part)) for part in canonical.split('.'))

def main() -> int:
    ap=argparse.ArgumentParser(description='Render fixed-width Story-Film version in human-readable form.')
    ap.add_argument('version', nargs='?')
    args=ap.parse_args()
    canonical=args.version or (ROOT/'VERSION').read_text(encoding='utf-8').strip()
    print(display_version(canonical))
    return 0
if __name__ == '__main__': raise SystemExit(main())
