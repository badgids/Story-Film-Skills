#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from media_runtime import MediaRuntimeError, project_path, project_root, read_json, tool, run, write_json

KINDS = {'dialogue', 'voiceover', 'ambience', 'foley', 'sfx', 'score', 'music', 'room-tone', 'other'}


def validate_manifest(root: Path, obj: dict, *, require_sources: bool) -> list[str]:
    errors = []
    if obj.get('schema_version') != 1:
        errors.append('unsupported schema_version')
    sample_rate = obj.get('sample_rate', 48000)
    channels = obj.get('channels', 2)
    if not isinstance(sample_rate, int) or sample_rate < 8000:
        errors.append('sample_rate must be an integer >= 8000')
    if channels not in {1, 2}:
        errors.append('channels must be 1 or 2')
    if not isinstance(obj.get('target_lufs', -16.0), (int, float)):
        errors.append('target_lufs must be numeric')
    if not isinstance(obj.get('true_peak_db', -1.5), (int, float)):
        errors.append('true_peak_db must be numeric')
    master_duration = obj.get('master_duration')
    if master_duration is not None and (not isinstance(master_duration, (int, float)) or isinstance(master_duration, bool) or master_duration <= 0):
        errors.append('master_duration must be positive when provided')
    out = obj.get('output_path', '')
    try:
        project_path(root, out)
    except Exception as exc:
        errors.append(str(exc))
    tracks = obj.get('tracks')
    if not isinstance(tracks, list) or not tracks:
        errors.append('tracks must be a nonempty array')
        return errors
    seen = set()
    for i, rec in enumerate(tracks, 1):
        if not isinstance(rec, dict):
            errors.append(f'track {i}: must be an object')
            continue
        eid = rec.get('event_id')
        if not isinstance(eid, str) or not eid:
            errors.append(f'track {i}: missing event_id')
        elif eid in seen:
            errors.append(f'track {i}: duplicate event_id {eid}')
        seen.add(eid)
        if rec.get('kind') not in KINDS:
            errors.append(f'track {i}: invalid kind {rec.get("kind")!r}')
        try:
            project_path(root, rec.get('path', ''), must_exist=require_sources)
        except Exception as exc:
            errors.append(f'track {i}: {exc}')
        for field in ['start', 'source_in', 'gain_db', 'pan', 'fade_in', 'fade_out']:
            value = rec.get(field, 0.0)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(f'track {i}: {field} must be numeric')
        if float(rec.get('start', 0)) < 0 or float(rec.get('source_in', 0)) < 0:
            errors.append(f'track {i}: start/source_in cannot be negative')
        duration = rec.get('duration')
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration <= 0:
            errors.append(f'track {i}: duration must be positive')
        elif isinstance(master_duration, (int, float)) and isinstance(rec.get('start', 0), (int, float)) and float(rec.get('start', 0)) + float(duration) > float(master_duration) + 1e-6:
            errors.append(f'track {i}: event extends past master_duration')
        pan = rec.get('pan', 0.0)
        if isinstance(pan, (int, float)) and not -1.0 <= float(pan) <= 1.0:
            errors.append(f'track {i}: pan must be between -1 and 1')
    return errors


def output_stale(root: Path, manifest_path: Path, obj: dict, output: Path, *, force: bool = False) -> bool:
    if force or not output.exists():
        return True
    if manifest_path.stat().st_mtime > output.stat().st_mtime:
        return True
    for rec in obj.get('tracks', []):
        if not isinstance(rec, dict) or not isinstance(rec.get('path'), str):
            continue
        source = project_path(root, rec['path'], must_exist=True)
        if source.stat().st_mtime > output.stat().st_mtime:
            return True
    return False


def build_command(root: Path, obj: dict, output_override: str | None = None) -> list[str]:
    ffmpeg = tool('ffmpeg')
    inputs = []
    filters = []
    labels = []
    sample_rate = int(obj.get('sample_rate', 48000))
    channels = int(obj.get('channels', 2))
    tracks = obj['tracks']
    for idx, rec in enumerate(tracks):
        source = project_path(root, rec['path'], must_exist=True)
        inputs += ['-i', str(source)]
        start = float(rec.get('start', 0.0))
        source_in = float(rec.get('source_in', 0.0))
        duration = float(rec['duration'])
        gain = float(rec.get('gain_db', 0.0))
        pan = float(rec.get('pan', 0.0))
        fade_in = max(0.0, float(rec.get('fade_in', 0.0)))
        fade_out = max(0.0, float(rec.get('fade_out', 0.0)))
        chain = [
            f'atrim=start={source_in:.6f}:duration={duration:.6f}',
            'asetpts=PTS-STARTPTS',
            f'aresample={sample_rate}',
        ]
        if channels == 2:
            chain.append('aformat=channel_layouts=stereo')
            left = 1.0 if pan <= 0 else 1.0 - pan
            right = 1.0 if pan >= 0 else 1.0 + pan
            chain.append(f'pan=stereo|c0={left:.6f}*c0|c1={right:.6f}*c1')
        else:
            chain.append('aformat=channel_layouts=mono')
        chain.append(f'volume={gain:.4f}dB')
        if fade_in > 0:
            chain.append(f'afade=t=in:st=0:d={min(fade_in, duration):.6f}')
        if fade_out > 0:
            d = min(fade_out, duration)
            chain.append(f'afade=t=out:st={max(0.0, duration-d):.6f}:d={d:.6f}')
        delay_ms = int(round(start * 1000.0))
        if delay_ms:
            chain.append(f'adelay={delay_ms}|{delay_ms}' if channels == 2 else f'adelay={delay_ms}')
        label = f'a{idx}'
        filters.append(f'[{idx}:a]{",".join(chain)}[{label}]')
        labels.append(f'[{label}]')
    mixed = 'mix'
    filters.append(f'{"".join(labels)}amix=inputs={len(labels)}:duration=longest:normalize=0[{mixed}]')
    target = float(obj.get('target_lufs', -16.0))
    peak = float(obj.get('true_peak_db', -1.5))
    master_duration = obj.get('master_duration')
    if isinstance(master_duration, (int, float)):
        filters.append(f'[{mixed}]apad=whole_dur={float(master_duration):.6f},atrim=duration={float(master_duration):.6f},loudnorm=I={target:.2f}:TP={peak:.2f}:LRA=11,aresample={sample_rate}[master]')
    else:
        filters.append(f'[{mixed}]loudnorm=I={target:.2f}:TP={peak:.2f}:LRA=11,aresample={sample_rate}[master]')
    out_rel = output_override or obj['output_path']
    output = project_path(root, out_rel)
    output.parent.mkdir(parents=True, exist_ok=True)
    return [ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', *inputs, '-filter_complex', ';'.join(filters), '-map', '[master]', '-ar', str(sample_rate), '-ac', str(channels), '-c:a', 'pcm_s24le', str(output)]


def main() -> int:
    ap = argparse.ArgumentParser(description='Render a synchronized project audio master with FFmpeg.')
    ap.add_argument('project_dir')
    ap.add_argument('--manifest', default='05_post/audio_mix.json')
    ap.add_argument('--output')
    ap.add_argument('--validate-only', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    root = project_root(args.project_dir)
    manifest_path = project_path(root, args.manifest, must_exist=True)
    obj = read_json(manifest_path)
    errors = validate_manifest(root, obj, require_sources=not args.validate_only or not args.dry_run)
    if errors:
        for e in errors:
            print('ERROR', e)
        return 1
    if args.validate_only:
        print(f'OK: {len(obj["tracks"])} audio events')
        return 0
    cmd = build_command(root, obj, args.output)
    if args.dry_run:
        print(json.dumps(cmd, indent=2))
        return 0
    run(cmd)
    output_rel = args.output or obj['output_path']
    output = project_path(root, output_rel, must_exist=True)
    report = {
        'schema_version': 1,
        'manifest': args.manifest,
        'output_path': output_rel,
        'track_count': len(obj['tracks']),
        'sample_rate': obj.get('sample_rate', 48000),
        'channels': obj.get('channels', 2),
        'target_lufs': obj.get('target_lufs', -16.0),
        'true_peak_db': obj.get('true_peak_db', -1.5),
        'master_duration': obj.get('master_duration'),
        'status': 'success',
    }
    report_path = output.with_suffix(output.suffix + '.render.json')
    write_json(report_path, report)
    print(output_rel)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except MediaRuntimeError as exc:
        print(f'ERROR {exc}')
        raise SystemExit(2)
