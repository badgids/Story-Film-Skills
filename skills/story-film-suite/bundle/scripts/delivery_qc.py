#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

from media_runtime import MediaRuntimeError, ffprobe, frame_rate, project_path, project_root, read_json, run, sha256, tool, write_json


def detect_black_frames(path: Path, cfg: dict) -> list[dict]:
    min_duration = float(cfg.get('min_duration', 1.0))
    picture_ratio = float(cfg.get('picture_black_ratio', 0.98))
    pixel_threshold = float(cfg.get('pixel_black_threshold', 0.10))
    proc = run([
        tool('ffmpeg'), '-hide_banner', '-nostats', '-i', str(path),
        '-vf', f'blackdetect=d={min_duration:.6f}:pic_th={picture_ratio:.6f}:pix_th={pixel_threshold:.6f}',
        '-an', '-f', 'null', '-'
    ], capture=True)
    text = (proc.stderr or '') + '\n' + (proc.stdout or '')
    rows = []
    for m in re.finditer(r'black_start:([0-9.]+)\s+black_end:([0-9.]+)\s+black_duration:([0-9.]+)', text):
        rows.append({'start': float(m.group(1)), 'end': float(m.group(2)), 'duration': float(m.group(3))})
    return rows


def detect_freeze_frames(path: Path, cfg: dict) -> list[dict]:
    min_duration = float(cfg.get('min_duration', 2.0))
    noise_db = float(cfg.get('noise_db', -60.0))
    proc = run([
        tool('ffmpeg'), '-hide_banner', '-nostats', '-i', str(path),
        '-vf', f'freezedetect=n={noise_db:.2f}dB:d={min_duration:.6f}',
        '-an', '-f', 'null', '-'
    ], capture=True)
    text = (proc.stderr or '') + '\n' + (proc.stdout or '')
    starts = [float(x) for x in re.findall(r'freeze_start:\s*([0-9.]+)', text)]
    durations = [float(x) for x in re.findall(r'freeze_duration:\s*([0-9.]+)', text)]
    ends = [float(x) for x in re.findall(r'freeze_end:\s*([0-9.]+)', text)]
    rows = []
    for i, start in enumerate(starts):
        row = {'start': start}
        if i < len(ends):
            row['end'] = ends[i]
        if i < len(durations):
            row['duration'] = durations[i]
        rows.append(row)
    return rows


def inspect_one(root: Path, spec: dict) -> dict:
    rel = spec.get('path', '')
    result = {
        'delivery_id': spec.get('delivery_id', ''),
        'kind': spec.get('kind', ''),
        'path': rel,
        'status': 'pass',
        'checks': [],
        'sha256': '',
    }
    def check(name, passed, observed=None, expected=None, severity='fail'):
        result['checks'].append({'name': name, 'status': 'pass' if passed else severity, 'observed': observed, 'expected': expected})
        if not passed and severity == 'fail':
            result['status'] = 'fail'
        elif not passed and result['status'] == 'pass':
            result['status'] = 'warn'
    try:
        path = project_path(root, rel, must_exist=True)
    except Exception as exc:
        check('file_exists', False, str(exc), True)
        return result
    check('file_nonempty', path.stat().st_size > 0, path.stat().st_size, '>0')
    if path.stat().st_size <= 0:
        return result
    try:
        info = ffprobe(path)
    except Exception as exc:
        check('probe', False, str(exc), 'readable media')
        return result
    streams = info.get('streams', [])
    video = next((s for s in streams if s.get('codec_type') == 'video'), None)
    audio = next((s for s in streams if s.get('codec_type') == 'audio'), None)
    subtitle = next((s for s in streams if s.get('codec_type') == 'subtitle'), None)
    fmt = info.get('format', {})
    duration = float(fmt.get('duration') or (video or audio or {}).get('duration') or 0.0)
    if spec.get('video_required', spec.get('kind') not in {'audio-master', 'audio'}):
        check('video_stream', video is not None, bool(video), True)
    if spec.get('audio_required') is True:
        check('audio_stream', audio is not None, bool(audio), True)
    if spec.get('subtitle_required') is True:
        check('subtitle_stream', subtitle is not None, bool(subtitle), True)
    if video:
        if spec.get('width') is not None:
            check('width', int(video.get('width', 0)) == int(spec['width']), int(video.get('width', 0)), int(spec['width']))
        if spec.get('height') is not None:
            check('height', int(video.get('height', 0)) == int(spec['height']), int(video.get('height', 0)), int(spec['height']))
        if spec.get('fps') is not None:
            observed = frame_rate(video.get('avg_frame_rate') or video.get('r_frame_rate'))
            tolerance = float(spec.get('fps_tolerance', 0.02))
            check('fps', abs(observed - float(spec['fps'])) <= tolerance, observed, float(spec['fps']))
        if spec.get('video_codec'):
            check('video_codec', video.get('codec_name') == spec['video_codec'], video.get('codec_name'), spec['video_codec'])
    if audio:
        if spec.get('audio_sample_rate') is not None:
            observed = int(audio.get('sample_rate') or 0)
            check('audio_sample_rate', observed == int(spec['audio_sample_rate']), observed, int(spec['audio_sample_rate']))
        if spec.get('audio_channels') is not None:
            observed = int(audio.get('channels') or 0)
            check('audio_channels', observed == int(spec['audio_channels']), observed, int(spec['audio_channels']))
        if spec.get('audio_codec'):
            check('audio_codec', audio.get('codec_name') == spec['audio_codec'], audio.get('codec_name'), spec['audio_codec'])
    if spec.get('duration') is not None:
        tolerance = float(spec.get('duration_tolerance', 0.5))
        check('duration', abs(duration - float(spec['duration'])) <= tolerance, duration, float(spec['duration']))
    if video and isinstance(spec.get('black_frame_check'), dict) and spec['black_frame_check'].get('enabled', True):
        cfg = spec['black_frame_check']
        intervals = detect_black_frames(path, cfg)
        severity = str(cfg.get('severity', 'warn'))
        if severity not in {'warn', 'fail'}:
            severity = 'warn'
        check('black_frame_intervals', not intervals, intervals, [], severity)
    if video and isinstance(spec.get('freeze_frame_check'), dict) and spec['freeze_frame_check'].get('enabled', True):
        cfg = spec['freeze_frame_check']
        intervals = detect_freeze_frames(path, cfg)
        severity = str(cfg.get('severity', 'warn'))
        if severity not in {'warn', 'fail'}:
            severity = 'warn'
        check('freeze_frame_intervals', not intervals, intervals, [], severity)
    result['observed'] = {
        'duration': duration,
        'format_name': fmt.get('format_name', ''),
        'video_codec': video.get('codec_name') if video else None,
        'width': int(video.get('width', 0)) if video else None,
        'height': int(video.get('height', 0)) if video else None,
        'fps': frame_rate(video.get('avg_frame_rate') or video.get('r_frame_rate')) if video else None,
        'audio_codec': audio.get('codec_name') if audio else None,
        'audio_sample_rate': int(audio.get('sample_rate') or 0) if audio else None,
        'audio_channels': int(audio.get('channels') or 0) if audio else None,
        'subtitle_codec': subtitle.get('codec_name') if subtitle else None,
    }
    result['sha256'] = sha256(path)
    return result


def inspect_specs(root: Path, obj: dict) -> dict:
    if obj.get('schema_version') != 1 or not isinstance(obj.get('deliverables'), list):
        raise MediaRuntimeError('delivery spec must contain schema_version 1 and deliverables array')
    results = [inspect_one(root, spec) for spec in obj['deliverables'] if isinstance(spec, dict)]
    blocking = [r['delivery_id'] for r in results if r['status'] == 'fail' and next((d for d in obj['deliverables'] if d.get('delivery_id') == r['delivery_id']), {}).get('required', True)]
    return {'schema_version': 1, 'status': 'fail' if blocking else ('warn' if any(r['status'] == 'warn' for r in results) else 'pass'), 'blocking_delivery_ids': blocking, 'results': results}


def main() -> int:
    ap = argparse.ArgumentParser(description='Probe release deliverables against explicit specs.')
    ap.add_argument('project_dir')
    ap.add_argument('--spec', default='06_release/delivery_specs.json')
    ap.add_argument('--output', default='06_release/delivery_qc.json')
    args = ap.parse_args()
    root = project_root(args.project_dir)
    spec_path = project_path(root, args.spec, must_exist=True)
    obj = read_json(spec_path)
    report = inspect_specs(root, obj)
    output = project_path(root, args.output)
    write_json(output, report)
    print(json.dumps(report, indent=2))
    return 0 if report['status'] != 'fail' else 1


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except MediaRuntimeError as exc:
        print(f'ERROR {exc}')
        raise SystemExit(2)
