#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Run deferred local-model smoke cases against an OpenAI-compatible endpoint.

This runner is intentionally separate from deterministic tests. It is for the
post-prototype regression phase and can point at llama.cpp, compatible local
servers, or another OpenAI-compatible chat endpoint.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def read_cases(path: Path) -> list[dict[str, Any]]:
    out=[]
    for n,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
        if not line.strip(): continue
        value=json.loads(line)
        value['_line']=n; out.append(value)
    return out


def skill_context(paths: list[str]) -> str:
    chunks=[]
    for rel in paths:
        p=(ROOT/rel).resolve()
        try: p.relative_to(ROOT.resolve())
        except ValueError: raise ValueError(f'skill path escapes repository: {rel}')
        if not p.is_file(): raise ValueError(f'missing skill path: {rel}')
        chunks.append(f'FILE: {rel}\n{p.read_text(encoding="utf-8")}')
    return '\n\n'.join(chunks)


def request_chat(url: str, model: str, messages: list[dict[str,str]], max_tokens: int, timeout: float, api_key: str='') -> str:
    endpoint=url.rstrip('/')
    if not endpoint.endswith('/v1/chat/completions'):
        endpoint += '/v1/chat/completions'
    body=json.dumps({'model':model,'messages':messages,'temperature':0,'max_tokens':max_tokens}).encode('utf-8')
    headers={'Content-Type':'application/json'}
    if api_key: headers['Authorization']=f'Bearer {api_key}'
    req=urllib.request.Request(endpoint,data=body,headers=headers,method='POST')
    with urllib.request.urlopen(req,timeout=timeout) as response:
        value=json.loads(response.read().decode('utf-8'))
    return str(value['choices'][0]['message']['content'])


def judge(case: dict[str,Any], text: str) -> list[str]:
    errors=[]; low=text.lower()
    for token in case.get('required',[]):
        if str(token).lower() not in low: errors.append(f'missing required text: {token}')
    for token in case.get('forbidden',[]):
        if str(token).lower() in low: errors.append(f'contains forbidden text: {token}')
    for pattern in case.get('required_regex',[]):
        if not re.search(pattern,text,re.I|re.M): errors.append(f'missing required regex: {pattern}')
    return errors


def main() -> int:
    ap=argparse.ArgumentParser(description='Run Story-Film local LLM smoke cases.')
    ap.add_argument('--url',default=os.environ.get('STORY_FILM_LLM_URL','http://127.0.0.1:8080'))
    ap.add_argument('--model',default=os.environ.get('STORY_FILM_LLM_MODEL','local-model'))
    ap.add_argument('--api-key',default=os.environ.get('STORY_FILM_LLM_API_KEY',''))
    ap.add_argument('--cases',default=str(ROOT/'tests/local_smoke_cases.jsonl'))
    ap.add_argument('--case')
    ap.add_argument('--timeout',type=float,default=180)
    args=ap.parse_args(); cases=read_cases(Path(args.cases))
    if args.case: cases=[x for x in cases if x.get('case_id')==args.case]
    if not cases: print('ERROR no smoke cases selected'); return 2
    failures=0
    for case in cases:
        try:
            context=skill_context(case.get('skill_paths',[]))
            system='You are testing Story-Film Skills. Follow the supplied skill files. Do not invent tool results.\n\n'+context
            text=request_chat(args.url,args.model,[{'role':'system','content':system},{'role':'user','content':case['user_prompt']}],int(case.get('max_tokens',700)),args.timeout,args.api_key)
            errors=judge(case,text)
        except Exception as exc:
            errors=[f'runner error: {exc}']; text=''
        status='PASS' if not errors else 'FAIL'
        print(f"{status} {case.get('case_id')}: {case.get('title','')}")
        if errors:
            failures+=1
            for error in errors: print('  ',error)
            if text: print('  response:',text[:1200].replace('\n',' '))
    print(f'Smoke cases: {len(cases)-failures}/{len(cases)} passed')
    return 1 if failures else 0

if __name__=='__main__': raise SystemExit(main())
