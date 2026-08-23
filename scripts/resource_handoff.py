#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Model-free resource handoff between a local Pi LLM and ComfyUI."""
from __future__ import annotations
import argparse,json,os,subprocess,sys,tempfile,time,urllib.request
from datetime import datetime,timezone
from pathlib import Path
from typing import Any

from comfyui_control import Client, resolve_url
from comfyui_batch import load_manifest, validate as validate_batch, preflight as preflight_batch, execute as execute_batch, manifest_path as batch_manifest_path, write as write_batch
from media_runtime import project_root, project_path
from llm_runtime import classify_endpoint
import llm_model_lifecycle

NATIVE_LLM_ADAPTERS={'auto','llama-server','ollama'}
PHASES={'idle','armed','waiting-for-agent-end','unloading-llm','running-comfyui','unloading-comfyui','reloading-llm','complete','failed','cancelled'}
def now():return datetime.now(timezone.utc).isoformat()
def paths(root:Path):
 p=root/'00_project'
 return {'policy':p/'resource_policy.json','status':p/'resource_handoff.json','events':p/'resource_events.jsonl','release':p/'resource_handoff.release','resume':p/'RESOURCE_RESUME.md','log':p/'resource_handoff.log','llm_snapshot':p/'llm_model_snapshot.json'}
def atomic(path:Path,text:str):
 path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
 try:
  with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as f:f.write(text);f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  try:os.unlink(tmp)
  except FileNotFoundError:pass
def write_json(path:Path,obj:Any):atomic(path,json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def event(root:Path,kind:str,**data):
 row={'timestamp':now(),'kind':kind,**data};p=paths(root)['events'];p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
def load_policy(root:Path)->dict[str,Any]:
 p=paths(root)['policy']
 if not p.is_file():raise ValueError('missing 00_project/resource_policy.json')
 o=json.loads(p.read_text(encoding='utf-8'))
 if o.get('schema_version')!=1:raise ValueError('resource policy schema_version must be 1')
 return o
def load_status(root:Path)->dict[str,Any]:
 p=paths(root)['status']
 if not p.is_file():return {'schema_version':1,'phase':'idle','message':'No resource handoff is active.'}
 return json.loads(p.read_text(encoding='utf-8'))
def update(root:Path,**fields):
 o=load_status(root);o.update(fields);o['schema_version']=1;o['updated_at']=now();write_json(paths(root)['status'],o);event(root,'state',phase=o.get('phase'),message=o.get('message'),current_job_id=o.get('current_job_id',''),job_index=o.get('job_index',0),job_total=o.get('job_total',0));return o
def run_argv(argv:list[str],timeout:float,label:str):
 if not isinstance(argv,list) or not argv or not all(isinstance(x,str) and x for x in argv):raise ValueError(f'{label} command must be a non-empty argv array')
 p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError(f'{label} command failed ({p.returncode}): {(p.stdout or "").strip()[-2000:]}')
 return (p.stdout or '').strip()
def http_ok(url:str,timeout:float=5):
 try:
  with urllib.request.urlopen(url,timeout=timeout) as r:return 200<=r.status<500
 except Exception:return False
def wait_health(llm:dict[str,Any],timeout:float):
 end=time.time()+timeout;cmd=llm.get('health_command') or [];url=str(llm.get('health_url') or '')
 if not cmd and not url:return
 while time.time()<end:
  if cmd:
   try:
    p=subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=min(10,max(1,end-time.time())))
    if p.returncode==0:return
   except Exception:pass
  if url and http_ok(url):return
  time.sleep(1)
 raise TimeoutError('local LLM health check did not become ready')
def validate_llm_policy(policy):
 llm=policy.get('local_llm',{});adapter=llm.get('adapter','auto');location=llm.get('runtime_location','unknown');endpoint=str(llm.get('endpoint') or llm.get('health_url') or '');evidence=llm.get('location_evidence') or []
 if location not in {'unknown','local','external'}:raise ValueError('local_llm.runtime_location must be unknown, local, or external')
 classified=classify_endpoint(endpoint).get('location') if endpoint else 'unknown'
 if classified=='local':
  if location=='external' or adapter=='external':raise ValueError('local_llm is configured as external, but its endpoint is local to this machine')
  location='local'
 if adapter=='external':
  if location!='external' or not isinstance(evidence,list) or not any(isinstance(x,str) and x.strip() for x in evidence):raise ValueError('external LLM mode requires explicit external runtime_location and location_evidence; never infer external from API style or missing environment variables')
 if adapter in NATIVE_LLM_ADAPTERS:
  if not endpoint:raise ValueError('native local LLM lifecycle requires local_llm.endpoint')
  if classified!='local':raise ValueError('native local LLM lifecycle endpoint must be proven local')
  if location=='external':raise ValueError('native local LLM lifecycle adapter conflicts with external runtime_location')
 if adapter=='command' and location=='external':raise ValueError('command lifecycle adapter conflicts with external runtime_location')
 if adapter not in NATIVE_LLM_ADAPTERS|{'command','external'}:raise ValueError('local_llm.adapter must be auto, llama-server, ollama, command, or external')
 return location
def unload_llm(root,policy):
 validate_llm_policy(policy);llm=policy.get('local_llm',{});adapter=llm.get('adapter','auto')
 if adapter=='external':return 'verified external model: no local unload needed'
 if adapter in NATIVE_LLM_ADAPTERS:
  state=llm_model_lifecycle.snapshot_and_unload(adapter,str(llm.get('endpoint') or ''),state_path=paths(root)['llm_snapshot'],timeout=float(llm.get('unload_timeout_s',120)))
  return json.dumps({'runtime':state.get('runtime'),'models':state.get('models',[])})
 return run_argv(llm.get('unload_command',[]),float(llm.get('unload_timeout_s',120)),'LLM unload')
def reload_llm(root,policy):
 validate_llm_policy(policy);llm=policy.get('local_llm',{});adapter=llm.get('adapter','auto')
 if adapter=='external':return 'verified external model: no local reload needed'
 if adapter in NATIVE_LLM_ADAPTERS:
  result=llm_model_lifecycle.restore(paths(root)['llm_snapshot'],keep_alive=str(llm.get('restore_keep_alive') or '5m'),unload_untracked=True,timeout=float(llm.get('reload_timeout_s',300)));wait_health(llm,float(llm.get('health_timeout_s',300)));return json.dumps(result)
 text=run_argv(llm.get('reload_command',[]),float(llm.get('reload_timeout_s',300)),'LLM reload');wait_health(llm,float(llm.get('health_timeout_s',300)));return text
def wait_queue_empty(client:Client,timeout=120):
 end=time.time()+timeout
 while time.time()<end:
  q=client.queue();running=q.get('queue_running',[]) if isinstance(q,dict) else [];pending=q.get('queue_pending',[]) if isinstance(q,dict) else []
  if not running and not pending:return True
  time.sleep(1)
 return False
def resume_md(status:dict[str,Any])->str:
 ls=['# Resource Handoff Resume','',f"Phase: {status.get('phase')}",f"Message: {status.get('message','')}",f"Batch: {status.get('batch_id','')}",'']
 if status.get('error'):ls += ['## Error','',str(status['error']),'']
 ls += ['## Generated outputs','']
 outs=status.get('outputs',[]);ls += ([f'- `{x}`' for x in outs] if outs else ['- None recorded'])
 ls += ['','## Next action','',str(status.get('next_action') or 'Review the batch result and continue the active Story-Film Todo target.'),'']
 return '\n'.join(ls)
def daemon(root:Path)->int:
 ps=paths(root);policy=load_policy(root);st=load_status(root);release_timeout=float(policy.get('exclusive_generation',{}).get('release_timeout_s',900));end=time.time()+release_timeout
 while not ps['release'].exists():
  if time.time()>end:update(root,phase='failed',message='Timed out waiting for Pi agent turn to finish.',error='release signal timeout',next_action='Reload/continue the LLM and re-arm the resource handoff.');return 2
  time.sleep(.25)
 try:ps['release'].unlink()
 except FileNotFoundError:pass
 llm_unloaded=False;client=None;outputs=[];failure=None
 try:
  update(root,phase='unloading-llm',message='Current agent turn is complete. Unloading the configured local LLM before ComfyUI generation.',llm_state='unloading')
  unload_llm(root,policy);llm_unloaded=True;update(root,llm_state='unloaded',message='Local LLM unloaded. Starting deterministic ComfyUI batch.')
  comfy=policy.get('comfyui',{});client=Client(resolve_url(comfy.get('url') or None),timeout=float(comfy.get('request_timeout_s',30)))
  batch=load_manifest(root,str(st.get('batch_manifest') or '04_generation/comfyui/offline_batch.json'))
  total=len(batch.get('jobs',[]));update(root,phase='running-comfyui',message=f'ComfyUI batch running: 0 of {total} jobs complete.',comfyui_state='running',job_total=total,job_index=0)
  def cb(ev):
   kind=ev.get('kind','');fields={}
   if 'job_id' in ev:fields['current_job_id']=ev['job_id']
   if 'index' in ev:fields['job_index']=ev['index']-1 if kind=='job-start' else ev['index']
   if 'total' in ev:fields['job_total']=ev['total']
   if kind=='job-start':fields['message']=f"ComfyUI job {ev.get('index')} of {ev.get('total')} running: {ev.get('job_id')}"
   elif kind=='job-complete':fields['message']=f"ComfyUI job {ev.get('index')} of {ev.get('total')} complete: {ev.get('job_id')}"
   elif kind=='job-retry':fields['message']=f"Transient error in {ev.get('job_id')}; retrying identical prepared job."
   elif kind=='job-failed':fields['message']=f"Prepared ComfyUI job failed: {ev.get('job_id')}"
   if fields:update(root,**fields)
   event(root,'comfyui-'+kind,**{k:v for k,v in ev.items() if k!='kind'})
  result=execute_batch(root,batch,client,cb)
  for j in result.get('jobs',[]):
   for rec in j.get('outputs',[]):
    p=rec.get('path')
    if p:
     pp=Path(p)
     try:outputs.append(pp.resolve().relative_to(root).as_posix())
     except Exception:outputs.append(str(p))
  update(root,message='All prepared ComfyUI jobs completed. Releasing ComfyUI models and caches.',job_index=total,outputs=outputs)
 except Exception as exc:
  failure=str(exc);update(root,message='ComfyUI batch stopped. Restoring resources before returning control.',error=failure)
 finally:
  try:
   update(root,phase='unloading-comfyui',message='Requesting ComfyUI model unload and cache release.',comfyui_state='unloading')
   if client is None:
    comfy=policy.get('comfyui',{});client=Client(resolve_url(comfy.get('url') or None),timeout=float(comfy.get('request_timeout_s',30)))
   wait_queue_empty(client,float(policy.get('comfyui',{}).get('queue_drain_timeout_s',120)))
   client.free(unload_models=True,free_memory=True);time.sleep(float(policy.get('comfyui',{}).get('free_settle_s',2)));update(root,comfyui_state='unloaded')
  except Exception as exc:
   failure=failure or f'ComfyUI cleanup failed: {exc}';update(root,error=failure,comfyui_state='cleanup-failed')
  try:
   if llm_unloaded:
    update(root,phase='reloading-llm',message='ComfyUI is released. Reloading the configured local LLM.',llm_state='reloading');reload_llm(root,policy);update(root,llm_state='ready')
  except Exception as exc:
   failure=failure or f'LLM reload failed: {exc}';update(root,error=failure,llm_state='reload-failed')
 final=update(root,phase='failed' if failure else 'complete',message=('Resource handoff failed, but cleanup/restore was attempted.' if failure else 'ComfyUI batch complete. ComfyUI models unloaded and local LLM restored.'),error=failure or '',outputs=outputs,next_action=('Review RESOURCE_RESUME.md and repair the failed prepared job.' if failure else 'Review RESOURCE_RESUME.md and continue the active Story-Film Todo target.'))
 atomic(ps['resume'],resume_md(final));return 2 if failure else 0
def arm(root:Path,manifest_rel:str,url:str|None,detach:bool)->dict[str,Any]:
 policy=load_policy(root);batch=load_manifest(root,manifest_rel);client=Client(resolve_url(url or policy.get('comfyui',{}).get('url') or None));errs=validate_batch(root,batch,live=None)
 if errs:raise ValueError('batch is not safe to hand off: '+'; '.join(errs))
 # Stage every declared input and validate every final patched workflow while the
 # LLM is still loaded. The daemon must not need a semantic repair later.
 batch=preflight_batch(root,batch,client,stage_uploads=True)
 write_batch(batch_manifest_path(root,manifest_rel),batch)
 adapter=policy.get('local_llm',{}).get('adapter','auto')
 validate_llm_policy(policy)
 if adapter not in NATIVE_LLM_ADAPTERS|{'command','external'}:raise ValueError('resource_policy local_llm.adapter is unsupported')
 ps=paths(root)
 try:ps['release'].unlink()
 except FileNotFoundError:pass
 state={'schema_version':1,'phase':'waiting-for-agent-end','message':'Offline ComfyUI batch is fully prepared. Waiting for the current Pi agent turn to end before unloading the local LLM.','batch_id':batch['batch_id'],'batch_manifest':manifest_rel,'job_total':len(batch['jobs']),'job_index':0,'current_job_id':'','llm_state':'ready','comfyui_state':'ready','outputs':[],'error':'','started_at':now(),'updated_at':now()};write_json(ps['status'],state);event(root,'armed',batch_id=batch['batch_id'],jobs=len(batch['jobs']))
 if detach:
  log=ps['log'].open('a',encoding='utf-8');p=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'run-daemon',str(root)],cwd=root,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);log.close();state['runner_pid']=p.pid;write_json(ps['status'],state)
 return state
def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True)
 p=sub.add_parser('arm');p.add_argument('project_dir');p.add_argument('--manifest',default='04_generation/comfyui/offline_batch.json');p.add_argument('--url');p.add_argument('--foreground',action='store_true')
 p=sub.add_parser('release');p.add_argument('project_dir')
 p=sub.add_parser('status');p.add_argument('project_dir')
 p=sub.add_parser('run-daemon');p.add_argument('project_dir')
 p=sub.add_parser('reset');p.add_argument('project_dir')
 a=ap.parse_args();root=project_root(a.project_dir);ps=paths(root)
 if a.cmd=='arm':print(json.dumps(arm(root,a.manifest,a.url,not a.foreground),indent=2));return 0
 if a.cmd=='release':atomic(ps['release'],now()+'\n');event(root,'release-signal');print(ps['release']);return 0
 if a.cmd=='status':print(json.dumps(load_status(root),indent=2));return 0
 if a.cmd=='run-daemon':return daemon(root)
 if a.cmd=='reset':
  for k in ('release','resume'):
   try:ps[k].unlink()
   except FileNotFoundError:pass
  write_json(ps['status'],{'schema_version':1,'phase':'idle','message':'No resource handoff is active.','updated_at':now()});return 0
 return 1
if __name__=='__main__':raise SystemExit(main())
