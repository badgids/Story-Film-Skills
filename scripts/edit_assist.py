#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from media_runtime import MediaRuntimeError, ASPECT_PROFILES, ffprobe, project_path, project_root, run, tool
from social_reframe import cover_crop

SILENCE_START=re.compile(r'silence_start:\s*([0-9.]+)')
SILENCE_END=re.compile(r'silence_end:\s*([0-9.]+)')


def media_duration(path: Path) -> float:
    return float((ffprobe(path).get('format') or {}).get('duration') or 0)


def detect_silence(path: Path, noise_db: float=-35.0, min_duration: float=0.5) -> dict:
    argv=[tool('ffmpeg'),'-hide_banner','-nostats','-i',str(path),'-af',f'silencedetect=n={noise_db}dB:d={min_duration}','-f','null','-']
    p=subprocess.run(argv,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
    if p.returncode: raise MediaRuntimeError('ffmpeg silencedetect failed')
    starts=[float(m.group(1)) for m in SILENCE_START.finditer(p.stdout)]
    ends=[float(m.group(1)) for m in SILENCE_END.finditer(p.stdout)]
    total=media_duration(path); silences=[]
    for i,s in enumerate(starts):
        e=ends[i] if i < len(ends) else total
        if e>s: silences.append({'start':s,'end':e,'duration':e-s})
    keep=[]; cursor=0.0
    for s in silences:
        if s['start']>cursor: keep.append({'start':cursor,'end':s['start'],'duration':s['start']-cursor})
        cursor=max(cursor,s['end'])
    if cursor<total: keep.append({'start':cursor,'end':total,'duration':total-cursor})
    return {'schema_version':1,'source_duration':total,'noise_db':noise_db,'min_silence':min_duration,'silences':silences,'keep':keep}


def render_jump_cut(source: Path, output: Path, keep: list[dict], padding: float=0.0) -> None:
    if not keep: raise MediaRuntimeError('jump cut has no keep intervals')
    info=ffprobe(source); has_audio=any(s.get('codec_type')=='audio' for s in info.get('streams',[]))
    parts=[]; labels=[]
    total=media_duration(source)
    for i,seg in enumerate(keep):
        s=max(0,float(seg['start'])-padding); e=min(total,float(seg['end'])+padding)
        parts.append(f'[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}]')
        if has_audio: parts.append(f'[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS[a{i}]')
        labels.append(f'[v{i}]' + (f'[a{i}]' if has_audio else ''))
    concat=''.join(labels)+f'concat=n={len(keep)}:v=1:a={1 if has_audio else 0}[v]' + ('[a]' if has_audio else '')
    fc=';'.join(parts+[concat]); output.parent.mkdir(parents=True,exist_ok=True)
    argv=[tool('ffmpeg'),'-hide_banner','-loglevel','error','-y','-i',str(source),'-filter_complex',fc,'-map','[v]']
    if has_audio: argv += ['-map','[a]']
    argv += ['-c:v','libx264','-crf','18','-pix_fmt','yuv420p']
    if has_audio: argv += ['-c:a','aac','-b:a','192k']
    argv += [str(output)]; run(argv); ffprobe(output)


def burn_captions(source: Path, srt: Path, output: Path) -> None:
    output.parent.mkdir(parents=True,exist_ok=True)
    escaped=str(srt).replace('\\','/').replace(':','\\:').replace("'","\\'")
    vf=f"subtitles=filename='{escaped}'"
    run([tool('ffmpeg'),'-hide_banner','-loglevel','error','-y','-i',str(source),'-vf',vf,'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','copy',str(output)]); ffprobe(output)


def clip(source: Path, output: Path, start: float, end: float, copy_mode: bool=False) -> None:
    if end<=start: raise MediaRuntimeError('clip end must be greater than start')
    output.parent.mkdir(parents=True,exist_ok=True)
    argv=[tool('ffmpeg'),'-hide_banner','-loglevel','error','-y','-ss',str(start),'-to',str(end),'-i',str(source)]
    argv += ['-c','copy'] if copy_mode else ['-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k']
    argv += [str(output)]; run(argv); ffprobe(output)

PRESETS={
    'review': {'height':720,'crf':26,'audio':'128k'},
    'web-hq': {'height':1080,'crf':20,'audio':'192k'},
    'vertical-hq': {'width':1080,'height':1920,'crf':20,'audio':'192k'},
    'small-share': {'height':480,'crf':30,'audio':'96k'},
}


def compress(source: Path, output: Path, preset: str) -> None:
    if preset not in PRESETS: raise MediaRuntimeError(f'unknown preset {preset!r}')
    p=PRESETS[preset]; output.parent.mkdir(parents=True,exist_ok=True)
    if p.get('width'):
        vf=f"scale={p['width']}:{p['height']}:force_original_aspect_ratio=decrease,pad={p['width']}:{p['height']}:(ow-iw)/2:(oh-ih)/2:black,setsar=1"
    else: vf=f"scale=-2:'min({p['height']},ih)'"
    run([tool('ffmpeg'),'-hide_banner','-loglevel','error','-y','-i',str(source),'-vf',vf,'-c:v','libx264','-crf',str(p['crf']),'-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a',p['audio'],str(output)]); ffprobe(output)


def face_focus(source: Path, sample_every: int=30, max_samples: int=120) -> tuple[float,float,int]:
    try:
        import cv2
        import numpy as np
    except Exception as exc:
        raise MediaRuntimeError('OpenCV and NumPy are required for face focus estimation') from exc
    cap=cv2.VideoCapture(str(source)); cascade=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
    xs=[]; ys=[]; frame=0; samples=0
    width=max(1,int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))); height=max(1,int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    while cap.isOpened() and samples<max_samples:
        ok,img=cap.read()
        if not ok: break
        if frame % sample_every==0:
            gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY); faces=cascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=4,minSize=(40,40))
            if len(faces):
                x,y,w,h=max(faces,key=lambda r:r[2]*r[3]); xs.append((x+w/2)/width); ys.append((y+h/2)/height)
            samples+=1
        frame+=1
    cap.release()
    if not xs: return 0.5,0.5,0
    return float(np.median(xs)),float(np.median(ys)),len(xs)


def reframe(source: Path, output: Path, aspect: str, focus_x: float, focus_y: float) -> None:
    ow,oh=ASPECT_PROFILES[aspect]; info=ffprobe(source); stream=next((s for s in info.get('streams',[]) if s.get('codec_type')=='video'),None)
    if not stream: raise MediaRuntimeError('source has no video stream')
    iw,ih=int(stream['width']),int(stream['height']); cw,ch,x,y=cover_crop(iw,ih,ow,oh,focus_x,focus_y); vf=f'crop={cw}:{ch}:{x}:{y},scale={ow}:{oh},setsar=1'
    output.parent.mkdir(parents=True,exist_ok=True); run([tool('ffmpeg'),'-hide_banner','-loglevel','error','-y','-i',str(source),'-vf',vf,'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','copy',str(output)]); ffprobe(output)


def transcribe(source: Path, output_srt: Path, model_name: str, language: str | None) -> None:
    try:
        from faster_whisper import WhisperModel
    except Exception as exc:
        raise MediaRuntimeError('faster-whisper is not installed; transcription cannot be claimed') from exc
    model=WhisperModel(model_name,device='auto',compute_type='auto'); segments,_=model.transcribe(str(source),language=language,word_timestamps=False)
    def ts(sec: float) -> str:
        ms=int(round(sec*1000)); h,rem=divmod(ms,3600000); m,rem=divmod(rem,60000); s,ms=divmod(rem,1000); return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
    lines=[]
    for i,seg in enumerate(segments,1): lines.extend([str(i),f'{ts(seg.start)} --> {ts(seg.end)}',seg.text.strip(),''])
    output_srt.parent.mkdir(parents=True,exist_ok=True); output_srt.write_text('\n'.join(lines),encoding='utf-8')


def main() -> int:
    ap=argparse.ArgumentParser(description='Non-destructive deterministic film edit assistance.')
    sub=ap.add_subparsers(dest='cmd',required=True)
    p=sub.add_parser('silence-map'); p.add_argument('project_dir'); p.add_argument('--input',required=True); p.add_argument('--output',default='05_post/edit_assist/silence_map.json'); p.add_argument('--noise-db',type=float,default=-35); p.add_argument('--min-silence',type=float,default=.5)
    p=sub.add_parser('jump-cut'); p.add_argument('project_dir'); p.add_argument('--input',required=True); p.add_argument('--map',default='05_post/edit_assist/silence_map.json'); p.add_argument('--output',required=True); p.add_argument('--padding',type=float,default=.0)
    p=sub.add_parser('burn-captions'); p.add_argument('project_dir'); p.add_argument('--input',required=True); p.add_argument('--srt',required=True); p.add_argument('--output',required=True)
    p=sub.add_parser('clip'); p.add_argument('project_dir'); p.add_argument('--input',required=True); p.add_argument('--output',required=True); p.add_argument('--start',type=float,required=True); p.add_argument('--end',type=float,required=True); p.add_argument('--copy',action='store_true')
    p=sub.add_parser('compress'); p.add_argument('project_dir'); p.add_argument('--input',required=True); p.add_argument('--output',required=True); p.add_argument('--preset',choices=sorted(PRESETS),required=True)
    p=sub.add_parser('reframe'); p.add_argument('project_dir'); p.add_argument('--input',required=True); p.add_argument('--output',required=True); p.add_argument('--aspect',choices=sorted(ASPECT_PROFILES),required=True); p.add_argument('--focus-x',type=float); p.add_argument('--focus-y',type=float); p.add_argument('--detect-face',action='store_true')
    p=sub.add_parser('transcribe'); p.add_argument('project_dir'); p.add_argument('--input',required=True); p.add_argument('--output',required=True); p.add_argument('--model',default='base'); p.add_argument('--language')
    args=ap.parse_args(); root=project_root(args.project_dir); src=project_path(root,args.input,must_exist=True)
    if args.cmd=='silence-map':
        obj=detect_silence(src,args.noise_db,args.min_silence); out=project_path(root,args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8'); print(args.output); return 0
    if args.cmd=='jump-cut':
        obj=json.loads(project_path(root,args.map,must_exist=True).read_text(encoding='utf-8')); out=project_path(root,args.output); render_jump_cut(src,out,obj.get('keep',[]),args.padding); print(args.output); return 0
    if args.cmd=='burn-captions': burn_captions(src,project_path(root,args.srt,must_exist=True),project_path(root,args.output)); print(args.output); return 0
    if args.cmd=='clip': clip(src,project_path(root,args.output),args.start,args.end,args.copy); print(args.output); return 0
    if args.cmd=='compress': compress(src,project_path(root,args.output),args.preset); print(args.output); return 0
    if args.cmd=='reframe':
        fx=.5 if args.focus_x is None else args.focus_x; fy=.5 if args.focus_y is None else args.focus_y
        if args.detect_face: fx,fy,count=face_focus(src); print(json.dumps({'focus_x':fx,'focus_y':fy,'face_samples':count}))
        reframe(src,project_path(root,args.output),args.aspect,fx,fy); print(args.output); return 0
    if args.cmd=='transcribe': transcribe(src,project_path(root,args.output),args.model,args.language); print(args.output); return 0
    return 2


if __name__=='__main__':
    try: raise SystemExit(main())
    except MediaRuntimeError as exc:
        print(f'ERROR {exc}'); raise SystemExit(2)
