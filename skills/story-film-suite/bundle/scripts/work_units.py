#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import argparse, json, os, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUSES={'ready','blocked','active','complete','failed','deferred'}

def now(): return datetime.now(timezone.utc).isoformat()

def root_of(value:str|Path)->Path:
    r=Path(value).expanduser().resolve()
    if not (r/'00_project/state.json').is_file(): raise SystemExit(f'not a Story-Film project: {r}')
    return r

def paths(root:Path): return root/'00_project/work_units.json', root/'00_project/work_units.md'

def atomic(path:Path,text:str):
    path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as f: f.write(text); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        try: os.unlink(tmp)
        except FileNotFoundError: pass

def validate(obj:dict[str,Any])->list[str]:
    errors=[]
    if obj.get('schema_version')!=1: errors.append('schema_version must be 1')
    units=obj.get('units')
    if not isinstance(units,list): return errors+['units must be an array']
    ids=[]
    for i,u in enumerate(units,1):
        if not isinstance(u,dict): errors.append(f'unit {i}: must be object'); continue
        uid=u.get('unit_id','')
        if not isinstance(uid,str) or not uid.startswith('UNIT-') or not uid[5:].isdigit(): errors.append(f'unit {i}: unit_id must be UNIT-###')
        ids.append(uid)
        if not isinstance(u.get('title'),str) or not u.get('title','').strip(): errors.append(f'{uid or i}: title required')
        if u.get('status','ready') not in STATUSES: errors.append(f'{uid or i}: invalid status')
        for key in ('blocked_by','source_ids','acceptance_criteria'):
            if not isinstance(u.get(key,[]),list): errors.append(f'{uid or i}: {key} must be array')
    if len(ids)!=len(set(ids)): errors.append('duplicate unit_id')
    known=set(ids)
    graph={u.get('unit_id'):set(u.get('blocked_by',[])) for u in units if isinstance(u,dict)}
    for uid,deps in graph.items():
        for d in deps:
            if d not in known: errors.append(f'{uid}: unknown blocker {d}')
            if d==uid: errors.append(f'{uid}: cannot block itself')
    visiting=set(); visited=set()
    def walk(uid):
        if uid in visited:return
        if uid in visiting: errors.append(f'cycle detected at {uid}'); return
        visiting.add(uid)
        for d in graph.get(uid,set()):
            if d in graph: walk(d)
        visiting.remove(uid); visited.add(uid)
    for uid in graph: walk(uid)
    return errors

def render(obj:dict[str,Any])->str:
    lines=['# Production Work Units','',f"Updated: {obj.get('updated_at','')}",'']
    status={u.get('unit_id'):u.get('status') for u in obj.get('units',[]) if isinstance(u,dict)}
    for u in obj.get('units',[]):
        uid=u.get('unit_id','UNIT-???'); lines += [f"## {uid}: {u.get('title','Untitled')}",'',f"Status: {u.get('status','ready')}",'']
        if u.get('delivers'): lines += ['### Delivers','',str(u['delivers']),'']
        deps=u.get('blocked_by',[]); lines += ['### Blocked by','']
        lines += ([f"- {d} ({status.get(d,'unknown')})" for d in deps] if deps else ['- None']) + ['']
        lines += ['### Acceptance criteria',''] + ([f'- [ ] {x}' for x in u.get('acceptance_criteria',[])] or ['- None declared']) + ['']
        if u.get('source_ids'): lines += ['### Source IDs','']+[f'- {x}' for x in u['source_ids']]+['']
        if u.get('validation_commands'): lines += ['### Validation','']+[f'- `{x}`' if isinstance(x,str) else f'- {x}' for x in u['validation_commands']]+['']
        if u.get('notes'): lines += ['### Notes','',str(u['notes']),'']
    return '\n'.join(lines).rstrip()+'\n'

def save(root:Path,obj:dict[str,Any]):
    obj['schema_version']=1; obj['updated_at']=now(); jp,mp=paths(root); atomic(jp,json.dumps(obj,indent=2,ensure_ascii=False)+'\n'); atomic(mp,render(obj))

def load(root:Path)->dict[str,Any]:
    jp,_=paths(root)
    if not jp.is_file(): return {'schema_version':1,'units':[],'updated_at':now()}
    return json.loads(jp.read_text(encoding='utf-8'))

def frontier(obj):
    units=obj.get('units',[]); by={u['unit_id']:u for u in units if isinstance(u,dict) and 'unit_id'in u}
    out=[]
    for u in units:
        if not isinstance(u,dict) or u.get('status') in {'complete','deferred','active'}: continue
        deps=u.get('blocked_by',[])
        if all(by.get(d,{}).get('status')=='complete' for d in deps): out.append(u)
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('command',choices=['init','validate','frontier','set-status','render']); ap.add_argument('project_dir'); ap.add_argument('--unit'); ap.add_argument('--status',choices=sorted(STATUSES)); ap.add_argument('--note'); args=ap.parse_args(); root=root_of(args.project_dir); obj=load(root)
    if args.command=='init': save(root,obj); print(paths(root)[0]); return 0
    errs=validate(obj)
    if errs:
        print(json.dumps({'status':'fail','errors':errs},indent=2)); return 2
    if args.command=='validate': print(json.dumps({'status':'pass','units':len(obj.get('units',[])),'frontier':[u['unit_id'] for u in frontier(obj)]},indent=2)); return 0
    if args.command=='frontier': print(json.dumps({'frontier':frontier(obj)},indent=2)); return 0
    if args.command=='render': save(root,obj); print(paths(root)[1]); return 0
    if not args.unit or not args.status: raise SystemExit('set-status requires --unit and --status')
    unit=next((u for u in obj['units'] if u.get('unit_id')==args.unit),None)
    if not unit: raise SystemExit(f'unknown unit {args.unit}')
    if args.status in {'active','complete'}:
        by={u['unit_id']:u for u in obj['units']}
        bad=[d for d in unit.get('blocked_by',[]) if by.get(d,{}).get('status')!='complete']
        if bad: raise SystemExit(f'{args.unit} is blocked by incomplete units: {", ".join(bad)}')
    unit['status']=args.status
    if args.note: unit['notes']=(str(unit.get('notes','')).rstrip()+'\n'+args.note).strip()
    save(root,obj); print(json.dumps({'unit_id':args.unit,'status':args.status,'frontier':[u['unit_id'] for u in frontier(obj)]},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
