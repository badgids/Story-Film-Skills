#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from feature_common import atomic_write_json, atomic_write_text, first_id, load_json, load_jsonl, now, records_from_json, rel

SCHEMA = 1
SEQ_STATUSES = {'planned', 'ready', 'in-production', 'generated', 'editing', 'approved', 'blocked', 'retired'}


def scene_records(root: Path) -> list[dict[str, Any]]:
    path = root / '02_screenplay/scene_manifest.json'
    value = load_json(path, {})
    records = records_from_json(value)
    out = []
    for i, rec in enumerate(records, 1):
        scene_id = first_id(rec, ('SCN-',)) or str(rec.get('scene_id') or rec.get('id') or f'SCN-{i:03d}')
        item = dict(rec)
        item['scene_id'] = scene_id
        out.append(item)
    return out


def make_sequences(scenes: list[dict[str, Any]], chunk_size: int) -> list[dict[str, Any]]:
    if chunk_size < 1:
        raise ValueError('chunk_size must be positive')
    out = []
    for offset in range(0, len(scenes), chunk_size):
        group = scenes[offset: offset + chunk_size]
        seq_num = len(out) + 1
        seq_id = f'SEQ-{seq_num:03d}'
        runtimes = []
        for rec in group:
            for key in ('approx_runtime_s', 'runtime_s', 'approximate_runtime_seconds'):
                if isinstance(rec.get(key), (int, float)):
                    runtimes.append(float(rec[key]))
                    break
        out.append({
            'sequence_id': seq_id,
            'title': f'Sequence {seq_num}',
            'order': seq_num,
            'scene_ids': [x['scene_id'] for x in group],
            'status': 'planned',
            'priority': 'normal',
            'estimated_runtime_s': round(sum(runtimes), 3) if runtimes else None,
            'shard_path': f'00_project/shards/{seq_id}/context.json',
            'notes': [],
        })
    return out


def validate_manifest(value: dict[str, Any], known_scenes: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    if value.get('schema_version') != SCHEMA:
        errors.append('sequence manifest schema_version must be 1')
    seqs = value.get('sequences')
    if not isinstance(seqs, list):
        return errors + ['sequence manifest sequences must be an array']
    ids: set[str] = set()
    seen_scenes: set[str] = set()
    expected_order = 1
    for i, rec in enumerate(seqs, 1):
        if not isinstance(rec, dict):
            errors.append(f'sequence {i} must be an object')
            continue
        sid = rec.get('sequence_id')
        if not isinstance(sid, str) or not sid.startswith('SEQ-'):
            errors.append(f'sequence {i} has invalid sequence_id')
            continue
        if sid in ids:
            errors.append(f'duplicate sequence_id {sid}')
        ids.add(sid)
        if rec.get('order') != expected_order:
            errors.append(f'{sid}: order must be {expected_order}')
        expected_order += 1
        if rec.get('status') not in SEQ_STATUSES:
            errors.append(f'{sid}: invalid status {rec.get("status")!r}')
        scenes = rec.get('scene_ids')
        if not isinstance(scenes, list) or not scenes:
            errors.append(f'{sid}: scene_ids must be a non-empty array')
            continue
        for scene_id in scenes:
            if not isinstance(scene_id, str) or not scene_id.startswith('SCN-'):
                errors.append(f'{sid}: invalid scene id {scene_id!r}')
                continue
            if scene_id in seen_scenes:
                errors.append(f'{scene_id}: assigned to more than one sequence')
            seen_scenes.add(scene_id)
            if known_scenes is not None and scene_id not in known_scenes:
                errors.append(f'{sid}: unknown scene {scene_id}')
        shard = rec.get('shard_path', '')
        if not isinstance(shard, str) or shard.startswith('/') or '..' in Path(shard).parts:
            errors.append(f'{sid}: shard_path must be project-relative')
    if known_scenes is not None:
        missing = sorted(known_scenes - seen_scenes)
        if missing:
            errors.append('unassigned scenes: ' + ', '.join(missing))
    return errors


def render_md(value: dict[str, Any]) -> str:
    lines = ['# Feature Sequence Plan', '', '[Documentation home](../docs/README.md)', '', f"Project: {value.get('project_title') or 'Untitled'}", '', '| Sequence | Status | Scenes | Runtime | Shard |', '|---|---|---:|---:|---|']
    for rec in value.get('sequences', []):
        runtime = rec.get('estimated_runtime_s')
        rt = '' if runtime is None else f'{runtime:.1f} s'
        lines.append(f"| {rec['sequence_id']} | {rec['status']} | {len(rec['scene_ids'])} | {rt} | `{rec['shard_path']}` |")
    lines += ['', '## Rules', '', '- Work on one sequence at a time unless the task requires a global check.', '- Keep every scene in exactly one active sequence.', '- Set a sequence to `approved` only after its sequence gates pass.', '- Do not use sequence completion as proof that the whole film is complete.', '']
    return '\n'.join(lines)


def init_manifest(root: Path, chunk_size: int, force: bool = False) -> dict[str, Any]:
    path = root / '00_project/sequence_manifest.json'
    if path.exists() and not force:
        value = load_json(path)
        errors = validate_manifest(value, {x['scene_id'] for x in scene_records(root)} or None)
        if errors:
            raise ValueError('; '.join(errors))
        return value
    scenes = scene_records(root)
    if not scenes:
        raise ValueError('02_screenplay/scene_manifest.json has no scenes')
    state = load_json(root / '00_project/state.json', {}) or {}
    value = {
        'schema_version': SCHEMA,
        'project_title': state.get('project_title', 'Untitled'),
        'sequence_size_hint': chunk_size,
        'sequences': make_sequences(scenes, chunk_size),
        'updated_at': now(),
    }
    errors = validate_manifest(value, {x['scene_id'] for x in scenes})
    if errors:
        raise ValueError('; '.join(errors))
    atomic_write_json(path, value)
    atomic_write_text(root / '00_project/sequence_manifest.md', render_md(value))
    return value


def set_status(root: Path, sequence_id: str, status: str, note: str = '') -> dict[str, Any]:
    if status not in SEQ_STATUSES:
        raise ValueError(f'invalid sequence status: {status}')
    path = root / '00_project/sequence_manifest.json'
    value = load_json(path)
    if not isinstance(value, dict):
        raise ValueError('sequence manifest does not exist')
    match = None
    for rec in value.get('sequences', []):
        if rec.get('sequence_id') == sequence_id:
            match = rec
            break
    if match is None:
        raise ValueError(f'unknown sequence: {sequence_id}')
    match['status'] = status
    if note:
        match.setdefault('notes', []).append(note)
    match['updated_at'] = now()
    value['updated_at'] = now()
    atomic_write_json(path, value)
    atomic_write_text(root / '00_project/sequence_manifest.md', render_md(value))
    return match


def next_sequence(value: dict[str, Any]) -> dict[str, Any] | None:
    for status in ('in-production', 'ready', 'planned', 'blocked', 'generated', 'editing'):
        for rec in value.get('sequences', []):
            if rec.get('status') == status:
                return rec
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description='Manage feature-film SEQ-### production boundaries.')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('init')
    p.add_argument('project')
    p.add_argument('--chunk-size', type=int, default=5)
    p.add_argument('--force', action='store_true')
    p = sub.add_parser('validate')
    p.add_argument('project')
    p = sub.add_parser('set')
    p.add_argument('project'); p.add_argument('sequence_id'); p.add_argument('status', choices=sorted(SEQ_STATUSES)); p.add_argument('--note', default='')
    p = sub.add_parser('next')
    p.add_argument('project')
    args = ap.parse_args()
    root = Path(args.project).expanduser().resolve()
    try:
        if args.cmd == 'init':
            value = init_manifest(root, args.chunk_size, args.force)
            print(json.dumps({'sequence_count': len(value['sequences']), 'path': '00_project/sequence_manifest.json'}, indent=2))
        elif args.cmd == 'validate':
            value = load_json(root / '00_project/sequence_manifest.json', {}) or {}
            errors = validate_manifest(value, {x['scene_id'] for x in scene_records(root)} or None)
            if errors:
                for error in errors: print('ERROR', error)
                return 1
            print(f"OK {len(value.get('sequences', []))} sequences")
        elif args.cmd == 'set':
            print(json.dumps(set_status(root, args.sequence_id, args.status, args.note), indent=2))
        elif args.cmd == 'next':
            value = load_json(root / '00_project/sequence_manifest.json', {}) or {}
            print(json.dumps(next_sequence(value), indent=2))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print('ERROR', exc)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
