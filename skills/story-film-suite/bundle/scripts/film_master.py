#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
from pathlib import Path

from audio_master import build_command as audio_command, output_stale as audio_output_stale, validate_manifest as validate_audio
from delivery_qc import inspect_one
from media_registry import register_primary_output
from media_runtime import MediaRuntimeError, project_path, project_root, read_json, run, write_json
from render_timeline import render as render_timeline, validate_timeline


def ensure_delivery_spec(root: Path, timeline: dict, *, persist: bool = True) -> dict:
    rel = '06_release/delivery_specs.json'
    path = project_path(root, rel)
    if path.exists():
        obj = read_json(path)
        if obj.get('schema_version') != 1 or not isinstance(obj.get('deliverables'), list):
            raise MediaRuntimeError(f'{rel} has invalid shape')
    else:
        obj = {'schema_version': 1, 'deliverables': []}
    planned = sum(float(x['duration']) for x in timeline['events'])
    video = timeline['video']
    existing = next((x for x in obj['deliverables'] if isinstance(x, dict) and x.get('path') == timeline['output_path']), None)
    if existing and isinstance(existing.get('delivery_id'), str):
        delivery_id = existing['delivery_id']
    else:
        used = []
        for x in obj['deliverables']:
            did = x.get('delivery_id') if isinstance(x, dict) else None
            if isinstance(did, str) and did.startswith('DELIV-') and did[6:].isdigit():
                used.append(int(did[6:]))
        delivery_id = f'DELIV-{max(used, default=0) + 1:03d}'
    spec = {
        'delivery_id': delivery_id,
        'kind': 'film-master',
        'path': timeline['output_path'],
        'source_ids': [timeline.get('timeline_id', 'MASTER-001')],
        'required': True,
        'video_required': True,
        'audio_required': bool(timeline.get('audio_master_path')),
        'width': int(video['width']),
        'height': int(video['height']),
        'fps': float(video['fps']),
        'fps_tolerance': 0.03,
        'duration': planned,
        'duration_tolerance': max(0.5, 1.0 / float(video['fps']) * 4.0),
        'video_codec': 'h264',
        'audio_sample_rate': 48000 if timeline.get('audio_master_path') else None,
        'subtitle_required': timeline.get('subtitle_mode', 'sidecar' if timeline.get('subtitles_path') else 'none') == 'muxed',
    }
    rows = [x for x in obj['deliverables'] if isinstance(x, dict) and x.get('delivery_id') != delivery_id]
    rows.insert(0, spec)
    obj['deliverables'] = rows
    if persist:
        write_json(path, obj)
    return spec


def main() -> int:
    ap = argparse.ArgumentParser(description='Render and verify the finished film master.')
    ap.add_argument('project_dir')
    ap.add_argument('--timeline', default='05_post/timeline.json')
    ap.add_argument('--audio-manifest', default='05_post/audio_mix.json')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--mux-subtitles', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    root = project_root(args.project_dir)
    timeline_path = project_path(root, args.timeline, must_exist=True)
    timeline = read_json(timeline_path)
    # Validate structure and portable paths first. The audio master may be an
    # output of this command, so requiring it before the mix runs would make
    # a clean first render impossible.
    errors = validate_timeline(root, timeline, require_sources=False)
    if errors:
        for e in errors:
            print('ERROR', e)
        return 1

    audio_rel = timeline.get('audio_master_path')
    if audio_rel:
        audio_output = project_path(root, audio_rel)
        mix_path = project_path(root, args.audio_manifest)
        if mix_path.exists():
            mix = read_json(mix_path)
            if mix.get('output_path') != audio_rel:
                raise MediaRuntimeError('timeline audio_master_path does not match audio mix output_path')
            planned_duration = sum(float(x['duration']) for x in timeline['events'])
            existing_duration = mix.get('master_duration')
            frame_tolerance = 1.0 / float(timeline['video']['fps'])
            if existing_duration is None:
                mix['master_duration'] = planned_duration
                if not args.dry_run:
                    write_json(mix_path, mix)
            elif not isinstance(existing_duration, (int, float)) or abs(float(existing_duration) - planned_duration) > frame_tolerance:
                raise MediaRuntimeError('audio mix master_duration does not match planned picture duration')
            audio_errors = validate_audio(root, mix, require_sources=not args.dry_run)
            if audio_errors:
                raise MediaRuntimeError('; '.join(audio_errors))
            if not args.dry_run and audio_output_stale(root, mix_path, mix, audio_output, force=args.force):
                run(audio_command(root, mix))
        elif not audio_output.exists():
            raise MediaRuntimeError(f'missing audio master and audio mix manifest: {args.audio_manifest}')

    # After buildable masters have been created, enforce the full source
    # contract before rendering picture.
    if not args.dry_run:
        errors = validate_timeline(root, timeline, require_sources=True)
        if errors:
            for e in errors:
                print('ERROR', e)
            return 1

    spec = ensure_delivery_spec(root, timeline, persist=not args.dry_run)
    if args.dry_run:
        print(json.dumps({'status': 'validated', 'timeline': args.timeline, 'output': timeline['output_path'], 'delivery_spec': spec}, indent=2))
        return 0

    render_report = render_timeline(
        root, timeline_path, timeline, force=args.force,
        mux_subtitles=args.mux_subtitles or timeline.get('subtitle_mode') == 'muxed',
    )
    qc = inspect_one(root, spec)
    qc_path = root / '05_post/qc/film_master.json'
    write_json(qc_path, {'schema_version': 1, **qc})
    if qc['status'] == 'fail':
        print(json.dumps({'render': render_report, 'qc': qc}, indent=2))
        return 1
    master_group = timeline.get('timeline_id') if isinstance(timeline.get('timeline_id'), str) and timeline.get('timeline_id', '').startswith('MASTER-') else 'MASTER-001'
    media_id = register_primary_output(
        root,
        kind='film-master',
        group_id=master_group,
        path=timeline['output_path'],
        source_ids=[master_group],
        qc_status=qc['status'],
        reason='Deterministic film render passed delivery QC',
    )
    out = {'status': 'pass', 'render': render_report, 'qc': qc, 'media_id': media_id}
    print(json.dumps(out, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except MediaRuntimeError as exc:
        print(f'ERROR {exc}')
        raise SystemExit(2)
