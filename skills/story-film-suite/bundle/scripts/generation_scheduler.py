#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from feature_common import atomic_write_json, atomic_write_text, load_json, now

DEFAULT_PROFILES = {
    'image': {'vram_gib': 12.0, 'ram_gib': 8.0, 'exclusive_gpu': True, 'estimated_seconds_per_job': 30.0, 'resident_group': 'image'},
    'video': {'vram_gib': 22.0, 'ram_gib': 20.0, 'exclusive_gpu': True, 'estimated_seconds_per_job': 180.0, 'resident_group': 'video'},
    'audio': {'vram_gib': 10.0, 'ram_gib': 8.0, 'exclusive_gpu': True, 'estimated_seconds_per_job': 45.0, 'resident_group': 'audio'},
    'cpu': {'vram_gib': 0.0, 'ram_gib': 4.0, 'exclusive_gpu': False, 'estimated_seconds_per_job': 30.0, 'resident_group': 'cpu'},
}


def infer_kind(job: dict[str, Any]) -> str:
    profile = job.get('resource_profile')
    if isinstance(profile, str) and profile:
        return profile
    kinds = [str(x).lower() for x in job.get('expected_output_kinds', []) if isinstance(x, str)]
    if any('video' in x for x in kinds): return 'video'
    if any(x in {'audio', 'voice', 'music', 'sfx', 'sound'} for x in kinds): return 'audio'
    if any(x in {'image', 'still', 'frame'} for x in kinds): return 'image'
    return 'image'


def normalize_profiles(value: dict[str, Any]) -> dict[str, dict[str, Any]]:
    profiles = dict(DEFAULT_PROFILES)
    supplied = value.get('profiles') if isinstance(value, dict) else None
    if isinstance(supplied, dict):
        for key, rec in supplied.items():
            if isinstance(rec, dict):
                merged = dict(profiles.get(key, {})); merged.update(rec); profiles[key] = merged
    return profiles


def validate_resources(value: dict[str, Any]) -> list[str]:
    errors = []
    machine = value.get('machine', {}) if isinstance(value, dict) else {}
    for field in ('vram_gib', 'ram_gib'):
        val = machine.get(field)
        if not isinstance(val, (int, float)) or val <= 0:
            errors.append(f'machine.{field} must be a positive number')
    for name, rec in normalize_profiles(value).items():
        for field in ('vram_gib', 'ram_gib', 'estimated_seconds_per_job'):
            if not isinstance(rec.get(field), (int, float)) or rec[field] < 0:
                errors.append(f'profile {name}.{field} must be a non-negative number')
    return errors


def build(root: Path) -> dict[str, Any]:
    resources = load_json(root / '04_generation/generation_resources.json', {}) or {}
    errors = validate_resources(resources)
    if errors:
        raise ValueError('; '.join(errors))
    batch = load_json(root / '04_generation/comfyui/offline_batch.json', {}) or {}
    jobs = batch.get('jobs', []) if isinstance(batch.get('jobs'), list) else []
    if not jobs:
        raise ValueError('offline batch has no jobs')
    profiles = normalize_profiles(resources)
    machine = resources['machine']
    vram_cap = float(machine['vram_gib']) - float(machine.get('vram_reserve_gib', 1.0))
    ram_cap = float(machine['ram_gib']) - float(machine.get('ram_reserve_gib', 4.0))
    if vram_cap <= 0 or ram_cap <= 0:
        raise ValueError('machine reserve leaves no usable memory')

    planned = []
    blockers = []
    group_order: list[str] = []
    for job in jobs:
        kind = infer_kind(job)
        if kind not in profiles:
            blockers.append(f"{job.get('job_id')}: unknown resource profile {kind}")
            continue
        p = profiles[kind]
        if float(p.get('vram_gib', 0)) > vram_cap:
            blockers.append(f"{job.get('job_id')}: profile {kind} needs {p.get('vram_gib')} GiB VRAM, usable limit is {vram_cap:.2f} GiB")
        if float(p.get('ram_gib', 0)) > ram_cap:
            blockers.append(f"{job.get('job_id')}: profile {kind} needs {p.get('ram_gib')} GiB RAM, usable limit is {ram_cap:.2f} GiB")
        group = str(p.get('resident_group') or kind)
        if group not in group_order: group_order.append(group)
        planned.append({
            'job_id': job.get('job_id'),
            'resource_profile': kind,
            'resident_group': group,
            'vram_gib': float(p.get('vram_gib', 0)),
            'ram_gib': float(p.get('ram_gib', 0)),
            'estimated_seconds': float(job.get('estimated_seconds', p.get('estimated_seconds_per_job', 0))),
            'blocked_by': job.get('blocked_by', []),
            'source_ids': job.get('source_ids', []),
        })

    # Keep dependency safety first. Within the ready frontier, prefer the current
    # resident group so model reloads are reduced without changing dependencies.
    by_id = {x['job_id']: x for x in planned}
    done: set[str] = set(); ordered = []; resident = ''
    while len(done) < len(planned):
        ready = [x for x in planned if x['job_id'] not in done and all(dep in done for dep in x.get('blocked_by', []))]
        if not ready:
            blockers.append('resource scheduler found a dependency deadlock')
            break
        same = [x for x in ready if x['resident_group'] == resident] if resident else []
        choice = same[0] if same else sorted(ready, key=lambda x: (group_order.index(x['resident_group']), x['job_id']))[0]
        if choice['resident_group'] != resident:
            resident = choice['resident_group']
        ordered.append(choice); done.add(choice['job_id'])

    waves = []
    for item in ordered:
        if not waves or waves[-1]['resident_group'] != item['resident_group']:
            waves.append({'wave_id': f'WAVE-{len(waves)+1:03d}', 'resident_group': item['resident_group'], 'jobs': [], 'estimated_seconds': 0.0, 'peak_vram_gib': 0.0, 'peak_ram_gib': 0.0})
        wave = waves[-1]
        wave['jobs'].append(item['job_id'])
        wave['estimated_seconds'] += item['estimated_seconds']
        wave['peak_vram_gib'] = max(wave['peak_vram_gib'], item['vram_gib'])
        wave['peak_ram_gib'] = max(wave['peak_ram_gib'], item['ram_gib'])
    for wave in waves:
        wave['estimated_seconds'] = round(wave['estimated_seconds'], 3)
    total_seconds = round(sum(x['estimated_seconds'] for x in ordered), 3)
    report = {
        'schema_version': 1,
        'batch_id': batch.get('batch_id', ''),
        'ready': not blockers and len(ordered) == len(planned),
        'llm_unload_required': any(profiles[x['resource_profile']].get('exclusive_gpu', False) for x in planned),
        'machine': machine,
        'usable_limits': {'vram_gib': round(vram_cap, 3), 'ram_gib': round(ram_cap, 3)},
        'jobs': ordered,
        'waves': waves,
        'budget': {
            'job_count': len(ordered),
            'wave_count': len(waves),
            'estimated_generation_seconds': total_seconds,
            'estimated_generation_hours': round(total_seconds / 3600.0, 3),
            'model_group_changes': max(0, len(waves) - 1),
        },
        'blockers': blockers,
        'generated_at': now(),
    }
    return report


def render_md(report: dict[str, Any]) -> str:
    lines = ['# Generation Budget and Memory Schedule', '', '[Resource-safe generation](../docs/generation/resource-safe.md) | [Feature-scale guide](../docs/production/feature-scale.md) | [Documentation home](../docs/README.md)', '', f"Ready: **{'YES' if report['ready'] else 'NO'}**", '', f"Jobs: {report['budget']['job_count']}", f"Memory waves: {report['budget']['wave_count']}", f"Estimated generation time: {report['budget']['estimated_generation_hours']} hour(s)", f"Local LLM unload required: {'yes' if report['llm_unload_required'] else 'no'}", '']
    if report['blockers']:
        lines += ['## Blockers', ''] + [f'- {x}' for x in report['blockers']] + ['']
    lines += ['## Waves', '', '| Wave | Model group | Jobs | Peak VRAM | Peak RAM | Estimated time |', '|---|---|---:|---:|---:|---:|']
    for wave in report['waves']:
        lines.append(f"| {wave['wave_id']} | {wave['resident_group']} | {len(wave['jobs'])} | {wave['peak_vram_gib']:.1f} GiB | {wave['peak_ram_gib']:.1f} GiB | {wave['estimated_seconds']:.1f} s |")
    lines += ['', '## Rule', '', 'Run jobs only when their blockers are complete. Prefer the current model group when more than one ready job exists. Never exceed the declared usable RAM or VRAM limit.', '']
    return '\n'.join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description='Build a local-first generation budget and memory schedule.')
    ap.add_argument('project')
    ap.add_argument('--strict', action='store_true')
    args = ap.parse_args(); root = Path(args.project).expanduser().resolve()
    try:
        report = build(root)
        atomic_write_json(root / '04_generation/generation_schedule.json', report)
        atomic_write_text(root / '04_generation/generation_schedule.md', render_md(report))
    except Exception as exc:
        print('ERROR', exc); return 1
    print(json.dumps(report, indent=2))
    return 1 if args.strict and not report['ready'] else 0

if __name__ == '__main__': raise SystemExit(main())
