#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from feature_common import atomic_write_json, atomic_write_text, load_json, load_jsonl, now


def shot_sequence_map(root: Path) -> dict[str, str]:
    seq_doc = load_json(root / '00_project/sequence_manifest.json', {}) or {}
    scene_to_seq = {}
    for seq in seq_doc.get('sequences', []) if isinstance(seq_doc.get('sequences'), list) else []:
        if not isinstance(seq, dict): continue
        for scene in seq.get('scene_ids', []) or []: scene_to_seq[scene] = seq.get('sequence_id', '')
    out = {}
    for shot in load_jsonl(root / '04_generation/shot_briefs.jsonl'):
        sid = shot.get('shot_id'); scene = shot.get('scene_id')
        if isinstance(sid, str) and isinstance(scene, str) and scene in scene_to_seq: out[sid] = scene_to_seq[scene]
    return out


def expected_shots(root: Path) -> set[str]:
    selections = load_json(root / '04_generation/selections.json', {}) or {}
    shots = selections.get('shots', {})
    if not isinstance(shots, dict): return set()
    return {sid for sid, rec in shots.items() if isinstance(sid, str) and sid.startswith('SHOT-') and isinstance(rec, dict) and rec.get('selected_take_id')}


def reconcile(root: Path) -> dict[str, Any]:
    timeline = load_json(root / '05_post/timeline.json', {}) or {}
    events = timeline.get('events', []) if isinstance(timeline.get('events'), list) else []
    mapping = shot_sequence_map(root)
    seq_doc = load_json(root / '00_project/sequence_manifest.json', {}) or {}
    order = {x.get('sequence_id'): x.get('order', 0) for x in seq_doc.get('sequences', []) if isinstance(x, dict)}
    errors: list[str] = []; warnings: list[str] = []
    event_ids = set(); timeline_shots: list[str] = []; placements = []; last_order = -1
    for i, event in enumerate(events, 1):
        if not isinstance(event, dict): errors.append(f'event {i} must be an object'); continue
        eid = event.get('event_id')
        if not isinstance(eid, str) or not eid.startswith('EVT-'): errors.append(f'event {i} has invalid event_id')
        elif eid in event_ids: errors.append(f'duplicate event_id {eid}')
        else: event_ids.add(eid)
        shot = event.get('shot_id')
        seq = mapping.get(shot, '') if isinstance(shot, str) else ''
        if isinstance(shot, str) and shot.startswith('SHOT-'):
            timeline_shots.append(shot)
            if not seq: warnings.append(f'{eid}: {shot} has no sequence mapping')
        if seq:
            seq_order = int(order.get(seq, 0))
            if seq_order < last_order and not event.get('editorial_order_override', False):
                errors.append(f'{eid}: sequence order moves backward to {seq} without editorial_order_override')
            last_order = max(last_order, seq_order) if not event.get('editorial_order_override', False) else seq_order
        placements.append({'event_id': eid, 'shot_id': shot or '', 'sequence_id': seq, 'duration': event.get('duration'), 'media_id': event.get('media_id', ''), 'source_id': event.get('source_id', '')})
    expected = expected_shots(root)
    present = set(timeline_shots)
    missing = sorted(expected - present)
    duplicate_shots = sorted({x for x in timeline_shots if timeline_shots.count(x) > 1})
    for shot in missing: errors.append(f'selected shot missing from main timeline: {shot}')
    for shot in duplicate_shots: warnings.append(f'shot appears more than once in main timeline: {shot}')
    by_seq: dict[str, dict[str, Any]] = {}
    for seq_id in order:
        seq_events = [x for x in placements if x['sequence_id'] == seq_id]
        by_seq[seq_id] = {'event_count': len(seq_events), 'duration_s': round(sum(float(x['duration'] or 0) for x in seq_events), 3), 'shot_ids': [x['shot_id'] for x in seq_events if x['shot_id']]}
    return {
        'schema_version': 1,
        'ready': not errors,
        'timeline_id': timeline.get('timeline_id', ''),
        'event_count': len(events),
        'selected_shot_count': len(expected),
        'timeline_shot_count': len(timeline_shots),
        'missing_selected_shots': missing,
        'duplicate_shots': duplicate_shots,
        'sequences': by_seq,
        'placements': placements,
        'errors': errors,
        'warnings': warnings,
        'generated_at': now(),
    }


def render_md(report: dict[str, Any]) -> str:
    lines = ['# Feature Editorial Reconciliation', '', '[Editorial guide](../../docs/postproduction/editorial.md) | [Documentation home](../../docs/README.md)', '', f"Ready: **{'YES' if report['ready'] else 'NO'}**", '', f"Timeline events: {report['event_count']}", f"Selected shots expected: {report['selected_shot_count']}", f"Shot placements found: {report['timeline_shot_count']}", '', '## Sequence summary', '', '| Sequence | Events | Duration |', '|---|---:|---:|']
    for seq, rec in report['sequences'].items(): lines.append(f"| {seq} | {rec['event_count']} | {rec['duration_s']:.2f} s |")
    lines += ['', '## Errors', ''] + ([f'- {x}' for x in report['errors']] or ['- None.'])
    lines += ['', '## Warnings', ''] + ([f'- {x}' for x in report['warnings']] or ['- None.'])
    lines += ['', '## Rule', '', 'Reconcile each sequence before the global film master. A selected shot must not disappear from the final timeline without an explicit editorial decision.', '']
    return '\n'.join(lines)


def main() -> int:
    ap=argparse.ArgumentParser(description='Reconcile a feature timeline against approved sequence and shot state.'); ap.add_argument('project'); ap.add_argument('--strict',action='store_true'); a=ap.parse_args(); root=Path(a.project).expanduser().resolve()
    try:
        report=reconcile(root); atomic_write_json(root/'05_post/editorial/reconciliation.json',report); atomic_write_text(root/'05_post/editorial/reconciliation.md',render_md(report))
    except Exception as exc: print('ERROR',exc); return 1
    print(json.dumps(report,indent=2)); return 1 if a.strict and not report['ready'] else 0

if __name__=='__main__': raise SystemExit(main())
