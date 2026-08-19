#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
from pathlib import Path

from media_runtime import MediaRuntimeError, project_path, project_root, tool, run


def filter_expr(width: int, height: int, fps: float, fit: str) -> str:
    if fit == 'cover':
        scale = f'scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}'
    else:
        scale = f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black'
    return f'{scale},fps={fps:.6f},setsar=1'


def build_command(root: Path, rec: dict) -> list[str]:
    source = project_path(root, rec['input_path'], must_exist=True)
    output = project_path(root, rec['output_path'])
    output.parent.mkdir(parents=True, exist_ok=True)
    width = int(rec.get('width', 1920))
    height = int(rec.get('height', 1080))
    fps = float(rec.get('fps', 24.0))
    fit = rec.get('fit', 'contain')
    if width < 16 or height < 16 or fps <= 0 or fit not in {'contain', 'cover'}:
        raise MediaRuntimeError('invalid width, height, fps, or fit')
    cmd = [tool('ffmpeg'), '-hide_banner', '-loglevel', 'error', '-y']
    if float(rec.get('source_in', 0.0)) > 0:
        cmd += ['-ss', f'{float(rec["source_in"]):.6f}']
    cmd += ['-i', str(source)]
    if rec.get('duration') is not None:
        if float(rec['duration']) <= 0:
            raise MediaRuntimeError('duration must be positive')
        cmd += ['-t', f'{float(rec["duration"]):.6f}']
    codec = rec.get('codec', 'libx264')
    crf = int(rec.get('crf', 18))
    cmd += ['-vf', filter_expr(width, height, fps, fit), '-an', '-c:v', codec, '-crf', str(crf), '-pix_fmt', 'yuv420p', str(output)]
    return cmd


def main() -> int:
    ap = argparse.ArgumentParser(description='Conventional picture finishing from video_finish.jsonl.')
    ap.add_argument('project_dir')
    ap.add_argument('--manifest', default='05_post/video_finish.jsonl')
    ap.add_argument('--finish-id')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    root = project_root(args.project_dir)
    path = project_path(root, args.manifest, must_exist=True)
    records = []
    for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            raise MediaRuntimeError(f'{args.manifest}:{n}: invalid JSON: {exc}') from exc
        if args.finish_id and rec.get('finish_id') != args.finish_id:
            continue
        records.append(rec)
    if not records:
        raise MediaRuntimeError('no matching finish records')
    plans = []
    for rec in records:
        cmd = build_command(root, rec)
        if args.dry_run:
            plans.append(cmd)
        else:
            run(cmd)
    if args.dry_run:
        print(json.dumps(plans, indent=2))
    else:
        print(f'finished {len(records)} media item(s)')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except MediaRuntimeError as exc:
        print(f'ERROR {exc}')
        raise SystemExit(2)
