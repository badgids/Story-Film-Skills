#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath

REF_RX = re.compile(r'^REF-\d{3,}$')


def portable(value: str) -> bool:
    if not value:
        return True
    if value.startswith('/') or value.startswith('~') or re.match(r'^[A-Za-z]:[\\/]', value):
        return False
    return not PurePosixPath(value.replace('\\', '/')).is_absolute()


def validate(obj: dict) -> list[str]:
    errors=[]
    if obj.get('schema_version') != 1:
        errors.append('schema_version must be 1')
    if not isinstance(obj.get('visual_concept'), str) or not obj.get('visual_concept','').strip():
        errors.append('visual_concept is required')
    for field in ('palette_roles','typography','safe_zones','motion_behavior'):
        if field in obj and not isinstance(obj.get(field), (dict,list)):
            errors.append(f'{field} must be an object or array')
    for field in ('exact_text','forbidden_shortcuts','accessibility','motifs'):
        if field in obj and not isinstance(obj.get(field), list):
            errors.append(f'{field} must be an array')
    refs=obj.get('source_refs',[])
    if not isinstance(refs,list):
        errors.append('source_refs must be an array')
    else:
        for ref in refs:
            if not isinstance(ref,str) or not REF_RX.fullmatch(ref):
                errors.append(f'invalid source ref {ref!r}')
    assets=obj.get('asset_paths',[])
    if not isinstance(assets,list):
        errors.append('asset_paths must be an array')
    else:
        for value in assets:
            if not isinstance(value,str) or not portable(value):
                errors.append(f'asset path must be project-relative: {value!r}')
    return errors


def main() -> int:
    ap=argparse.ArgumentParser(description='Validate the reusable film/campaign visual design system.')
    ap.add_argument('path')
    args=ap.parse_args(); path=Path(args.path).expanduser().resolve()
    try: obj=json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'ERROR invalid JSON: {exc}'); return 2
    errors=validate(obj)
    if errors:
        for e in errors: print('ERROR',e)
        return 2
    print(json.dumps({'status':'pass'},indent=2)); return 0


if __name__=='__main__':
    raise SystemExit(main())
