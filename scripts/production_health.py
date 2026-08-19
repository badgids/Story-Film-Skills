#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from feature_common import atomic_write_json, atomic_write_text, load_json, load_jsonl, now


def _count_status(records: list[dict[str, Any]], field: str = 'status') -> dict[str, int]:
    counts: dict[str, int] = {}
    for rec in records:
        value = str(rec.get(field) or 'unknown')
        counts[value] = counts.get(value, 0) + 1
    return counts


def gather(root: Path) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    facts: dict[str, Any] = {}

    state = load_json(root / '00_project/state.json', {}) or {}
    artifacts = state.get('artifacts', {}) if isinstance(state.get('artifacts'), dict) else {}
    stale = sorted(k for k, v in artifacts.items() if isinstance(v, dict) and v.get('status') == 'stale')
    draft = sorted(k for k, v in artifacts.items() if isinstance(v, dict) and v.get('status') in {'draft', 'blocked'})
    if stale:
        blockers.append(f'{len(stale)} artifact records are stale')
    if draft:
        warnings.append(f'{len(draft)} artifact records are draft or blocked')
    facts['artifact_status'] = {'stale': stale, 'draft_or_blocked': draft, 'tracked': len(artifacts)}

    seq = load_json(root / '00_project/sequence_manifest.json', {}) or {}
    seqs = seq.get('sequences', []) if isinstance(seq.get('sequences'), list) else []
    seq_counts = _count_status([x for x in seqs if isinstance(x, dict)])
    blocked_seq = [x.get('sequence_id') for x in seqs if isinstance(x, dict) and x.get('status') == 'blocked']
    if blocked_seq:
        blockers.append('blocked sequences: ' + ', '.join(str(x) for x in blocked_seq))
    facts['sequences'] = {'total': len(seqs), 'status_counts': seq_counts, 'blocked': blocked_seq}

    progress = load_json(root / '00_project/pipeline_progress.json', {}) or {}
    if progress.get('status') == 'blocked':
        blockers.append('pipeline progress is blocked')
    facts['pipeline'] = {
        'status': progress.get('status', 'unknown'),
        'target': (progress.get('cursor') or {}).get('target_id', ''),
        'next_action': progress.get('next_action', ''),
        'blocker': progress.get('blocker', ''),
    }

    resource = load_json(root / '00_project/resource_handoff.json', {}) or {}
    if resource.get('phase') == 'failed':
        blockers.append('resource-safe generation is in failed state')
    facts['resource_handoff'] = {
        'phase': resource.get('phase', 'unknown'),
        'job_index': resource.get('job_index', 0),
        'job_total': resource.get('job_total', 0),
        'current_job_id': resource.get('current_job_id', ''),
        'error': resource.get('error', ''),
    }

    batch_result = load_json(root / '04_generation/comfyui/offline_batch_result.json', {}) or {}
    jobs = batch_result.get('jobs', []) if isinstance(batch_result.get('jobs'), list) else []
    failed_jobs = [x.get('job_id') for x in jobs if isinstance(x, dict) and x.get('status') == 'failed']
    if failed_jobs:
        blockers.append('failed generation jobs: ' + ', '.join(str(x) for x in failed_jobs))
    facts['generation'] = {'result_jobs': len(jobs), 'failed_jobs': failed_jobs, 'status_counts': _count_status([x for x in jobs if isinstance(x, dict)])}

    coverage = load_json(root / '03_preproduction/production_coverage.json', {}) or {}
    if coverage:
        ready = coverage.get('ready')
        if ready is False:
            blockers.append('production coverage is not ready')
        facts['production_coverage'] = {'ready': ready, 'totals': coverage.get('totals', {})}

    editorial = load_json(root / '05_post/editorial/reconciliation.json', {}) or {}
    if editorial:
        if editorial.get('ready') is False:
            blockers.append('editorial reconciliation is not ready')
        facts['editorial'] = {'ready': editorial.get('ready'), 'errors': len(editorial.get('errors', []) or []), 'warnings': len(editorial.get('warnings', []) or [])}

    continuity = load_json(root / '03_preproduction/continuity/long_range_report.json', {}) or {}
    if continuity:
        if continuity.get('ready') is False:
            blockers.append('long-range continuity has unresolved conflicts')
        facts['long_range_continuity'] = {'ready': continuity.get('ready'), 'conflicts': len(continuity.get('conflicts', []) or [])}

    docs_missing = []
    try:
        from document_companions import audit_project
        docs_missing = audit_project(root)
    except Exception as exc:
        warnings.append(f'document companion audit could not run: {exc}')
    if docs_missing:
        blockers.append(f'{len(docs_missing)} rich-document companion problems')
    facts['document_companions'] = {'problems': docs_missing}

    if blockers:
        status = 'blocked'
    elif warnings:
        status = 'attention'
    else:
        status = 'healthy'
    return {
        'schema_version': 1,
        'status': status,
        'blockers': blockers,
        'warnings': warnings,
        'facts': facts,
        'generated_at': now(),
    }


def render_md(report: dict[str, Any]) -> str:
    lines = ['# Production Health Report', '', '[Feature-scale guide](../docs/production/feature-scale.md) | [Documentation home](../docs/README.md)', '', f"Overall status: **{report['status'].upper()}**", '']
    lines += ['## Blockers', '']
    if report['blockers']:
        lines.extend(f'- {x}' for x in report['blockers'])
    else:
        lines.append('- None.')
    lines += ['', '## Warnings', '']
    if report['warnings']:
        lines.extend(f'- {x}' for x in report['warnings'])
    else:
        lines.append('- None.')
    seq = report['facts'].get('sequences', {})
    lines += ['', '## Sequence status', '', f"Total sequences: {seq.get('total', 0)}", '']
    for key, value in sorted((seq.get('status_counts') or {}).items()):
        lines.append(f'- {key}: {value}')
    pipe = report['facts'].get('pipeline', {})
    lines += ['', '## Current pipeline position', '', f"Status: `{pipe.get('status', 'unknown')}`", f"Target: `{pipe.get('target') or 'none'}`", f"Next action: {pipe.get('next_action') or 'none'}", '']
    lines += ['## Meaning', '', '- `healthy` means no known deterministic blocker was found.', '- `attention` means work can continue, but warnings need review.', '- `blocked` means at least one known gate must be repaired before a completion claim.', '- This report does not judge artistic quality.', '']
    return '\n'.join(lines)


def write_report(root: Path) -> dict[str, Any]:
    report = gather(root)
    atomic_write_json(root / '00_project/health_report.json', report)
    atomic_write_text(root / '00_project/health_report.md', render_md(report))
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description='Create a deterministic Story-Film production health report.')
    ap.add_argument('project')
    ap.add_argument('--strict', action='store_true', help='Exit nonzero when status is blocked.')
    args = ap.parse_args()
    root = Path(args.project).expanduser().resolve()
    try:
        report = write_report(root)
    except Exception as exc:
        print('ERROR', exc)
        return 1
    print(json.dumps(report, indent=2))
    return 1 if args.strict and report['status'] == 'blocked' else 0

if __name__ == '__main__':
    raise SystemExit(main())
