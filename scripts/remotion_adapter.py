#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

from media_runtime import MediaRuntimeError, portable_rel, project_path, project_root

COMP_RX = re.compile(r'^COMP-\d{3}$')


def read_manifest(path: Path) -> dict:
    try:
        obj=json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        raise MediaRuntimeError(f'invalid composition manifest: {path}') from exc
    if obj.get('schema_version') != 1 or not isinstance(obj.get('compositions'),list):
        raise MediaRuntimeError('composition manifest requires schema_version=1 and compositions array')
    return obj


def validate(obj: dict) -> list[str]:
    errors=[]; seen=set()
    for i,c in enumerate(obj.get('compositions',[]),1):
        cid=c.get('composition_id',''); prefix=cid or f'composition {i}'
        if not COMP_RX.fullmatch(cid or ''): errors.append(f'{prefix}: composition_id must be COMP-###')
        elif cid in seen: errors.append(f'{cid}: duplicate composition_id')
        seen.add(cid)
        for field in ('width','height','fps','duration_frames'):
            try:
                if int(c.get(field,0)) <= 0: errors.append(f'{prefix}: {field} must be positive')
            except Exception: errors.append(f'{prefix}: {field} must be integer')
        layers=c.get('layers',[])
        if not isinstance(layers,list): errors.append(f'{prefix}: layers must be an array'); continue
        for j,l in enumerate(layers,1):
            typ=l.get('type')
            if typ not in {'solid','text','image','video','audio'}: errors.append(f'{prefix}: layer {j} has unsupported type {typ!r}')
            if typ in {'image','video','audio'} and not portable_rel(str(l.get('path',''))): errors.append(f'{prefix}: layer {j} media path must be project-relative')
            start=int(l.get('start_frame',0)); dur=int(l.get('duration_frames',c.get('duration_frames',0)))
            if start<0 or dur<=0: errors.append(f'{prefix}: layer {j} timing is invalid')
            keyframes=l.get('keyframes', [])
            if keyframes is not None:
                if not isinstance(keyframes, list): errors.append(f'{prefix}: layer {j} keyframes must be an array')
                else:
                    last=-1
                    for kidx,kf in enumerate(keyframes,1):
                        if not isinstance(kf,dict): errors.append(f'{prefix}: layer {j} keyframe {kidx} must be object'); continue
                        try: frame=int(kf.get('frame',-1))
                        except Exception: frame=-1
                        if frame < 0 or frame < last: errors.append(f'{prefix}: layer {j} keyframes must use nonnegative ascending frames')
                        last=max(last,frame)
    return errors


def camel(s: str) -> str:
    return ''.join(x.capitalize() for x in re.split(r'[^A-Za-z0-9]+',s) if x) or 'Composition'


def scaffold(root: Path, obj: dict, out_rel: str, version: str, force_generated_code: bool=False) -> Path:
    errors=validate(obj)
    if errors: raise MediaRuntimeError('; '.join(errors))
    out=project_path(root,out_rel); out.mkdir(parents=True,exist_ok=True); src=out/'src'; public=out/'public/media'; src.mkdir(parents=True,exist_ok=True); public.mkdir(parents=True,exist_ok=True)
    copied={}
    for comp in obj['compositions']:
        for layer in comp.get('layers',[]):
            rel=layer.get('path')
            if not rel: continue
            source=project_path(root,rel,must_exist=True)
            key=rel.replace('\\','/')
            if key not in copied:
                dest_name=f'{len(copied)+1:03d}_{source.name}'; shutil.copy2(source,public/dest_name); copied[key]=f'media/{dest_name}'
            layer['adapter_path']=copied[key]
    (out/'composition-data.json').write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
    package={
        'name':'story-film-remotion-adapter','private':True,'version':'0.0.0',
        'scripts':{'studio':'remotion studio','render':'remotion render'},
        'dependencies':{'@remotion/cli':version,'remotion':version,'react':'^19.0.0','react-dom':'^19.0.0'}
    }
    if force_generated_code or not (out/'package.json').exists():
        (out/'package.json').write_text(json.dumps(package,indent=2)+'\n',encoding='utf-8')
    if force_generated_code or not (src/'index.ts').exists():
        (src/'index.ts').write_text("import {registerRoot} from 'remotion';\nimport {Root} from './Root';\nregisterRoot(Root);\n",encoding='utf-8')
    root_lines=["import React from 'react';","import {Composition} from 'remotion';","import data from '../composition-data.json';","import {GeneratedComposition} from './GeneratedComposition';","","export const Root: React.FC = () => (<>"]
    for comp in obj['compositions']:
        root_lines.append(f"  <Composition id=\"{camel(comp['composition_id'])}\" component={{GeneratedComposition}} durationInFrames={int(comp['duration_frames'])} fps={int(comp['fps'])} width={int(comp['width'])} height={int(comp['height'])} defaultProps={{{{compositionId: '{comp['composition_id']}'}}}} />")
    root_lines.append('</>);')
    if force_generated_code or not (src/'Root.tsx').exists():
        (src/'Root.tsx').write_text('\n'.join(root_lines)+'\n',encoding='utf-8')
    component=r'''import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, Video, staticFile, useCurrentFrame, interpolate} from 'remotion';
import data from '../composition-data.json';

type Props = {compositionId: string};

const valueAt = (layer: any, key: string, frame: number, fallback: number): number => {
  const frames = (layer.keyframes ?? []).filter((k: any) => typeof k[key] === 'number');
  if (!frames.length) return typeof layer[key] === 'number' ? layer[key] : fallback;
  if (frames.length === 1) return frames[0][key];
  const input = frames.map((k: any) => k.frame);
  const output = frames.map((k: any) => k[key]);
  return interpolate(frame, input, output, {extrapolateLeft:'clamp', extrapolateRight:'clamp'});
};

const layerStyle = (layer: any, frame: number): React.CSSProperties => {
  const start = layer.start_frame ?? 0;
  const dur = layer.duration_frames ?? 1;
  const local = frame - start;
  const baseOpacity = valueAt(layer, 'opacity', local, 1);
  const opacity = layer.fade_frames ? baseOpacity * interpolate(local, [0, layer.fade_frames, Math.max(layer.fade_frames, dur-layer.fade_frames), dur], [0,1,1,0], {extrapolateLeft:'clamp', extrapolateRight:'clamp'}) : baseOpacity;
  const x = valueAt(layer, 'x', local, 0);
  const y = valueAt(layer, 'y', local, 0);
  const scale = valueAt(layer, 'scale', local, 1);
  const rotate = valueAt(layer, 'rotate_deg', local, 0);
  const rotateX = valueAt(layer, 'rotate_x_deg', local, 0);
  const rotateY = valueAt(layer, 'rotate_y_deg', local, 0);
  const perspective = valueAt(layer, 'perspective', local, 1200);
  return {
    position: 'absolute', left: x, top: y,
    width: layer.width ?? '100%', height: layer.height ?? '100%',
    opacity, transform: `perspective(${perspective}px) scale(${scale}) rotate(${rotate}deg) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
    transformOrigin: layer.transform_origin ?? 'center center',
    color: layer.color ?? 'white', fontSize: layer.font_size ?? 48,
    fontFamily: layer.font_family ?? 'Arial, sans-serif', fontWeight: layer.font_weight ?? 400,
    objectFit: layer.fit ?? 'cover', display: 'flex', alignItems: layer.align_y ?? 'center', justifyContent: layer.align_x ?? 'center'
  };
};

export const GeneratedComposition: React.FC<Props> = ({compositionId}) => {
  const frame = useCurrentFrame();
  const comp: any = (data as any).compositions.find((x: any) => x.composition_id === compositionId);
  return <AbsoluteFill style={{backgroundColor: comp.background ?? 'black'}}>{comp.layers.map((layer: any, i: number) => {
    const start = layer.start_frame ?? 0; const dur = layer.duration_frames ?? comp.duration_frames;
    const style = layerStyle(layer, frame);
    let el: React.ReactNode = null;
    if (layer.type === 'solid') el = <div style={{...style, backgroundColor: layer.color ?? 'black'}} />;
    if (layer.type === 'text') el = <div style={style}>{layer.text ?? ''}</div>;
    if (layer.type === 'image') el = <Img src={staticFile(layer.adapter_path)} style={style} />;
    if (layer.type === 'video') el = <Video src={staticFile(layer.adapter_path)} style={style} volume={layer.volume ?? 1} />;
    if (layer.type === 'audio') el = <Audio src={staticFile(layer.adapter_path)} volume={layer.volume ?? 1} />;
    return <Sequence key={i} from={start} durationInFrames={dur}>{el}</Sequence>;
  })}</AbsoluteFill>;
};
'''
    if force_generated_code or not (src/'GeneratedComposition.tsx').exists():
        (src/'GeneratedComposition.tsx').write_text(component,encoding='utf-8')
    if force_generated_code or not (out/'README.md').exists():
        (out/'README.md').write_text('# Generated Remotion Adapter\n\nThis folder is generated from `05_post/programmatic/compositions.json`. Remotion is not bundled. Review its current license before installation or rendering.\n',encoding='utf-8')
    return out


def runtime_info(out: Path) -> dict:
    return {'node':shutil.which('node') or '', 'npm':shutil.which('npm') or '', 'npx':shutil.which('npx') or '', 'project_exists':(out/'package.json').is_file(), 'node_modules':(out/'node_modules/remotion').is_dir()}


def main() -> int:
    ap=argparse.ArgumentParser(description='Translate portable programmatic-video compositions to an optional Remotion project.')
    sub=ap.add_subparsers(dest='cmd',required=True)
    p=sub.add_parser('scaffold'); p.add_argument('project_dir'); p.add_argument('--manifest',default='05_post/programmatic/compositions.json'); p.add_argument('--output',default='05_post/programmatic/remotion'); p.add_argument('--remotion-version',default='4.0.513'); p.add_argument('--force-generated-code',action='store_true')
    p=sub.add_parser('discover'); p.add_argument('project_dir'); p.add_argument('--output',default='05_post/programmatic/remotion')
    p=sub.add_parser('install'); p.add_argument('project_dir'); p.add_argument('--output',default='05_post/programmatic/remotion'); p.add_argument('--acknowledge-license',action='store_true')
    p=sub.add_parser('render'); p.add_argument('project_dir'); p.add_argument('--output',default='05_post/programmatic/remotion'); p.add_argument('--composition',required=True); p.add_argument('--target',required=True); p.add_argument('--acknowledge-license',action='store_true')
    args=ap.parse_args(); root=project_root(args.project_dir); out=project_path(root,args.output)
    if args.cmd=='scaffold':
        obj=read_manifest(project_path(root,args.manifest,must_exist=True)); scaffold(root,obj,args.output,args.remotion_version,args.force_generated_code); print(args.output); return 0
    if args.cmd=='discover': print(json.dumps(runtime_info(out),indent=2)); return 0
    if not args.acknowledge_license: raise MediaRuntimeError('Remotion execution requires --acknowledge-license after reviewing current Remotion license terms')
    if not shutil.which('npm') or not shutil.which('npx'): raise MediaRuntimeError('Node npm/npx runtime is not available')
    if not (out/'package.json').is_file(): raise MediaRuntimeError('Remotion adapter project has not been scaffolded')
    if args.cmd=='install': subprocess.run([shutil.which('npm'),'install'],cwd=out,check=True); return 0
    target=project_path(root,args.target); target.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run([shutil.which('npx'),'remotion','render',args.composition,str(target)],cwd=out,check=True); print(args.target); return 0
    return 2


if __name__=='__main__':
    try: raise SystemExit(main())
    except (MediaRuntimeError, subprocess.CalledProcessError) as exc:
        print(f'ERROR {exc}'); raise SystemExit(2)
