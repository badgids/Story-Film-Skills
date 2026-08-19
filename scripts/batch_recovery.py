#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from feature_common import atomic_write_json, atomic_write_text, load_json, now


def build_retry(root: Path, retry_failed_only: bool = True) -> dict[str, Any]:
    batch = load_json(root / '04_generation/comfyui/offline_batch.json', {}) or {}
    result = load_json(root / '04_generation/comfyui/offline_batch_result.json', {}) or {}
    jobs = batch.get('jobs', []) if isinstance(batch.get('jobs'), list) else []
    result_jobs = result.get('jobs', []) if isinstance(result.get('jobs'), list) else []
    status = {x.get('job_id'): x.get('status') for x in result_jobs if isinstance(x, dict)}
    complete = {jid for jid, st in status.items() if st == 'complete'}
    failed = {jid for jid, st in status.items() if st == 'failed'}
    # A batch that stopped before recording the current failure may name it in
    # failed_job_id. Keep that record in the recovery frontier.
    if isinstance(result.get('failed_job_id'), str): failed.add(result['failed_job_id'])
    all_ids = {x.get('job_id') for x in jobs if isinstance(x, dict)}
    pending = {x for x in all_ids if x and x not in complete}
    target = set(failed or pending) if retry_failed_only else pending
    # Include downstream jobs that cannot be trusted because they depend on a
    # retried job. Completed upstream jobs stay complete and are not regenerated.
    changed = True
    while changed:
        changed = False
        for job in jobs:
            jid = job.get('job_id')
            if jid in target: continue
            if any(dep in target for dep in job.get('blocked_by', [])):
                target.add(jid); changed = True
    retry_jobs = []
    for job in jobs:
        jid = job.get('job_id')
        if jid not in target: continue
        rec = copy.deepcopy(job)
        rec['blocked_by'] = [dep for dep in rec.get('blocked_by', []) if dep in target]
        retry_jobs.append(rec)
    if not retry_jobs:
        raise ValueError('no failed or pending jobs need recovery')
    retry = {
        'schema_version': 1,
        'batch_id': batch.get('batch_id', 'BATCH-000'),
        'recovery_id': f"RECOVERY-{now().replace(':','').replace('-','').replace('+','_')}",
        'status': 'prepared',
        'sequential': True,
        'uploads': batch.get('uploads', []),
        'staged_uploads': batch.get('staged_uploads', {}),
        'jobs': retry_jobs,
        'preserved_complete_jobs': sorted(complete - target),
        'recovered_from_status': result.get('status', 'unknown'),
        'generated_at': now(),
    }
    return retry


def render_md(retry: dict[str, Any]) -> str:
    lines = ['# Partial Batch Recovery Plan', '', '[Resource-safe generation](../../../docs/generation/resource-safe.md) | [Documentation home](../../../docs/README.md)', '', f"Original batch: `{retry['batch_id']}`", f"Jobs to run again: {len(retry['jobs'])}", f"Completed jobs kept: {len(retry['preserved_complete_jobs'])}", '', '## Retry jobs', '']
    lines.extend(f"- `{x['job_id']}`" for x in retry['jobs'])
    lines += ['', '## Completed jobs that stay valid', '']
    lines.extend([f'- `{x}`' for x in retry['preserved_complete_jobs']] or ['- None.'])
    lines += ['', '## Rule', '', 'Do not regenerate a completed upstream job unless its artifact changed or its result was invalidated. Re-run a downstream job when it depends on a job that you retry.', '']
    return '\n'.join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description='Create a minimal retry batch from a partial ComfyUI failure.')
    ap.add_argument('project')
    ap.add_argument('--all-pending', action='store_true')
    args = ap.parse_args(); root = Path(args.project).expanduser().resolve()
    try:
        retry = build_retry(root, not args.all_pending)
        atomic_write_json(root / '04_generation/comfyui/recovery_batch.json', retry)
        atomic_write_text(root / '04_generation/comfyui/recovery_batch.md', render_md(retry))
    except Exception as exc:
        print('ERROR', exc); return 1
    print(json.dumps({'jobs': [x['job_id'] for x in retry['jobs']], 'preserved': retry['preserved_complete_jobs']}, indent=2))
    return 0

if __name__ == '__main__': raise SystemExit(main())
