#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from feature_common import atomic_write_json, atomic_write_text, load_json, now
from production_health import gather as health_gather
from editorial_reconcile import reconcile as editorial_reconcile

REQUIRED_CONTROL = [
    '00_project/state.json', '00_project/canon.json', '00_project/sequence_manifest.json',
    '02_screenplay/screenplay.fountain', '02_screenplay/scene_manifest.json', '02_screenplay/line_manifest.jsonl',
    '03_preproduction/production_coverage.json', '04_generation/selections.json', '00_project/media_approvals.json',
    '05_post/timeline.json', '05_post/masters/film_audio_master.wav', '05_post/masters/film_master.mp4',
    '05_post/editorial/reconciliation.json', '06_release/delivery_qc.json', '06_release/release_manifest.json',
]


def probe_master(path: Path) -> dict[str, Any]:
    if not path.is_file(): return {'exists': False}
    result: dict[str, Any] = {'exists': True, 'size_bytes': path.stat().st_size}
    ffprobe = shutil.which('ffprobe')
    if not ffprobe: return result
    p = subprocess.run([ffprobe, '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,codec_name,width,height', '-of', 'json', str(path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode == 0:
        try: result['ffprobe'] = json.loads(p.stdout)
        except json.JSONDecodeError: result['ffprobe_error'] = 'invalid JSON from ffprobe'
    else: result['ffprobe_error'] = p.stderr.strip()[-1000:]
    return result


def audit(root: Path) -> dict[str, Any]:
    blockers: list[str] = []; warnings: list[str] = []
    missing = [rel for rel in REQUIRED_CONTROL if not (root / rel).is_file()]
    blockers.extend(f'missing required final artifact: {x}' for x in missing)

    seq = load_json(root / '00_project/sequence_manifest.json', {}) or {}
    seqs = [x for x in seq.get('sequences', []) if isinstance(x, dict)]
    not_approved = [x.get('sequence_id') for x in seqs if x.get('status') not in {'approved', 'retired'}]
    if not_approved: blockers.append('sequences not approved: ' + ', '.join(str(x) for x in not_approved))

    coverage = load_json(root / '03_preproduction/production_coverage.json', {}) or {}
    if coverage.get('ready') is not True: blockers.append('production coverage is not ready')

    continuity = load_json(root / '03_preproduction/continuity/long_range_report.json', {}) or {}
    if continuity and continuity.get('ready') is not True: blockers.append('long-range continuity is not ready')
    elif not continuity: warnings.append('long-range continuity report does not exist')

    editorial = load_json(root / '05_post/editorial/reconciliation.json', {}) or {}
    if not editorial and (root / '05_post/timeline.json').is_file():
        editorial = editorial_reconcile(root)
    if editorial.get('ready') is not True: blockers.append('feature editorial reconciliation is not ready')

    delivery = load_json(root / '06_release/delivery_qc.json', {}) or {}
    # Delivery schemas can vary by target. Treat any explicit blocker/fail as blocking.
    if delivery:
        text = json.dumps(delivery).lower()
        if '"status": "fail"' in text or '"ready": false' in text or '"blocking": true' in text:
            blockers.append('delivery QC contains a blocking failure')

    release = load_json(root / '06_release/release_manifest.json', {}) or {}
    if release and release.get('ready') is False: blockers.append('release manifest is not ready')

    batch = load_json(root / '04_generation/comfyui/offline_batch_result.json', {}) or {}
    if batch.get('status') == 'failed': blockers.append('offline ComfyUI batch has failed jobs')

    state = load_json(root / '00_project/state.json', {}) or {}
    stale = [k for k, v in (state.get('artifacts') or {}).items() if isinstance(v, dict) and v.get('status') == 'stale']
    if stale: blockers.append('stale downstream artifacts remain: ' + ', '.join(stale))

    progress = load_json(root / '00_project/pipeline_progress.json', {}) or {}
    if progress.get('status') == 'blocked': blockers.append('pipeline progress is blocked')

    resource = load_json(root / '00_project/resource_handoff.json', {}) or {}
    if resource.get('phase') in {'failed', 'waiting-for-agent-end', 'unloading-llm', 'running-comfyui', 'unloading-comfyui', 'reloading-llm'}:
        blockers.append(f"resource handoff is not settled: {resource.get('phase')}")

    try:
        from document_companions import audit_project
        companion_problems = audit_project(root)
    except Exception as exc:
        companion_problems = [f'companion audit failed: {exc}']
    if companion_problems: blockers.append(f'{len(companion_problems)} rich-document companion problem(s) remain')

    master = probe_master(root / '05_post/masters/film_master.mp4')
    if master.get('exists') and master.get('size_bytes', 0) <= 0: blockers.append('film master is empty')
    ff = master.get('ffprobe')
    if isinstance(ff, dict):
        streams = ff.get('streams', []) if isinstance(ff.get('streams'), list) else []
        if not any(x.get('codec_type') == 'video' for x in streams if isinstance(x, dict)): blockers.append('film master has no video stream')
        if not any(x.get('codec_type') == 'audio' for x in streams if isinstance(x, dict)): warnings.append('film master has no audio stream')

    health = health_gather(root)
    if health.get('status') == 'blocked': warnings.append('production health report also reports blockers; see 00_project/health_report.md')

    return {
        'schema_version': 1,
        'complete': not blockers,
        'blockers': blockers,
        'warnings': warnings,
        'missing_required_artifacts': missing,
        'sequence_total': len(seqs),
        'sequence_not_approved': not_approved,
        'master_probe': master,
        'generated_at': now(),
        'statement': 'A complete=true result means the deterministic completion gates passed. It does not prove artistic quality or audience success.',
    }


def render_md(report: dict[str, Any]) -> str:
    lines = ['# Final Film Completeness Audit', '', '[Finish and release guide](../docs/release/completion.md) | [Documentation home](../docs/README.md)', '', f"Complete: **{'YES' if report['complete'] else 'NO'}**", '', f"Sequences checked: {report['sequence_total']}", '', '## Blockers', '']
    lines += [f'- {x}' for x in report['blockers']] or ['- None.']
    lines += ['', '## Warnings', ''] + ([f'- {x}' for x in report['warnings']] or ['- None.'])
    lines += ['', '## What this result means', '', report['statement'], '', 'Do not call the project a completed film until this audit reports `Complete: YES` and the user accepts the final creative result.', '']
    return '\n'.join(lines)


def main() -> int:
    ap=argparse.ArgumentParser(description='Audit whether a Story-Film project has all required feature-film completion evidence.'); ap.add_argument('project'); ap.add_argument('--strict',action='store_true'); a=ap.parse_args(); root=Path(a.project).expanduser().resolve()
    try:
        report=audit(root); atomic_write_json(root/'06_release/completeness_audit.json',report); atomic_write_text(root/'06_release/completeness_audit.md',render_md(report))
    except Exception as exc: print('ERROR',exc); return 1
    print(json.dumps(report,indent=2)); return 1 if a.strict and not report['complete'] else 0

if __name__=='__main__': raise SystemExit(main())
