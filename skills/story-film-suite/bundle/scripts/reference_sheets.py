#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import argparse,json
from pathlib import Path
TYPES={'character-reference','location-reference','prop-reference'}
def validate_project(root):
 p=root/'03_preproduction/references/reference_sheet_plans.json'; errors=[]
 if not p.exists(): return errors
 try:o=json.loads(p.read_text(encoding='utf-8'))
 except Exception as e:return [f'{p.relative_to(root)}: {e}']
 plans=o.get('plans',[]) if isinstance(o,dict) else []
 for n,r in enumerate(plans,1):
  if r.get('sheet_type') not in TYPES: errors.append(f'plan {n}: invalid sheet_type')
  if not isinstance(r.get('subject_id'),str): errors.append(f'plan {n}: subject_id required')
  if not isinstance(r.get('required_views',[]),list): errors.append(f'plan {n}: required_views must be array')
  if r.get('functional_views') is not None and not isinstance(r.get('functional_views'),list): errors.append(f'plan {n}: functional_views must be array')
 return errors
def main():
 ap=argparse.ArgumentParser();ap.add_argument('project_dir');a=ap.parse_args();e=validate_project(Path(a.project_dir).resolve());[print('ERROR',x) for x in e];print('OK reference sheet plans' if not e else f'FAILED {len(e)}');return 1 if e else 0
if __name__=='__main__':raise SystemExit(main())
