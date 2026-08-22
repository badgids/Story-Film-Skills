#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
from pathlib import Path

from dialogue_sync import build_coverage as build_dialogue_sync_coverage


def read_json(path: Path, default):
    if not path.exists():
        return default
    with path.open(encoding='utf-8') as f:
        return json.load(f)


def read_jsonl(path: Path):
    rows = []
    if not path.exists():
        return rows
    for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        rows.append((n, json.loads(line)))
    return rows


def build_report(root: Path, scene_ids: set[str] | None = None):
    root = root.resolve()
    line_path = root / '02_screenplay/line_manifest.jsonl'
    screenplay_exists = (root / '02_screenplay/screenplay.fountain').exists()
    lines_raw = read_jsonl(line_path)
    lines = {}
    duplicate_lines = []
    invalid_lines = []
    for n, rec in lines_raw:
        if not isinstance(rec, dict):
            invalid_lines.append({'row': n, 'reason': 'record is not an object'})
            continue
        lid = rec.get('line_id')
        sid = rec.get('scene_id')
        if not isinstance(lid, str) or not lid.startswith('LINE-'):
            invalid_lines.append({'row': n, 'reason': f'invalid line_id {lid!r}'})
            continue
        if scene_ids and sid not in scene_ids:
            continue
        if lid in lines:
            duplicate_lines.append(lid)
        lines[lid] = rec

    shot_rows = read_jsonl(root / '04_generation/shot_briefs.jsonl')
    shots = {}
    shot_line_map = {}
    for _, rec in shot_rows:
        if not isinstance(rec, dict):
            continue
        sid = rec.get('shot_id')
        if isinstance(sid, str):
            shots[sid] = rec
            for lid in rec.get('line_ids', []) if isinstance(rec.get('line_ids', []), list) else []:
                shot_line_map.setdefault(lid, []).append(sid)

    voice_rows = read_jsonl(root / '04_generation/voice_cues.jsonl')
    voice_by_line = {}
    for _, rec in voice_rows:
        if isinstance(rec, dict) and isinstance(rec.get('line_id'), str):
            voice_by_line.setdefault(rec['line_id'], []).append(rec)

    block_rows = read_jsonl(root / '03_preproduction/performance_blocking.jsonl')
    blocking = {}
    for _, rec in block_rows:
        if isinstance(rec, dict) and isinstance(rec.get('line_id'), str):
            blocking.setdefault(rec['line_id'], []).append(rec)

    shooting_path = root / '03_preproduction/shooting_script.json'
    shooting = read_json(shooting_path, {})
    shooting_units = {}
    if isinstance(shooting, dict):
        for scene in shooting.get('scenes', []) if isinstance(shooting.get('scenes', []), list) else []:
            if not isinstance(scene, dict):
                continue
            if scene_ids and scene.get('scene_id') not in scene_ids:
                continue
            for unit in scene.get('units', []) if isinstance(scene.get('units', []), list) else []:
                if isinstance(unit, dict) and isinstance(unit.get('line_id'), str):
                    shooting_units.setdefault(unit['line_id'], []).append(unit)

    missing_voice = []
    missing_shot_coverage = []
    missing_blocking = []
    missing_shooting_unit = []
    text_drift = []
    unresolved_shots = []
    timing_conflicts = []

    for lid, rec in lines.items():
        kind = rec.get('kind')
        text = rec.get('text')
        audible = rec.get('audible', kind == 'dialogue')
        on_screen = rec.get('on_screen', True)
        blocking_required = rec.get('blocking_required', on_screen and kind in {'dialogue', 'action', 'movement'})

        if audible and kind == 'dialogue':
            cues = voice_by_line.get(lid, [])
            if not cues:
                missing_voice.append(lid)
            for cue in cues:
                if isinstance(text, str) and isinstance(cue.get('text'), str) and cue['text'] != text:
                    text_drift.append({'line_id': lid, 'source': 'voice_cue', 'expected': text, 'actual': cue['text']})

        covered = set(shot_line_map.get(lid, []))
        for unit in shooting_units.get(lid, []):
            ids = unit.get('shot_ids', [])
            if isinstance(ids, list):
                covered.update(x for x in ids if isinstance(x, str))
        if on_screen and not covered:
            missing_shot_coverage.append(lid)

        if blocking_required and not blocking.get(lid):
            missing_blocking.append(lid)

        if shooting and not shooting_units.get(lid):
            missing_shooting_unit.append(lid)

        for unit in shooting_units.get(lid, []):
            utext = unit.get('text')
            if kind == 'dialogue' and isinstance(text, str) and isinstance(utext, str) and utext != text:
                text_drift.append({'line_id': lid, 'source': 'shooting_script', 'expected': text, 'actual': utext})
            for sid in unit.get('shot_ids', []) if isinstance(unit.get('shot_ids', []), list) else []:
                if sid not in shots:
                    unresolved_shots.append({'line_id': lid, 'shot_id': sid})
            timing = unit.get('timing', {}) if isinstance(unit.get('timing'), dict) else {}
            speech = timing.get('speech_duration_s')
            planned = timing.get('planned_duration_s')
            allow_overlap = timing.get('allow_overlap', False)
            if isinstance(speech, (int, float)) and isinstance(planned, (int, float)) and speech > planned and not allow_overlap:
                timing_conflicts.append({'line_id': lid, 'speech_duration_s': speech, 'planned_duration_s': planned})

    orphan_voice = sorted(lid for lid in voice_by_line if lid not in lines)
    orphan_blocking = sorted(lid for lid in blocking if lid not in lines)
    orphan_shooting = sorted(lid for lid in shooting_units if lid not in lines)
    orphan_shot_links = sorted(lid for lid in shot_line_map if lid not in lines)

    missing_line_manifest = screenplay_exists and not line_path.exists()
    empty_line_manifest = screenplay_exists and line_path.exists() and not lines
    missing_shooting_script = bool(lines) and not shooting_path.exists()
    dialogue_sync = build_dialogue_sync_coverage(root, scene_ids)
    sync_blockers = any(dialogue_sync.get(key) for key in (
        'missing_lip_sync_coverage',
        'lip_sync_speaker_conflicts',
        'lip_sync_timing_conflicts',
        'lip_sync_line_conflicts',
    ))
    blockers = bool(
        invalid_lines or duplicate_lines or missing_voice or missing_shot_coverage or
        missing_blocking or missing_shooting_unit or text_drift or unresolved_shots or timing_conflicts or
        orphan_voice or orphan_blocking or orphan_shooting or orphan_shot_links or
        missing_line_manifest or empty_line_manifest or missing_shooting_script or sync_blockers
    )
    report = {
        'schema_version': 1,
        'scope': sorted(scene_ids) if scene_ids else 'all',
        'ready': not blockers,
        'totals': {
            'lines': len(lines),
            'shots': len(shots),
            'voice_cues': sum(len(v) for v in voice_by_line.values()),
            'blocking_records': sum(len(v) for v in blocking.values()),
            'shooting_units': sum(len(v) for v in shooting_units.values()),
        },
        'missing_line_manifest': missing_line_manifest,
        'empty_line_manifest': empty_line_manifest,
        'missing_shooting_script': missing_shooting_script,
        'invalid_lines': invalid_lines,
        'duplicate_lines': sorted(set(duplicate_lines)),
        'missing_voice': sorted(set(missing_voice)),
        'missing_shot_coverage': sorted(set(missing_shot_coverage)),
        'missing_blocking': sorted(set(missing_blocking)),
        'missing_shooting_unit': sorted(set(missing_shooting_unit)),
        'text_drift': text_drift,
        'unresolved_shots': unresolved_shots,
        'timing_conflicts': timing_conflicts,
        'orphan_voice_lines': orphan_voice,
        'orphan_blocking_lines': orphan_blocking,
        'orphan_shooting_lines': orphan_shooting,
        'orphan_shot_line_links': orphan_shot_links,
    }
    report.update(dialogue_sync)
    return report


def markdown(report):
    lines = ['# Production Coverage', '', f"Ready: {'YES' if report['ready'] else 'NO'}", '']
    for key, val in report['totals'].items():
        lines.append(f'- {key}: {val}')
    sections = [
        ('Missing line manifest', report['missing_line_manifest']),
        ('Empty line manifest', report['empty_line_manifest']),
        ('Missing shooting script', report['missing_shooting_script']),
        ('Invalid lines', report['invalid_lines']),
        ('Duplicate lines', report['duplicate_lines']),
        ('Missing voice', report['missing_voice']),
        ('Missing shot coverage', report['missing_shot_coverage']),
        ('Missing blocking', report['missing_blocking']),
        ('Missing shooting unit', report['missing_shooting_unit']),
        ('Text drift', report['text_drift']),
        ('Unresolved shots', report['unresolved_shots']),
        ('Timing conflicts', report['timing_conflicts']),
        ('Missing visible-dialogue sync coverage', report.get('missing_lip_sync_coverage', [])),
        ('Visible-dialogue speaker conflicts', report.get('lip_sync_speaker_conflicts', [])),
        ('Visible-dialogue timing conflicts', report.get('lip_sync_timing_conflicts', [])),
        ('Visible-dialogue line conflicts', report.get('lip_sync_line_conflicts', [])),
        ('Orphan voice lines', report['orphan_voice_lines']),
        ('Orphan blocking lines', report['orphan_blocking_lines']),
        ('Orphan shooting lines', report['orphan_shooting_lines']),
        ('Orphan shot line links', report['orphan_shot_line_links']),
    ]
    for title, value in sections:
        if not value:
            continue
        lines += ['', f'## {title}', '']
        if value is True:
            lines.append('- present')
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    lines.append('- ' + json.dumps(item, ensure_ascii=False, sort_keys=True))
                else:
                    lines.append(f'- {item}')
    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project_dir')
    ap.add_argument('--scene', action='append', default=[])
    ap.add_argument('--json-out')
    ap.add_argument('--md-out')
    ap.add_argument('--no-write', action='store_true')
    args = ap.parse_args()
    root = Path(args.project_dir).expanduser().resolve()
    report = build_report(root, set(args.scene) or None)
    if not args.no_write:
        jpath = Path(args.json_out) if args.json_out else root / '03_preproduction/production_coverage.json'
        mpath = Path(args.md_out) if args.md_out else root / '03_preproduction/production_coverage.md'
        jpath.parent.mkdir(parents=True, exist_ok=True)
        mpath.parent.mkdir(parents=True, exist_ok=True)
        jpath.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        mpath.write_text(markdown(report), encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report['ready'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
