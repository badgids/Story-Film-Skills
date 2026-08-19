#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from feature_common import append_jsonl, atomic_write_json, atomic_write_text, load_json, now, sha256_file

CONTROL_FILES = [
    '00_project/state.json',
    '00_project/canon.json',
    '00_project/pipeline_progress.json',
    '00_project/sequence_manifest.json',
    '00_project/work_units.json',
    '00_project/resource_handoff.json',
    '04_generation/comfyui/offline_batch.json',
    '04_generation/comfyui/offline_batch_result.json',
    '04_generation/generation_schedule.json',
    '04_generation/selections.json',
    '00_project/media_approvals.json',
    '05_post/timeline.json',
]
ACTIVE_RESOURCE_PHASES = {'waiting-for-agent-end', 'unloading-llm', 'running-comfyui', 'unloading-comfyui', 'reloading-llm'}


def snapshot(root: Path, note: str = '') -> dict[str, Any]:
    files = {}
    for rel in CONTROL_FILES:
        path = root / rel
        files[rel] = {'exists': path.is_file(), 'sha256': sha256_file(path) if path.is_file() else None}
    progress = load_json(root / '00_project/pipeline_progress.json', {}) or {}
    sequences = load_json(root / '00_project/sequence_manifest.json', {}) or {}
    resource = load_json(root / '00_project/resource_handoff.json', {}) or {}
    current_seq = ''
    for rec in sequences.get('sequences', []) if isinstance(sequences.get('sequences'), list) else []:
        if isinstance(rec, dict) and rec.get('status') in {'in-production', 'blocked', 'editing'}:
            current_seq = rec.get('sequence_id', ''); break
    stamp = now()
    checkpoint = {
        'schema_version': 1,
        'checkpoint_id': 'CP-' + ''.join(ch for ch in stamp if ch.isdigit())[:17],
        'created_at': stamp,
        'note': note,
        'pipeline_status': progress.get('status', 'unknown'),
        'pipeline_cursor': progress.get('cursor', {}),
        'next_action': progress.get('next_action', ''),
        'current_sequence_id': current_seq,
        'resource_phase': resource.get('phase', 'idle'),
        'resource_job_id': resource.get('current_job_id', ''),
        'control_files': files,
    }
    atomic_write_json(root / '00_project/recovery/checkpoint.json', checkpoint)
    append_jsonl(root / '00_project/recovery/journal.jsonl', {'event': 'checkpoint', 'checkpoint_id': checkpoint['checkpoint_id'], 'created_at': stamp, 'note': note})
    atomic_write_text(root / '00_project/recovery/checkpoint.md', render_checkpoint(checkpoint))
    return checkpoint


def compare(root: Path, cp: dict[str, Any]) -> list[dict[str, Any]]:
    changes = []
    for rel, old in (cp.get('control_files') or {}).items():
        path = root / rel
        exists = path.is_file()
        current = sha256_file(path) if exists else None
        if exists != old.get('exists') or current != old.get('sha256'):
            changes.append({'path': rel, 'checkpoint_exists': old.get('exists'), 'current_exists': exists, 'checkpoint_sha256': old.get('sha256'), 'current_sha256': current})
    return changes


def resume_report(root: Path) -> dict[str, Any]:
    cp = load_json(root / '00_project/recovery/checkpoint.json', {}) or {}
    if not cp:
        raise ValueError('no recovery checkpoint exists')
    changes = compare(root, cp)
    progress = load_json(root / '00_project/pipeline_progress.json', {}) or {}
    resource = load_json(root / '00_project/resource_handoff.json', {}) or {}
    resource_phase = resource.get('phase', 'idle')
    if resource_phase in ACTIVE_RESOURCE_PHASES:
        mode = 'resource-interrupted'
        next_action = 'Inspect the ComfyUI queue and resource_handoff.json. Do not assume the old runner survived the reboot. Release or re-arm resources before normal model work.'
    elif changes:
        mode = 'dirty'
        next_action = 'Review changed control files before continuing. Create a new checkpoint only after the changes are understood.'
    else:
        mode = 'exact'
        next_action = progress.get('next_action') or cp.get('next_action') or 'Continue the recorded pipeline target.'
    report = {
        'schema_version': 1,
        'resume_mode': mode,
        'checkpoint_id': cp.get('checkpoint_id', ''),
        'checkpoint_created_at': cp.get('created_at', ''),
        'recorded_cursor': cp.get('pipeline_cursor', {}),
        'current_cursor': progress.get('cursor', {}),
        'current_sequence_id': cp.get('current_sequence_id', ''),
        'resource_phase': resource_phase,
        'resource_job_id': resource.get('current_job_id', ''),
        'changed_control_files': changes,
        'next_action': next_action,
        'generated_at': now(),
    }
    atomic_write_json(root / '00_project/recovery/resume_report.json', report)
    atomic_write_text(root / '00_project/recovery/RECOVERY_RESUME.md', render_resume(report))
    append_jsonl(root / '00_project/recovery/journal.jsonl', {'event': 'resume-check', 'checkpoint_id': report['checkpoint_id'], 'resume_mode': mode, 'created_at': now()})
    return report


def render_checkpoint(cp: dict[str, Any]) -> str:
    return '\n'.join([
        '# Recovery Checkpoint', '',
        '[Recovery guide](../../docs/operations/recovery.md) | [Documentation home](../../docs/README.md)', '',
        f"Checkpoint: `{cp.get('checkpoint_id')}`", f"Created: {cp.get('created_at')}", f"Current sequence: `{cp.get('current_sequence_id') or 'none'}`", f"Pipeline target: `{(cp.get('pipeline_cursor') or {}).get('target_id', 'none')}`", f"Resource phase: `{cp.get('resource_phase')}`", '',
        'This checkpoint records control state. It does not copy large media files.', ''
    ])


def render_resume(report: dict[str, Any]) -> str:
    lines = ['# Recovery Resume', '', '[Recovery guide](../../docs/operations/recovery.md) | [Documentation home](../../docs/README.md)', '', f"Resume mode: **{report['resume_mode']}**", '', f"Checkpoint: `{report['checkpoint_id']}`", f"Current sequence: `{report['current_sequence_id'] or 'none'}`", f"Current pipeline target: `{(report.get('current_cursor') or {}).get('target_id', 'none')}`", f"Resource phase: `{report['resource_phase']}`", '', '## Changed control files', '']
    if report['changed_control_files']:
        lines.extend(f"- `{x['path']}`" for x in report['changed_control_files'])
    else:
        lines.append('- None.')
    lines += ['', '## Next action', '', report['next_action'], '', 'Do not reconstruct progress from memory. Use the recorded durable state.', '']
    return '\n'.join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description='Checkpoint and recover Story-Film control state across a machine reboot.')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('checkpoint'); p.add_argument('project'); p.add_argument('--note', default='')
    p = sub.add_parser('resume'); p.add_argument('project'); p.add_argument('--strict', action='store_true')
    args = ap.parse_args(); root = Path(args.project).expanduser().resolve()
    try:
        if args.cmd == 'checkpoint':
            print(json.dumps(snapshot(root, args.note), indent=2)); return 0
        report = resume_report(root); print(json.dumps(report, indent=2))
        return 1 if args.strict and report['resume_mode'] != 'exact' else 0
    except Exception as exc:
        print('ERROR', exc); return 1

if __name__ == '__main__': raise SystemExit(main())
