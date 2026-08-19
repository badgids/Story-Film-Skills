#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from feature_common import atomic_write_json, atomic_write_text, load_json, load_jsonl, now

ALLOWED_KINDS = {'character-state', 'prop-state', 'costume', 'injury', 'knowledge', 'relationship', 'location-state', 'weather', 'time', 'visual', 'audio', 'promise', 'custom'}


def validate_anchor(rec: dict[str, Any], sequence_ids: set[str]) -> list[str]:
    errors = []
    aid = rec.get('anchor_id')
    if not isinstance(aid, str) or not aid.startswith('CONT-'):
        errors.append(f'invalid anchor_id {aid!r}')
    if rec.get('kind') not in ALLOWED_KINDS:
        errors.append(f'{aid}: invalid kind {rec.get("kind")!r}')
    if not isinstance(rec.get('subject_id'), str) or not rec.get('subject_id'):
        errors.append(f'{aid}: subject_id is required')
    source = rec.get('source_sequence')
    if source not in sequence_ids:
        errors.append(f'{aid}: unknown source_sequence {source!r}')
    targets = rec.get('target_sequences')
    if not isinstance(targets, list) or not targets:
        errors.append(f'{aid}: target_sequences must be a non-empty array')
    else:
        for seq in targets:
            if seq not in sequence_ids:
                errors.append(f'{aid}: unknown target sequence {seq!r}')
    if 'expected_state' not in rec:
        errors.append(f'{aid}: expected_state is required')
    return errors


def audit(root: Path) -> dict[str, Any]:
    seq_doc = load_json(root / '00_project/sequence_manifest.json', {}) or {}
    sequences = [x for x in seq_doc.get('sequences', []) if isinstance(x, dict)]
    seq_ids = {x.get('sequence_id') for x in sequences if isinstance(x.get('sequence_id'), str)}
    order = {x.get('sequence_id'): x.get('order', 0) for x in sequences}
    anchors = load_jsonl(root / '03_preproduction/continuity/anchors.jsonl')
    observations = load_jsonl(root / '03_preproduction/continuity/observations.jsonl')
    errors: list[str] = []
    for rec in anchors:
        errors.extend(validate_anchor(rec, seq_ids))
    obs_by_pair: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for obs in observations:
        aid = obs.get('anchor_id')
        seq = obs.get('sequence_id')
        if not isinstance(aid, str) or not aid.startswith('CONT-'):
            errors.append(f'observation has invalid anchor_id {aid!r}')
            continue
        if seq not in seq_ids:
            errors.append(f'{aid}: observation has unknown sequence {seq!r}')
            continue
        obs_by_pair[(aid, seq)].append(obs)

    conflicts: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    distance_checks: list[dict[str, Any]] = []
    for anchor in anchors:
        aid = anchor.get('anchor_id', '')
        expected = anchor.get('expected_state')
        source = anchor.get('source_sequence')
        for target in anchor.get('target_sequences') or []:
            distance = abs(int(order.get(target, 0)) - int(order.get(source, 0)))
            pair_obs = obs_by_pair.get((aid, target), [])
            distance_checks.append({'anchor_id': aid, 'source_sequence': source, 'target_sequence': target, 'sequence_distance': distance, 'observations': len(pair_obs)})
            if not pair_obs:
                missing.append({'anchor_id': aid, 'sequence_id': target, 'subject_id': anchor.get('subject_id'), 'expected_state': expected, 'sequence_distance': distance})
                continue
            for obs in pair_obs:
                if obs.get('observed_state') != expected and not obs.get('intentional_change', False):
                    conflicts.append({
                        'anchor_id': aid,
                        'subject_id': anchor.get('subject_id'),
                        'source_sequence': source,
                        'target_sequence': target,
                        'expected_state': expected,
                        'observed_state': obs.get('observed_state'),
                        'sequence_distance': distance,
                        'evidence': obs.get('evidence', ''),
                    })
    ready = not errors and not conflicts and not missing
    return {
        'schema_version': 1,
        'ready': ready,
        'anchor_count': len(anchors),
        'observation_count': len(observations),
        'errors': errors,
        'conflicts': conflicts,
        'missing_observations': missing,
        'distance_checks': distance_checks,
        'generated_at': now(),
    }


def render_md(report: dict[str, Any]) -> str:
    lines = ['# Long-Range Continuity Report', '', '[Feature-scale guide](../../docs/production/feature-scale.md) | [Documentation home](../../docs/README.md)', '', f"Ready: **{'YES' if report['ready'] else 'NO'}**", '', f"Anchors: {report['anchor_count']}", f"Observations: {report['observation_count']}", '']
    lines += ['## Conflicts', '']
    if report['conflicts']:
        for item in report['conflicts']:
            lines.append(f"- `{item['anchor_id']}`: `{item['subject_id']}` expected `{item['expected_state']}` in `{item['target_sequence']}`, but observed `{item['observed_state']}`.")
    else:
        lines.append('- None.')
    lines += ['', '## Missing checks', '']
    if report['missing_observations']:
        for item in report['missing_observations']:
            lines.append(f"- `{item['anchor_id']}` needs an observation in `{item['sequence_id']}`. Distance: {item['sequence_distance']} sequence(s).")
    else:
        lines.append('- None.')
    if report['errors']:
        lines += ['', '## Data errors', ''] + [f'- {x}' for x in report['errors']]
    lines += ['', '## Rule', '', 'Use long-range anchors for facts that must survive across non-adjacent sequences. Record an intentional change when the story changes the state on purpose.', '']
    return '\n'.join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description='Check continuity facts across distant feature-film sequences.')
    ap.add_argument('project')
    ap.add_argument('--strict', action='store_true')
    args = ap.parse_args()
    root = Path(args.project).expanduser().resolve()
    try:
        report = audit(root)
        atomic_write_json(root / '03_preproduction/continuity/long_range_report.json', report)
        atomic_write_text(root / '03_preproduction/continuity/long_range_report.md', render_md(report))
    except Exception as exc:
        print('ERROR', exc)
        return 1
    print(json.dumps(report, indent=2))
    return 1 if args.strict and not report['ready'] else 0

if __name__ == '__main__':
    raise SystemExit(main())
