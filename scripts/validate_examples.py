#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Validate the Story-Film Skills example/test prompt catalog."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/'examples/catalog.json'
EXPECTED={'video':3,'short-film':3,'movie':3}
PREFIX={'video':'VIDEO-5M-','short-film':'SHORT-20M-','movie':'MOVIE-90M-'}

def main():
    errors=[]
    if not CAT.is_file():
        errors.append('missing examples/catalog.json')
    else:
        data=json.loads(CAT.read_text(encoding='utf-8'))
        tiers=data.get('tiers',{})
        seen=set()
        for tier,count in EXPECTED.items():
            items=tiers.get(tier,[])
            if len(items)!=count: errors.append(f'{tier}: expected {count} prompts, got {len(items)}')
            for item in items:
                ident=str(item.get('id','')); path=ROOT/'examples'/str(item.get('path',''))
                if ident in seen: errors.append(f'duplicate id: {ident}')
                seen.add(ident)
                if not ident.startswith(PREFIX[tier]): errors.append(f'{ident}: wrong tier ID prefix')
                if not path.is_file(): errors.append(f'{ident}: missing prompt file {path.name}'); continue
                text=path.read_text(encoding='utf-8')
                if chr(0x2014) in text: errors.append(f'{path.name}: contains forbidden em dash')
                if 'Use Story-Film Skills to create a complete original' not in text: errors.append(f'{path.name}: prompt does not request complete original production')
                target=int(item.get('target_minutes',0))
                if tier=='video' and not 4 <= target <= 6: errors.append(f'{ident}: video target must be about 5 minutes')
                if tier=='short-film' and not 18 <= target <= 22: errors.append(f'{ident}: short target must be about 20 minutes')
                if tier=='movie' and target < 90: errors.append(f'{ident}: movie target must be at least 90 minutes')
        if len(seen)!=9: errors.append(f'expected 9 unique prompts, got {len(seen)}')
    for req in ['docs/examples/README.md','docs/examples/video-examples.md','docs/examples/short-film-examples.md','docs/examples/movie-examples.md','examples/README.md']:
        if not (ROOT/req).is_file(): errors.append('missing '+req)
    if errors:
        print('ERROR example prompts:')
        for e in errors: print('-',e)
        return 1
    print('OK example prompts: 9 prompts across 3 production levels')
    return 0
if __name__=='__main__': raise SystemExit(main())
