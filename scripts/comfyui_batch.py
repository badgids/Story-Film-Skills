#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Compile, validate, and execute deterministic ComfyUI offline batches.

No LLM is called by this module. All creative values must already be present in
workflow JSON or explicit batch patches before execution starts.
"""
from __future__ import annotations
import argparse, copy, json, re, time
from pathlib import Path
from typing import Any, Callable

from comfyui_control import Client, ComfyError, resolve_url
from comfyui_workflow import load_json, detect_format
from media_runtime import project_root, project_path, portable_rel

BATCH_RX=re.compile(r'^BATCH-\d{3,}$'); JOB_RX=re.compile(r'^JOB-\d{3,}$'); UP_RX=re.compile(r'^UP-\d{3,}$')
STATUS_VALUES={'prepared','running','complete','failed'}
PLACEHOLDER_RX=re.compile(r'\{\{[^}]+\}\}|\b(?:TODO|TBD|NEEDS[-_ ]?LLM)\b',re.I)

def read(path:Path):return json.loads(path.read_text(encoding='utf-8'))
def write(path:Path,obj:Any):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def manifest_path(root:Path,rel='04_generation/comfyui/offline_batch.json')->Path:return project_path(root,rel)

def load_manifest(root:Path,rel='04_generation/comfyui/offline_batch.json')->dict[str,Any]:
 p=manifest_path(root,rel)
 if not p.is_file():raise ValueError(f'missing offline batch: {rel}')
 o=read(p)
 if not isinstance(o,dict):raise ValueError('offline batch must be an object')
 return o

def validate(root:Path,obj:dict[str,Any],live:Client|None=None)->list[str]:
 errors=[]
 if obj.get('schema_version')!=1:errors.append('schema_version must be 1')
 bid=obj.get('batch_id','')
 if not BATCH_RX.fullmatch(str(bid)):errors.append('batch_id must be BATCH-###')
 if obj.get('status','prepared') not in STATUS_VALUES:errors.append('invalid batch status')
 if obj.get('sequential',True) is not True:errors.append('offline resource-safe batches currently require sequential=true')
 uploads=obj.get('uploads',[]); jobs=obj.get('jobs',[])
 if not isinstance(uploads,list):return errors+['uploads must be array']
 if not isinstance(jobs,list) or not jobs:return errors+['jobs must be a non-empty array']
 upload_ids=[]
 for i,u in enumerate(uploads,1):
  if not isinstance(u,dict):errors.append(f'upload {i}: must be object');continue
  uid=str(u.get('upload_id',''));upload_ids.append(uid)
  if not UP_RX.fullmatch(uid):errors.append(f'upload {i}: upload_id must be UP-###')
  rel=u.get('path','')
  if not isinstance(rel,str) or not portable_rel(rel):errors.append(f'{uid or i}: path must be project-relative')
  else:
   try:project_path(root,rel,must_exist=True)
   except Exception as exc:errors.append(f'{uid or i}: {exc}')
 if len(upload_ids)!=len(set(upload_ids)):errors.append('duplicate upload_id')
 known_upload=set(upload_ids); job_ids=[]
 for i,j in enumerate(jobs,1):
  if not isinstance(j,dict):errors.append(f'job {i}: must be object');continue
  jid=str(j.get('job_id',''));job_ids.append(jid)
  if not JOB_RX.fullmatch(jid):errors.append(f'job {i}: job_id must be JOB-###')
  rel=j.get('workflow','')
  if not isinstance(rel,str) or not portable_rel(rel):errors.append(f'{jid or i}: workflow must be project-relative');continue
  try:wp=project_path(root,rel,must_exist=True);wf=load_json(wp)
  except Exception as exc:errors.append(f'{jid or i}: workflow error: {exc}');continue
  if detect_format(wf)!='api':errors.append(f'{jid}: workflow must be API-format JSON')
  raw=wp.read_text(encoding='utf-8',errors='ignore')
  if PLACEHOLDER_RX.search(raw):errors.append(f'{jid}: workflow contains unresolved placeholder/TODO text')
  for pidx,p in enumerate(j.get('patches',[]),1):
   if not isinstance(p,dict):errors.append(f'{jid} patch {pidx}: must be object');continue
   if not str(p.get('node','')).strip() or not str(p.get('input','')).strip():errors.append(f'{jid} patch {pidx}: node and input required')
   has_upload='upload_id' in p;has_value='value' in p
   if has_upload==has_value:errors.append(f'{jid} patch {pidx}: specify exactly one of upload_id or value')
   if has_upload and p.get('upload_id') not in known_upload:errors.append(f"{jid} patch {pidx}: unknown upload_id {p.get('upload_id')}")
  if not isinstance(j.get('blocked_by',[]),list):errors.append(f'{jid}: blocked_by must be array')
  out=j.get('output_dir','')
  if not isinstance(out,str) or not portable_rel(out):errors.append(f'{jid}: output_dir must be project-relative')
  if int(j.get('timeout_s',1800))<=0:errors.append(f'{jid}: timeout_s must be positive')
  retries=int(j.get('max_transient_retries',0))
  if retries<0 or retries>5:errors.append(f'{jid}: max_transient_retries must be 0..5')
  if live is not None:
   # Exact live validation of upload-dependent inputs happens in preflight(),
   # after required files have been staged and their server-returned names are patched.
   upload_dependent=any(isinstance(p,dict) and 'upload_id' in p for p in j.get('patches',[]))
   if not upload_dependent:
    try:
     lr=live.validate_workflow(wf)
     for e in lr.get('errors',[]):errors.append(f'{jid} live: {e}')
    except Exception as exc:errors.append(f'{jid} live validation failed: {exc}')
 if len(job_ids)!=len(set(job_ids)):errors.append('duplicate job_id')
 known=set(job_ids); graph={str(j.get('job_id')):list(j.get('blocked_by',[])) for j in jobs if isinstance(j,dict)}
 for jid,deps in graph.items():
  for d in deps:
   if d not in known:errors.append(f'{jid}: unknown blocker {d}')
   if d==jid:errors.append(f'{jid}: cannot block itself')
 visiting=set();visited=set()
 def walk(jid):
  if jid in visited:return
  if jid in visiting:errors.append(f'job dependency cycle at {jid}');return
  visiting.add(jid)
  for d in graph.get(jid,[]):
   if d in graph:walk(d)
  visiting.remove(jid);visited.add(jid)
 for jid in graph:walk(jid)
 return errors

def upload_value(rec:dict[str,Any])->str:
 name=str(rec.get('name',''));sub=str(rec.get('subfolder','')).strip('/')
 return f'{sub}/{name}' if sub else name

def patch_workflow(wf:dict[str,Any],patches:list[dict[str,Any]],uploaded:dict[str,dict[str,Any]])->dict[str,Any]:
 out=copy.deepcopy(wf)
 for p in patches:
  node=str(p['node']);key=str(p['input'])
  if node not in out or not isinstance(out[node],dict) or not isinstance(out[node].get('inputs'),dict):raise ValueError(f'patch node {node} not found or has no inputs')
  if key not in out[node]['inputs']:raise ValueError(f'patch input {node}.{key} does not exist')
  out[node]['inputs'][key]=upload_value(uploaded[p['upload_id']]) if 'upload_id' in p else p['value']
 return out

def transient(exc:Exception)->bool:
 return isinstance(exc,(TimeoutError,ComfyError)) and (not isinstance(exc,ComfyError) or exc.status is None or exc.status==429 or (exc.status and 500<=exc.status<600))

def preflight(root:Path,obj:dict[str,Any],client:Client,stage_uploads:bool=True,on_event:Callable[[dict[str,Any]],None]|None=None)->dict[str,Any]:
 """Prepare an offline batch while the LLM is still available.

 Required inputs are uploaded before unload so every upload-dependent workflow can
 be patched with the exact ComfyUI server identity and live-validated in its final
 executable form. The returned object is safe to persist as the armed manifest.
 """
 def event(**kw):
  if on_event:on_event(kw)
 errors=validate(root,obj,live=None)
 if errors:raise ValueError('offline batch structural preflight failed: '+'; '.join(errors))
 out=copy.deepcopy(obj);uploaded=copy.deepcopy(out.get('staged_uploads') or {})
 if stage_uploads:
  for u in out.get('uploads',[]):
   uid=u['upload_id']
   if uid in uploaded and isinstance(uploaded[uid],dict) and uploaded[uid].get('name'):
    continue
   path=project_path(root,u['path'],must_exist=True);event(kind='upload-start',upload_id=uid,path=u['path'])
   rec=client.upload_image(path,subfolder=str(u.get('subfolder','')),overwrite=bool(u.get('overwrite',False)),upload_type=str(u.get('type','input')))
   uploaded[uid]=rec;event(kind='upload-complete',upload_id=uid,server_name=upload_value(rec))
 out['staged_uploads']=uploaded
 live_errors=[]
 for j in out['jobs']:
  try:
   wf=patch_workflow(load_json(project_path(root,j['workflow'],must_exist=True)),j.get('patches',[]),uploaded)
   lr=client.validate_workflow(wf)
   for e in lr.get('errors',[]):live_errors.append(f"{j['job_id']} live: {e}")
  except Exception as exc:live_errors.append(f"{j['job_id']} final live validation failed: {exc}")
 if live_errors:raise ValueError('offline batch final live preflight failed: '+'; '.join(live_errors))
 out['preflight']={'status':'pass','staged_upload_count':len(uploaded),'validated_job_count':len(out['jobs'])}
 return out

def execute(root:Path,obj:dict[str,Any],client:Client,on_event:Callable[[dict[str,Any]],None]|None=None)->dict[str,Any]:
 def event(**kw):
  if on_event:on_event(kw)
 def persist(status:str,failed_job_id:str='',error:str=''):
  result={'schema_version':1,'batch_id':obj['batch_id'],'status':status,'jobs':results,'uploads':uploaded,'failed_job_id':failed_job_id,'error':error}
  write(root/'04_generation/comfyui/offline_batch_result.json',result)
  return result
 errors=validate(root,obj,live=None)
 if errors:raise ValueError('offline batch preflight failed: '+'; '.join(errors))
 uploaded=copy.deepcopy(obj.get('staged_uploads') or {})
 for u in obj.get('uploads',[]):
  if u['upload_id'] in uploaded and isinstance(uploaded[u['upload_id']],dict) and uploaded[u['upload_id']].get('name'):
   continue
  path=project_path(root,u['path'],must_exist=True)
  event(kind='upload-start',upload_id=u['upload_id'],path=u['path'])
  rec=client.upload_image(path,subfolder=str(u.get('subfolder','')),overwrite=bool(u.get('overwrite',False)),upload_type=str(u.get('type','input')))
  uploaded[u['upload_id']]=rec;event(kind='upload-complete',upload_id=u['upload_id'],server_name=upload_value(rec))
 results=[]; done=set(); jobs=obj['jobs']; total=len(jobs);persist('running')
 while len(done)<total:
  ready=[j for j in jobs if j['job_id'] not in done and all(d in done for d in j.get('blocked_by',[]))]
  if not ready:
   persist('failed',error='no executable job frontier; dependency graph is stuck')
   raise ValueError('no executable job frontier; dependency graph is stuck')
  j=ready[0];jid=j['job_id'];attempt=0;maxr=int(j.get('max_transient_retries',0))
  while True:
   attempt+=1
   try:
    event(kind='job-start',job_id=jid,index=len(done)+1,total=total,attempt=attempt)
    wf=patch_workflow(load_json(project_path(root,j['workflow'],must_exist=True)),j.get('patches',[]),uploaded)
    live=client.validate_workflow(wf)
    if live.get('errors'):raise ValueError(f'{jid} patched workflow invalid: '+ '; '.join(live['errors']))
    submit=client.submit(wf);pid=str(submit.get('prompt_id',''))
    if not pid:raise ValueError(f'{jid}: ComfyUI did not return prompt_id')
    rec=client.wait(pid,timeout=float(j.get('timeout_s',1800)),poll_interval=float(j.get('poll_interval_s',2)))
    status=rec.get('status',{}) if isinstance(rec,dict) else {}
    if isinstance(status,dict) and status.get('status_str') in {'error','failed','cancelled','canceled'}:raise ValueError(f'{jid}: ComfyUI completed with {status.get("status_str")}')
    outdir=project_path(root,j['output_dir']);download=client.download_outputs(pid,outdir)
    result={'job_id':jid,'source_ids':j.get('source_ids',[]),'prompt_id':pid,'attempts':attempt,'status':'complete','outputs':download.get('written',[]),'text':download.get('text',{})}
    results.append(result);done.add(jid);persist('running');event(kind='job-complete',job_id=jid,index=len(done),total=total,prompt_id=pid,outputs=result['outputs']);break
   except Exception as exc:
    if attempt<=maxr and transient(exc):event(kind='job-retry',job_id=jid,attempt=attempt,error=str(exc));time.sleep(min(2**attempt,10));continue
    results.append({'job_id':jid,'source_ids':j.get('source_ids',[]),'attempts':attempt,'status':'failed','outputs':[],'text':{},'error':str(exc)})
    persist('failed',failed_job_id=jid,error=str(exc));event(kind='job-failed',job_id=jid,index=len(done)+1,total=total,error=str(exc));raise
 return persist('complete')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('command',choices=['validate','preflight','run']);ap.add_argument('project_dir');ap.add_argument('--manifest',default='04_generation/comfyui/offline_batch.json');ap.add_argument('--url');ap.add_argument('--live',action='store_true');ap.add_argument('--write',action='store_true');a=ap.parse_args();root=project_root(a.project_dir);obj=load_manifest(root,a.manifest);client=Client(resolve_url(a.url)) if a.live or a.command=='run' else None;errs=validate(root,obj,live=client)
 if errs:print(json.dumps({'status':'fail','errors':errs},indent=2));return 2
 if a.command=='validate':print(json.dumps({'status':'pass','batch_id':obj['batch_id'],'jobs':len(obj['jobs']),'live':bool(client)},indent=2));return 0
 if a.command=='preflight':
  prepared=preflight(root,obj,client or Client(resolve_url(a.url)),stage_uploads=True, on_event=lambda e:print(json.dumps(e,ensure_ascii=False),flush=True))
  if a.write:write(manifest_path(root,a.manifest),prepared)
  print(json.dumps({'status':'pass','batch_id':prepared['batch_id'],'jobs':len(prepared['jobs']),'staged_uploads':len(prepared.get('staged_uploads',{})),'written':bool(a.write)},indent=2));return 0
 result=execute(root,obj,client or Client(resolve_url(a.url)),lambda e:print(json.dumps(e,ensure_ascii=False),flush=True));print(json.dumps(result,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
