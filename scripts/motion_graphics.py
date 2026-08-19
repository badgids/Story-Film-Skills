#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from media_runtime import MediaRuntimeError, ffprobe, portable_rel, project_path, project_root, run, tool

GFX_RX = re.compile(r'^GFX-\d{3}$')


def esc(text: str) -> str:
    return str(text).replace('\\','\\\\').replace(':','\\:').replace("'","\\'").replace('%','\\%')


def color(value: str, default: str) -> str:
    v=str(value or default).strip()
    if re.fullmatch(r'#[0-9A-Fa-f]{6}',v):
        return '0x'+v[1:]
    if re.fullmatch(r'[A-Za-z]+',v) or re.fullmatch(r'0x[0-9A-Fa-f]{6}',v):
        return v
    return default


def validate_manifest(obj: dict) -> list[str]:
    errors=[]
    if obj.get('schema_version') != 1: errors.append('schema_version must be 1')
    if not isinstance(obj.get('input'),str) or not obj.get('input'): errors.append('input is required')
    elif not portable_rel(obj['input']): errors.append('input must be project-relative')
    if not isinstance(obj.get('output'),str) or not obj.get('output'): errors.append('output is required')
    elif not portable_rel(obj['output']): errors.append('output must be project-relative')
    graphics=obj.get('graphics')
    if not isinstance(graphics,list): errors.append('graphics must be an array'); return errors
    seen=set()
    allowed={'text','lower-third','letterbox','fade-in','fade-out'}
    for i,g in enumerate(graphics,1):
        gid=g.get('gfx_id',''); prefix=gid or f'graphic {i}'
        if not GFX_RX.fullmatch(gid or ''): errors.append(f'{prefix}: gfx_id must be GFX-###')
        elif gid in seen: errors.append(f'{gid}: duplicate gfx_id')
        seen.add(gid)
        if g.get('type') not in allowed: errors.append(f'{prefix}: unsupported type {g.get("type")!r}')
        if g.get('type') in {'text','lower-third'} and not str(g.get('text','')).strip(): errors.append(f'{prefix}: text is required')
        if 'start' in g and float(g.get('start',0)) < 0: errors.append(f'{prefix}: start must be nonnegative')
        if 'end' in g and float(g.get('end',0)) <= float(g.get('start',0)): errors.append(f'{prefix}: end must be greater than start')
    return errors


def pos_expr(position: str, margin: int = 48) -> tuple[str,str]:
    pos=position or 'lower-left'
    if pos=='upper-left': return str(margin),str(margin)
    if pos=='upper-right': return f'w-text_w-{margin}',str(margin)
    if pos=='center': return '(w-text_w)/2','(h-text_h)/2'
    if pos=='lower-right': return f'w-text_w-{margin}',f'h-text_h-{margin}'
    if pos=='lower-center': return '(w-text_w)/2',f'h-text_h-{margin}'
    return str(margin),f'h-text_h-{margin}'


def enable(g: dict) -> str:
    if 'start' in g and 'end' in g: return f":enable='between(t,{float(g['start'])},{float(g['end'])})'"
    return ''


def build_vf(graphics: list[dict], duration: float | None = None) -> str:
    filters=[]
    for g in graphics:
        kind=g['type']; style=g.get('style') or {}; en=enable(g)
        if kind=='text':
            x,y=pos_expr(g.get('position','lower-left'),int(style.get('margin',48)))
            fs=int(style.get('font_size',42)); fg=color(style.get('color'),'white'); box=int(bool(style.get('box',False)))
            boxpart=f":box={box}:boxcolor={color(style.get('box_color'),'black')}@{float(style.get('box_alpha',0.55))}" if box else ''
            filters.append(f"drawtext=font='Sans':text='{esc(g['text'])}':x={x}:y={y}:fontsize={fs}:fontcolor={fg}{boxpart}{en}")
        elif kind=='lower-third':
            start=float(g.get('start',0)); end=float(g.get('end',duration or start+4)); alpha=float(style.get('box_alpha',0.72)); boxc=color(style.get('box_color'),'black')
            filters.append(f"drawbox=x=36:y=h-190:w='min(iw-72,900)':h=130:color={boxc}@{alpha}:t=fill:enable='between(t,{start},{end})'")
            primary=esc(g['text']); secondary=esc(g.get('secondary','')); fg=color(style.get('color'),'white')
            filters.append(f"drawtext=font='Sans':text='{primary}':x=64:y=h-158:fontsize={int(style.get('font_size',40))}:fontcolor={fg}:enable='between(t,{start},{end})'")
            if secondary:
                filters.append(f"drawtext=font='Sans':text='{secondary}':x=64:y=h-105:fontsize={int(style.get('secondary_size',25))}:fontcolor={fg}:enable='between(t,{start},{end})'")
        elif kind=='letterbox':
            px=int(style.get('pixels',80)); c=color(style.get('color'),'black')
            filters.append(f'drawbox=x=0:y=0:w=iw:h={px}:color={c}:t=fill')
            filters.append(f'drawbox=x=0:y=ih-{px}:w=iw:h={px}:color={c}:t=fill')
        elif kind=='fade-in':
            start=float(g.get('start',0)); dur=float(g.get('duration',1)); filters.append(f'fade=t=in:st={start}:d={dur}')
        elif kind=='fade-out':
            start=float(g.get('start',max(0,(duration or 1)-1))); dur=float(g.get('duration',1)); filters.append(f'fade=t=out:st={start}:d={dur}')
    return ','.join(filters)


def render_manifest(root: Path, obj: dict, dry_run: bool=False) -> list[str]:
    errors=validate_manifest(obj)
    if errors: raise MediaRuntimeError('; '.join(errors))
    src=project_path(root,obj['input'],must_exist=True); out=project_path(root,obj['output']); out.parent.mkdir(parents=True,exist_ok=True)
    probe=ffprobe(src); duration=float((probe.get('format') or {}).get('duration') or 0)
    vf=build_vf(obj['graphics'],duration)
    argv=[tool('ffmpeg'),'-hide_banner','-loglevel','error','-y','-i',str(src)]
    if vf: argv += ['-vf',vf]
    argv += ['-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','copy',str(out)]
    if dry_run: return argv
    run(argv); ffprobe(out); return argv


def transition(root: Path, a_rel: str, b_rel: str, out_rel: str, kind: str, duration: float, offset: float | None) -> None:
    a=project_path(root,a_rel,must_exist=True); b=project_path(root,b_rel,must_exist=True); out=project_path(root,out_rel); out.parent.mkdir(parents=True,exist_ok=True)
    if offset is None:
        pa=ffprobe(a); ad=float((pa.get('format') or {}).get('duration') or 0); offset=max(0,ad-duration)
    transitions={'fade':'fade','wipe-left':'wipeleft','wipe-right':'wiperight','slide-left':'slideleft','slide-right':'slideright','circle-open':'circleopen','circle-close':'circleclose'}
    x=transitions.get(kind)
    if not x: raise MediaRuntimeError(f'unsupported transition {kind!r}')
    fc=f'[0:v][1:v]xfade=transition={x}:duration={duration}:offset={offset}[v];[0:a][1:a]acrossfade=d={duration}[a]'
    run([tool('ffmpeg'),'-hide_banner','-loglevel','error','-y','-i',str(a),'-i',str(b),'-filter_complex',fc,'-map','[v]','-map','[a]','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k',str(out)])
    ffprobe(out)


def main() -> int:
    ap=argparse.ArgumentParser(description='Render reusable motion graphics and transitions with FFmpeg.')
    sub=ap.add_subparsers(dest='cmd',required=True)
    p=sub.add_parser('render'); p.add_argument('project_dir'); p.add_argument('--manifest',default='05_post/graphics/graphics.json'); p.add_argument('--dry-run',action='store_true')
    p=sub.add_parser('transition'); p.add_argument('project_dir'); p.add_argument('--a',required=True); p.add_argument('--b',required=True); p.add_argument('--output',required=True); p.add_argument('--type',default='fade'); p.add_argument('--duration',type=float,default=0.5); p.add_argument('--offset',type=float)
    args=ap.parse_args(); root=project_root(args.project_dir)
    if args.cmd=='render':
        mp=project_path(root,args.manifest,must_exist=True); obj=json.loads(mp.read_text(encoding='utf-8')); argv=render_manifest(root,obj,args.dry_run); print(json.dumps(argv,indent=2) if args.dry_run else obj['output']); return 0
    transition(root,args.a,args.b,args.output,args.type,args.duration,args.offset); print(args.output); return 0


if __name__=='__main__':
    try: raise SystemExit(main())
    except MediaRuntimeError as exc:
        print(f'ERROR {exc}'); raise SystemExit(2)
