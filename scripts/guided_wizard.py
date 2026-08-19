#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import argparse,json,os,shlex,stat
from pathlib import Path


def load_spec(path:Path)->dict:
 o=json.loads(path.read_text(encoding='utf-8'))
 if o.get('schema_version')!=1 or not isinstance(o.get('stages'),list) or not o['stages']:raise ValueError('wizard spec requires schema_version=1 and non-empty stages')
 for i,s in enumerate(o['stages'],1):
  if not isinstance(s,dict) or not str(s.get('title','')).strip():raise ValueError(f'stage {i}: title required')
  if not isinstance(s.get('instructions',[]),list):raise ValueError(f'stage {i}: instructions must be array')
 return o

def markdown(o):
 ls=[f"# {o.get('title','Guided Production Wizard')}",'',o.get('purpose',''),'']
 total=len(o['stages'])
 for i,s in enumerate(o['stages'],1):
  ls += [f'## Stage {i} of {total}: {s["title"]}','']+[f'- {x}' for x in s.get('instructions',[])]+['']
  if s.get('verification'):ls += [f"Verification: {s['verification']}",'']
 return '\n'.join(ls).rstrip()+'\n'
def bash(o):
 total=len(o['stages']); lines=['#!/usr/bin/env bash','set -euo pipefail','',f'TOTAL_STAGES={total}','']
 lines += ["pause(){ read -r -p \"Press Enter when this stage is complete... \" _; }",""]
 for i,s in enumerate(o['stages'],1):
  title=shlex.quote(str(s['title']));lines += [f"printf '\\n[%s/%s] %s\\n' {i} \"$TOTAL_STAGES\" {title}"]
  for x in s.get('instructions',[]):lines.append(f"printf '%s\\n' {shlex.quote(str(x))}")
  if s.get('irreversible'):lines += ["read -r -p 'This stage is marked irreversible. Type YES to continue: ' answer","[[ \"$answer\" == YES ]] || { echo 'Stopped.'; exit 1; }"]
  lines += ['pause','']
 lines += ["echo 'Wizard complete. Return to the Story-Film Todo and continue the recorded next action.'",'']
 return '\n'.join(lines)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('spec');ap.add_argument('--out',required=True,help='Output shell wizard path. Matching .md is always created.');a=ap.parse_args();sp=Path(a.spec).expanduser().resolve();o=load_spec(sp);out=Path(a.out).expanduser().resolve();out.parent.mkdir(parents=True,exist_ok=True);out.write_text(bash(o),encoding='utf-8');out.chmod(out.stat().st_mode|stat.S_IXUSR);md=out.with_suffix('.md');md.write_text(markdown(o),encoding='utf-8');print(json.dumps({'script':str(out),'markdown':str(md),'stages':len(o['stages'])},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
