#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import argparse,json,re
from datetime import datetime,timezone
from pathlib import Path

DEC=re.compile(r'^DEC-\d{3,}$'); STATES={'open','decided','deferred','out-of-scope'}
def now(): return datetime.now(timezone.utc).isoformat()
def root_of(v):
 r=Path(v).expanduser().resolve()
 if not (r/'00_project/state.json').is_file(): raise SystemExit(f'not a Story-Film project: {r}')
 return r
def pp(r): return r/'00_project/decision_map.json',r/'00_project/decision_map.md'
def load(r):
 p,_=pp(r)
 return json.loads(p.read_text()) if p.is_file() else {'schema_version':1,'destination':'','notes':[],'decisions':[],'not_yet_specified':[],'out_of_scope':[]}
def validate(o):
 e=[]
 if o.get('schema_version')!=1:e.append('schema_version must be 1')
 if not isinstance(o.get('decisions'),list):return e+['decisions must be array']
 ids=[]
 for d in o['decisions']:
  did=d.get('decision_id',''); ids.append(did)
  if not DEC.fullmatch(did):e.append(f'{did or "decision"}: decision_id must be DEC-###')
  if d.get('status','open') not in STATES:e.append(f'{did}: invalid status')
  if not isinstance(d.get('prerequisites',[]),list):e.append(f'{did}: prerequisites must be array')
 known=set(ids)
 for d in o['decisions']:
  for x in d.get('prerequisites',[]):
   if x not in known:e.append(f"{d.get('decision_id')}: unknown prerequisite {x}")
 return e
def frontier(o):
 by={d['decision_id']:d for d in o['decisions']}
 return [d for d in o['decisions'] if d.get('status','open')=='open' and all(by.get(x,{}).get('status')=='decided' for x in d.get('prerequisites',[]))]
def md(o):
 ls=['# Production Compass','',f"Destination: {o.get('destination','')}",'','## Decisions so far','']
 dec=[d for d in o['decisions'] if d.get('status')=='decided']
 ls += ([f"- **{d['decision_id']} {d.get('title','')}**: {d.get('resolution','')}" for d in dec] or ['- None'])
 ls += ['','## Ready frontier','']+([f"- **{d['decision_id']} {d.get('title','')}**: {d.get('question','')}" for d in frontier(o)] or ['- None'])
 ls += ['','## Not yet specified','']+([f'- {x}' for x in o.get('not_yet_specified',[])] or ['- None'])
 ls += ['','## Out of scope','']+([f'- {x}' for x in o.get('out_of_scope',[])] or ['- None'])
 return '\n'.join(ls)+'\n'
def save(r,o):
 o['updated_at']=now(); a,b=pp(r); a.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n'); b.write_text(md(o))
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('command',choices=['init','validate','frontier','resolve','defer','render']); ap.add_argument('project_dir'); ap.add_argument('--destination'); ap.add_argument('--decision'); ap.add_argument('--resolution'); args=ap.parse_args(); r=root_of(args.project_dir); o=load(r)
 if args.command=='init':
  if args.destination:o['destination']=args.destination
  save(r,o); print(pp(r)[0]); return 0
 e=validate(o)
 if e:print(json.dumps({'status':'fail','errors':e},indent=2)); return 2
 if args.command=='validate':print(json.dumps({'status':'pass','frontier':[d['decision_id'] for d in frontier(o)]},indent=2)); return 0
 if args.command=='frontier':print(json.dumps({'frontier':frontier(o)},indent=2)); return 0
 if args.command=='render':save(r,o); print(pp(r)[1]); return 0
 d=next((x for x in o['decisions'] if x.get('decision_id')==args.decision),None)
 if not d:raise SystemExit('unknown --decision')
 if args.command=='resolve':
  if not args.resolution:raise SystemExit('--resolution required')
  d['status']='decided';d['resolution']=args.resolution
 elif args.command=='defer':d['status']='deferred';d['resolution']=args.resolution or 'Deferred'
 save(r,o); print(json.dumps({'decision_id':d['decision_id'],'status':d['status'],'frontier':[x['decision_id'] for x in frontier(o)]},indent=2)); return 0
if __name__=='__main__':raise SystemExit(main())
