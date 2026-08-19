#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json

from media_runtime import ASPECT_PROFILES, MediaRuntimeError, ffprobe, project_path, project_root, tool, run


def source_dimensions(path):
    info = ffprobe(path)
    video = next((s for s in info.get('streams', []) if s.get('codec_type') == 'video'), None)
    if not video:
        raise MediaRuntimeError('source has no video stream')
    return int(video.get('width', 0)), int(video.get('height', 0))


def cover_crop(iw: int, ih: int, ow: int, oh: int, focus_x: float, focus_y: float):
    target_ar = ow / oh
    source_ar = iw / ih
    if source_ar > target_ar:
        ch = ih
        cw = int(round(ih * target_ar))
    else:
        cw = iw
        ch = int(round(iw / target_ar))
    center_x = focus_x * iw
    center_y = focus_y * ih
    x = int(round(center_x - cw / 2))
    y = int(round(center_y - ch / 2))
    x = max(0, min(iw - cw, x))
    y = max(0, min(ih - ch, y))
    return cw, ch, x, y


def build_command(root, input_rel, output_rel, width, height, mode, focus_x, focus_y):
    source = project_path(root, input_rel, must_exist=True)
    output = project_path(root, output_rel)
    output.parent.mkdir(parents=True, exist_ok=True)
    if mode == 'cover':
        iw, ih = source_dimensions(source)
        cw, ch, x, y = cover_crop(iw, ih, width, height, focus_x, focus_y)
        vf = f'crop={cw}:{ch}:{x}:{y},scale={width}:{height},setsar=1'
    else:
        vf = f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,setsar=1'
    return [tool('ffmpeg'), '-hide_banner', '-loglevel', 'error', '-y', '-i', str(source), '-vf', vf, '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', str(output)]


def main() -> int:
    ap = argparse.ArgumentParser(description='Deterministically reframe approved video for social delivery.')
    ap.add_argument('project_dir')
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--aspect', choices=sorted(ASPECT_PROFILES))
    ap.add_argument('--width', type=int)
    ap.add_argument('--height', type=int)
    ap.add_argument('--mode', choices=['contain', 'cover'], default='contain')
    ap.add_argument('--focus-x', type=float, default=0.5)
    ap.add_argument('--focus-y', type=float, default=0.5)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    root = project_root(args.project_dir)
    if args.aspect:
        width, height = ASPECT_PROFILES[args.aspect]
    elif args.width and args.height:
        width, height = args.width, args.height
    else:
        raise MediaRuntimeError('provide --aspect or both --width and --height')
    if width < 16 or height < 16:
        raise MediaRuntimeError('destination dimensions are too small')
    if not 0 <= args.focus_x <= 1 or not 0 <= args.focus_y <= 1:
        raise MediaRuntimeError('focus values must be between 0 and 1')
    cmd = build_command(root, args.input, args.output, width, height, args.mode, args.focus_x, args.focus_y)
    if args.dry_run:
        print(json.dumps(cmd, indent=2))
        return 0
    run(cmd)
    print(args.output)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except MediaRuntimeError as exc:
        print(f'ERROR {exc}')
        raise SystemExit(2)
