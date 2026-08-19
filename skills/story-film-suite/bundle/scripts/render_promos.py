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
from media_runtime import ASPECT_PROFILES, MediaRuntimeError, portable_rel, project_path, project_root, read_json, run, write_json
from promo_validate import validate_social, validate_trailers
from render_timeline import render as render_timeline, validate_timeline


def render_audio_if_needed(root: Path, mix_rel: str | None, timeline: dict, dry_run: bool, force: bool):
    if not mix_rel:
        return
    mix_path = project_path(root, mix_rel, must_exist=True)
    mix = read_json(mix_path)
    audio_rel = timeline.get('audio_master_path')
    if audio_rel and mix.get('output_path') != audio_rel:
        raise MediaRuntimeError(f'{mix_rel}: output_path does not match timeline audio_master_path')
    planned_duration = sum(float(x['duration']) for x in timeline['events'])
    existing_duration = mix.get('master_duration')
    frame_tolerance = 1.0 / float(timeline['video']['fps'])
    if existing_duration is None:
        mix['master_duration'] = planned_duration
        if not dry_run:
            write_json(mix_path, mix)
    elif not isinstance(existing_duration, (int, float)) or abs(float(existing_duration) - planned_duration) > frame_tolerance:
        raise MediaRuntimeError(f'{mix_rel}: master_duration does not match planned promo duration')
    errors = validate_audio(root, mix, require_sources=not dry_run)
    if errors:
        raise MediaRuntimeError('; '.join(errors))
    output = project_path(root, mix['output_path'])
    if not dry_run and audio_output_stale(root, mix_path, mix, output, force=force):
        run(audio_command(root, mix))


def trailer_jobs(root: Path):
    path = root / '06_release/trailers/trailer_manifest.json'
    if not path.exists():
        return []
    obj = read_json(path)
    return [rec for rec in obj.get('trailers', []) if isinstance(rec, dict)]


def social_jobs(root: Path):
    path = root / '06_release/social/deliverables.jsonl'
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip():
            rec = json.loads(line)
            if isinstance(rec, dict) and rec.get('media_type') == 'video' and rec.get('timeline_path'):
                rows.append(rec)
    return rows


def render_job(root: Path, rec: dict, kind: str, dry_run: bool, force: bool) -> dict:
    stable_id = rec['trailer_id'] if kind == 'trailer' else rec['social_id']
    tl_rel = rec['timeline_path']
    tl_path = project_path(root, tl_rel, must_exist=True)
    timeline = read_json(tl_path)
    # Validate structure first because the declared audio master may be built
    # from this promo job's audio mix during the same invocation.
    errors = validate_timeline(root, timeline, require_sources=False)
    if errors:
        raise MediaRuntimeError(f'{stable_id}: ' + '; '.join(errors))
    mix_rel = rec.get('audio_mix_path')
    if not mix_rel and kind == 'social':
        guess = str(Path(tl_rel).with_name('audio_mix.json')).replace('\\', '/')
        if project_path(root, guess).exists():
            mix_rel = guess
    render_audio_if_needed(root, mix_rel, timeline, dry_run, force)
    if dry_run:
        return {'id': stable_id, 'status': 'validated', 'output_path': timeline['output_path']}
    errors = validate_timeline(root, timeline, require_sources=True)
    if errors:
        raise MediaRuntimeError(f'{stable_id}: ' + '; '.join(errors))
    report = render_timeline(
        root, tl_path, timeline, force=force,
        mux_subtitles=timeline.get('subtitle_mode') == 'muxed',
    )
    video = timeline['video']
    target = float(rec.get('target_duration', sum(float(x['duration']) for x in timeline['events'])))
    tol = float(rec.get('duration_tolerance', 1.0 if kind == 'social' else 2.0))
    spec = {
        'delivery_id': f'DELIV-{(1000 if kind == "trailer" else 2000) + int(stable_id.split("-")[-1]):04d}',
        'kind': f'{kind}-master',
        'path': timeline['output_path'],
        'required': True,
        'video_required': True,
        'audio_required': bool(timeline.get('audio_master_path')),
        'width': int(video['width']),
        'height': int(video['height']),
        'fps': float(video['fps']),
        'fps_tolerance': 0.03,
        'duration': target,
        'duration_tolerance': tol,
        'video_codec': 'h264',
        'subtitle_required': timeline.get('subtitle_mode', 'sidecar' if timeline.get('subtitles_path') else 'none') == 'muxed',
    }
    qc = inspect_one(root, spec)
    qc_dir = root / ('06_release/trailers' if kind == 'trailer' else '06_release/social/qc')
    if kind == 'trailer':
        qc_path = project_path(root, str(Path(tl_rel).with_name('qc.json')).replace('\\', '/'))
    else:
        qc_path = qc_dir / f'{stable_id}.json'
    write_json(qc_path, {'schema_version': 1, **qc})
    if qc['status'] == 'fail':
        return {'id': stable_id, 'status': 'fail', 'render': report, 'qc': qc}
    media_id = register_primary_output(
        root,
        kind=f'{kind}-master',
        group_id=stable_id,
        path=timeline['output_path'],
        source_ids=list(rec.get('source_ids', [])) + [stable_id],
        qc_status=qc['status'],
        reason=f'Deterministic {kind} render passed delivery QC',
    )
    return {'id': stable_id, 'status': qc['status'], 'render': report, 'qc': qc, 'media_id': media_id}


def main() -> int:
    ap = argparse.ArgumentParser(description='Render trailer and social-video masters from shared executable timeline contracts.')
    ap.add_argument('project_dir')
    ap.add_argument('--scope', choices=['all', 'trailers', 'social'], default='all')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args()
    root = project_root(args.project_dir)
    manifest_errors = []
    if args.scope in {'all', 'trailers'}:
        manifest_errors += validate_trailers(root)
    if args.scope in {'all', 'social'}:
        manifest_errors += validate_social(root)
    if manifest_errors:
        for e in manifest_errors:
            print('ERROR', e)
        return 1
    results = []
    if args.scope in {'all', 'trailers'}:
        for rec in trailer_jobs(root):
            results.append(render_job(root, rec, 'trailer', args.dry_run, args.force))
    if args.scope in {'all', 'social'}:
        for rec in social_jobs(root):
            results.append(render_job(root, rec, 'social', args.dry_run, args.force))
    print(json.dumps({'status': 'fail' if any(x['status'] == 'fail' for x in results) else 'pass', 'results': results}, indent=2))
    return 1 if any(x['status'] == 'fail' for x in results) else 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except MediaRuntimeError as exc:
        print(f'ERROR {exc}')
        raise SystemExit(2)
