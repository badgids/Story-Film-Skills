#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import argparse, json
from pathlib import Path
SCOPES={'frame-zero-composition','temporal-continuity','character-identity','location-identity','style-world','prop-or-context'}

def _load(path):
    if not path.exists(): return {'references': []}
    return json.loads(path.read_text(encoding='utf-8'))

def _refs(obj):
    if isinstance(obj,list): return obj
    if isinstance(obj,dict):
        for key in ('references','assets','items'):
            if isinstance(obj.get(key),list): return obj[key]
    return []

def validate_project(root: Path):
    path=root/'03_preproduction/references/reference_manifest.json'; errors=[]
    try: obj=_load(path)
    except Exception as e: return [f'{path.relative_to(root)}: {e}']
    for i,rec in enumerate(_refs(obj),1):
        if not isinstance(rec,dict): continue
        rid=rec.get('ref_id',f'row {i}')
        scopes=rec.get('authority_scopes',[]); deny=rec.get('must_not_control',[])
        if not isinstance(scopes,list) or any(x not in SCOPES for x in scopes): errors.append(f'{rid}: invalid authority_scopes')
        if not isinstance(deny,list) or any(not isinstance(x,str) for x in deny): errors.append(f'{rid}: must_not_control must be a string array')
        atlas=rec.get('atlas')
        if atlas is not None:
            if not isinstance(atlas,dict): errors.append(f'{rid}: atlas must be an object')
            elif atlas.get('layout_is_reference_only') not in (None,True,False): errors.append(f'{rid}: atlas.layout_is_reference_only must be boolean')
    return errors

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('project_dir'); a=ap.parse_args(); errs=validate_project(Path(a.project_dir).resolve())
    for e in errs: print('ERROR',e)
    if not errs: print('OK reference authority')
    return 1 if errs else 0
if __name__=='__main__': raise SystemExit(main())
