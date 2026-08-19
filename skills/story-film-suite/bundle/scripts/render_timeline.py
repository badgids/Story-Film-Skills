#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from media_runtime import MediaRuntimeError, project_path, project_root, read_json, tool, run, write_json

EVENT_ID_RX = re.compile(r'^EVT-\d{3,}$')


def validate_timeline(root: Path, obj: dict, *, require_sources: bool = True) -> list[str]:
    errors = []
    if obj.get('schema_version') != 1:
        errors.append('unsupported schema_version')
    tid = obj.get('timeline_id', '')
    if not isinstance(tid, str) or not tid:
        errors.append('missing timeline_id')
    video = obj.get('video')
    if not isinstance(video, dict):
        errors.append('video must be an object')
        video = {}
    for field in ['width', 'height']:
        value = video.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 16:
            errors.append(f'video.{field} must be an integer >= 16')
    fps = video.get('fps')
    if not isinstance(fps, (int, float)) or isinstance(fps, bool) or fps <= 0:
        errors.append('video.fps must be positive')
    events = obj.get('events')
    if not isinstance(events, list) or not events:
        errors.append('events must be a nonempty array')
        return errors
    seen = set()
    for i, rec in enumerate(events, 1):
        if not isinstance(rec, dict):
            errors.append(f'event {i}: must be an object')
            continue
        eid = rec.get('event_id', '')
        if not isinstance(eid, str) or not EVENT_ID_RX.fullmatch(eid):
            errors.append(f'event {i}: invalid event_id {eid!r}')
        elif eid in seen:
            errors.append(f'event {i}: duplicate event_id {eid}')
        seen.add(eid)
        kind = rec.get('kind')
        if kind not in {'video', 'image', 'color'}:
            errors.append(f'event {i}: invalid kind {kind!r}')
        duration = rec.get('duration')
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration <= 0:
            errors.append(f'event {i}: duration must be positive')
        source_in = rec.get('source_in', 0.0)
        if not isinstance(source_in, (int, float)) or isinstance(source_in, bool) or source_in < 0:
            errors.append(f'event {i}: source_in must be nonnegative')
        if kind in {'video', 'image'}:
            try:
                project_path(root, rec.get('path', ''), must_exist=require_sources)
            except Exception as exc:
                errors.append(f'event {i}: {exc}')
        elif kind == 'color' and not isinstance(rec.get('color'), str):
            errors.append(f'event {i}: color event requires color string')
    for field in ['audio_master_path', 'subtitles_path', 'output_path']:
        value = obj.get(field)
        if value:
            try:
                project_path(root, value, must_exist=require_sources and field != 'output_path')
            except Exception as exc:
                errors.append(f'{field}: {exc}')
    subtitle_mode = obj.get('subtitle_mode', 'sidecar' if obj.get('subtitles_path') else 'none')
    if subtitle_mode not in {'none', 'sidecar', 'muxed'}:
        errors.append(f'invalid subtitle_mode {subtitle_mode!r}')
    if subtitle_mode in {'sidecar', 'muxed'} and not obj.get('subtitles_path'):
        errors.append(f'subtitle_mode {subtitle_mode} requires subtitles_path')
    if not obj.get('output_path'):
        errors.append('missing output_path')
    return errors


def event_command(root: Path, rec: dict, output: Path, width: int, height: int, fps: float) -> list[str]:
    ffmpeg = tool('ffmpeg')
    duration = float(rec['duration'])
    common_vf = f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,fps={fps:.6f},setsar=1'
    cmd = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-y']
    kind = rec['kind']
    if kind == 'video':
        source = project_path(root, rec['path'], must_exist=True)
        source_in = float(rec.get('source_in', 0.0))
        if source_in > 0:
            cmd += ['-ss', f'{source_in:.6f}']
        cmd += ['-i', str(source), '-t', f'{duration:.6f}', '-an', '-vf', common_vf]
    elif kind == 'image':
        source = project_path(root, rec['path'], must_exist=True)
        cmd += ['-loop', '1', '-i', str(source), '-t', f'{duration:.6f}', '-an', '-vf', common_vf]
    else:
        color = rec.get('color', 'black')
        cmd += ['-f', 'lavfi', '-i', f'color=c={color}:s={width}x{height}:r={fps:.6f}:d={duration:.6f}', '-an']
    cmd += ['-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output)]
    return cmd


def render(root: Path, timeline_path: Path, obj: dict, *, force: bool = False, mux_subtitles: bool = False) -> dict:
    errors = validate_timeline(root, obj, require_sources=True)
    if errors:
        raise MediaRuntimeError('; '.join(errors))
    video = obj['video']
    width, height, fps = int(video['width']), int(video['height']), float(video['fps'])
    output = project_path(root, obj['output_path'])
    output.parent.mkdir(parents=True, exist_ok=True)
    safe_tid = re.sub(r'[^A-Za-z0-9._-]+', '_', str(obj['timeline_id']))
    cache = timeline_path.parent / '.render_cache' / safe_tid
    cache.mkdir(parents=True, exist_ok=True)
    segments = []
    commands = []
    for idx, rec in enumerate(obj['events'], 1):
        seg = cache / f'{idx:05d}_{rec["event_id"]}.mp4'
        source = None
        if rec['kind'] in {'video', 'image'}:
            source = project_path(root, rec['path'], must_exist=True)
        stale = force or not seg.exists() or timeline_path.stat().st_mtime > seg.stat().st_mtime
        if source is not None and seg.exists() and source.stat().st_mtime > seg.stat().st_mtime:
            stale = True
        if stale:
            cmd = event_command(root, rec, seg, width, height, fps)
            commands.append(cmd)
            run(cmd)
        segments.append(seg)

    concat_list = cache / 'concat.txt'
    concat_list.write_text(''.join(f"file '{str(p).replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))}'\n" for p in segments), encoding='utf-8')
    picture = cache / 'picture.mp4'
    concat_cmd = [tool('ffmpeg'), '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(concat_list), '-c', 'copy', str(picture)]
    commands.append(concat_cmd)
    run(concat_cmd)

    audio_rel = obj.get('audio_master_path')
    subtitle_mode = obj.get('subtitle_mode', 'sidecar' if obj.get('subtitles_path') else 'none')
    should_mux_subtitles = mux_subtitles or subtitle_mode == 'muxed'
    subs_rel = obj.get('subtitles_path') if should_mux_subtitles else None
    if audio_rel:
        audio = project_path(root, audio_rel, must_exist=True)
        cmd = [tool('ffmpeg'), '-hide_banner', '-loglevel', 'error', '-y', '-i', str(picture), '-i', str(audio)]
        if subs_rel:
            subs = project_path(root, subs_rel, must_exist=True)
            cmd += ['-i', str(subs), '-map', '0:v:0', '-map', '1:a:0', '-map', '2:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k']
            if output.suffix.lower() == '.mp4':
                cmd += ['-c:s', 'mov_text']
            else:
                cmd += ['-c:s', 'srt']
        else:
            cmd += ['-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k']
        planned_duration = sum(float(x['duration']) for x in obj['events'])
        cmd += ['-t', f'{planned_duration:.6f}', '-movflags', '+faststart', str(output)]
    elif subs_rel:
        subs = project_path(root, subs_rel, must_exist=True)
        cmd = [tool('ffmpeg'), '-hide_banner', '-loglevel', 'error', '-y', '-i', str(picture), '-i', str(subs), '-map', '0:v:0', '-map', '1:0', '-c:v', 'copy']
        cmd += ['-c:s', 'mov_text' if output.suffix.lower() == '.mp4' else 'srt', str(output)]
    else:
        cmd = [tool('ffmpeg'), '-hide_banner', '-loglevel', 'error', '-y', '-i', str(picture), '-c', 'copy', str(output)]
    commands.append(cmd)
    run(cmd)

    report = {
        'schema_version': 1,
        'timeline_id': obj['timeline_id'],
        'timeline_path': str(timeline_path.relative_to(root)).replace('\\', '/'),
        'output_path': obj['output_path'],
        'event_count': len(obj['events']),
        'planned_duration': round(sum(float(x['duration']) for x in obj['events']), 6),
        'status': 'success',
        'muxed_audio': bool(audio_rel),
        'muxed_subtitles': bool(subs_rel),
        'subtitle_mode': subtitle_mode,
    }
    report_path = output.with_suffix(output.suffix + '.render.json')
    write_json(report_path, report)
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description='Validate or render an executable story-film timeline.')
    ap.add_argument('project_dir')
    ap.add_argument('--timeline', default='05_post/timeline.json')
    ap.add_argument('--validate-only', action='store_true')
    ap.add_argument('--dry-run', action='store_true', help='Validate and print the timeline summary without invoking FFmpeg.')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--mux-subtitles', action='store_true')
    args = ap.parse_args()
    root = project_root(args.project_dir)
    timeline_path = project_path(root, args.timeline, must_exist=True)
    obj = read_json(timeline_path)
    errors = validate_timeline(root, obj, require_sources=not args.dry_run)
    if errors:
        for e in errors:
            print('ERROR', e)
        return 1
    planned = sum(float(x['duration']) for x in obj['events'])
    if args.validate_only or args.dry_run:
        print(json.dumps({'timeline_id': obj['timeline_id'], 'events': len(obj['events']), 'planned_duration': planned, 'output_path': obj['output_path']}, indent=2))
        return 0
    report = render(root, timeline_path, obj, force=args.force, mux_subtitles=args.mux_subtitles)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except MediaRuntimeError as exc:
        print(f'ERROR {exc}')
        raise SystemExit(2)
