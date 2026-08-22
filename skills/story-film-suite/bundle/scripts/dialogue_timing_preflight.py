#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import argparse,json,wave
from pathlib import Path
def wav_duration(p):
 with wave.open(str(p),'rb') as w:return w.getnframes()/w.getframerate()
def classify(start,duration,clip,rebalance=0):
 end=start+duration
 if end<=clip+1e-6:return 'fits'
 if end<=clip+max(0,rebalance)+1e-6:return 'needs-timing-rebalance'
 return 'impossible'
def validate_project(root):
 p=root/'04_generation/dialogue_timing_plan.json';errors=[]
 if not p.exists():return errors
 try:o=json.loads(p.read_text(encoding='utf-8'))
 except Exception as e:return [f'{p.relative_to(root)}: {e}']
 for n,r in enumerate(o.get('clips',[]),1):
  clip=float(r.get('duration_seconds',0)); reb=float(r.get('rebalance_seconds',0))
  for line in r.get('lines',[]):
   q=(root/line.get('path','')).resolve();
   if root.resolve() not in q.parents or not q.is_file():errors.append(f'clip {n} {line.get("line_id")}: audio missing/unsafe');continue
   status=classify(float(line.get('start_seconds',0)),wav_duration(q),clip,reb)
   if status=='impossible':errors.append(f'clip {n} {line.get("line_id")}: dialogue does not fit')
 return errors
def main():
 ap=argparse.ArgumentParser();ap.add_argument('project_dir');a=ap.parse_args();e=validate_project(Path(a.project_dir).resolve());[print('ERROR',x) for x in e];print('OK dialogue timing preflight' if not e else f'FAILED {len(e)}');return 1 if e else 0
if __name__=='__main__':raise SystemExit(main())
