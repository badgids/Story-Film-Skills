#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
from pathlib import Path

from media_registry import load_approvals, load_records, paths as media_paths
from media_runtime import MediaRuntimeError, portable_rel, project_path, project_root, read_json, write_json
from promo_validate import validate_social, validate_trailers

ACCEPTABLE_QC = {'pass', 'warn', 'not-applicable'}


def registry_state(root: Path):
    registry_path, approvals_path = media_paths(root)
    records = load_records(registry_path)
    approvals = load_approvals(approvals_path)
    by_id = {r.get('media_id'): r for r in records if isinstance(r, dict)}
    return by_id, approvals.get('groups', {}) if isinstance(approvals.get('groups'), dict) else {}


def approved_output(by_id: dict, groups: dict, group_id: str, output_path: str):
    group = groups.get(group_id)
    if not isinstance(group, dict):
        return None, f'{group_id}: no media approval group'
    mid = group.get('primary_media_id')
    rec = by_id.get(mid)
    if not isinstance(rec, dict):
        return None, f'{group_id}: no valid primary media record'
    if rec.get('path') != output_path:
        return rec, f'{group_id}: approved primary path does not match deliverable output'
    if rec.get('qc_status') not in ACCEPTABLE_QC:
        return rec, f'{group_id}: approved primary QC is not complete'
    return rec, None


def qc_status(path: Path):
    if not path.exists():
        return None, 'missing QC report'
    try:
        obj = read_json(path)
    except Exception as exc:
        return None, f'invalid QC report: {exc}'
    status = obj.get('status')
    if status not in ACCEPTABLE_QC:
        return status, f'QC status is {status!r}'
    return status, None


def reconcile_trailers(root: Path, *, mutate: bool) -> dict:
    errors = validate_trailers(root)
    path = root / '06_release/trailers/trailer_manifest.json'
    if not path.exists():
        report = {'schema_version': 1, 'scope': 'trailers', 'ready': True, 'deliverables': [], 'blockers': errors}
        if errors:
            report['ready'] = False
        write_json(root / '06_release/trailers/delivery_report.json', report)
        return report
    obj = read_json(path)
    by_id, groups = registry_state(root)
    rows = []
    blockers = list(errors)
    for rec in obj.get('trailers', []):
        if not isinstance(rec, dict):
            continue
        tid = rec.get('trailer_id', '')
        required = rec.get('required', True) is not False
        out = rec.get('output_path', '')
        item_errors = []
        media_id = ''
        media_qc = ''
        if not isinstance(out, str) or not portable_rel(out):
            item_errors.append('invalid output_path')
        else:
            output = project_path(root, out)
            if not output.is_file() or output.stat().st_size <= 0:
                item_errors.append('output media missing or empty')
            approved, msg = approved_output(by_id, groups, tid, out)
            if msg:
                item_errors.append(msg)
            elif approved:
                media_id = approved.get('media_id', '')
                media_qc = approved.get('qc_status', '')
        tl = rec.get('timeline_path', '')
        if isinstance(tl, str) and portable_rel(tl):
            qc_path = project_path(root, str(Path(tl).with_name('qc.json')).replace('\\', '/'))
            qcs, msg = qc_status(qc_path)
            if msg:
                item_errors.append(msg)
        else:
            qcs = None
            item_errors.append('invalid timeline_path')
        ready = not item_errors
        if required and not ready:
            blockers.extend(f'{tid}: {msg}' for msg in item_errors)
        status = 'ready' if ready else ('blocked' if required else 'optional-missing')
        rows.append({'trailer_id': tid, 'required': required, 'status': status, 'media_id': media_id, 'media_qc_status': media_qc, 'delivery_qc_status': qcs, 'issues': item_errors})
        if mutate:
            rec['delivery_status'] = status
            if media_id:
                rec['primary_media_id'] = media_id
            if qcs:
                rec['qc_status'] = qcs
    if mutate:
        write_json(path, obj)
    report = {'schema_version': 1, 'scope': 'trailers', 'ready': not blockers, 'deliverables': rows, 'blockers': blockers}
    write_json(root / '06_release/trailers/delivery_report.json', report)
    return report


def load_copy_ids(root: Path) -> set[str]:
    path = root / '06_release/social/copy.jsonl'
    ids = set()
    if not path.exists():
        return ids
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(rec, dict) and isinstance(rec.get('copy_id'), str):
            ids.add(rec['copy_id'])
    return ids


def social_rows(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip():
            obj = json.loads(line)
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def write_jsonl(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in rows), encoding='utf-8')


def reconcile_social(root: Path, *, mutate: bool) -> dict:
    errors = validate_social(root)
    path = root / '06_release/social/deliverables.jsonl'
    records = social_rows(path)
    by_id, groups = registry_state(root)
    copy_ids = load_copy_ids(root)
    rows = []
    blockers = list(errors)
    for rec in records:
        sid = rec.get('social_id', '')
        required = rec.get('required', True) is not False
        media_type = rec.get('media_type')
        item_errors = []
        media_id = ''
        media_qc = ''
        delivery_qc_state = None
        out = rec.get('output_path')
        if media_type in {'video', 'image', 'audio'}:
            if not isinstance(out, str) or not portable_rel(out):
                item_errors.append('missing or invalid output_path')
            else:
                output = project_path(root, out)
                if not output.is_file() or output.stat().st_size <= 0:
                    item_errors.append('output media missing or empty')
                approved, msg = approved_output(by_id, groups, sid, out)
                if msg:
                    item_errors.append(msg)
                elif approved:
                    media_id = approved.get('media_id', '')
                    media_qc = approved.get('qc_status', '')
            if media_type == 'video':
                qpath = root / f'06_release/social/qc/{sid}.json'
                delivery_qc_state, msg = qc_status(qpath)
                if msg:
                    item_errors.append(msg)
        elif media_type == 'package':
            if not isinstance(out, str) or not portable_rel(out) or not project_path(root, out).is_file():
                item_errors.append('package output missing')
        copy_id = rec.get('copy_id')
        if copy_id and copy_id not in copy_ids:
            item_errors.append(f'missing copy record {copy_id}')
        if media_type == 'copy' and not copy_id:
            item_errors.append('copy deliverable requires copy_id')
        ready = not item_errors
        if required and not ready:
            blockers.extend(f'{sid}: {msg}' for msg in item_errors)
        status = 'ready' if ready else ('blocked' if required else 'optional-missing')
        rows.append({'social_id': sid, 'required': required, 'status': status, 'media_id': media_id, 'media_qc_status': media_qc, 'delivery_qc_status': delivery_qc_state, 'issues': item_errors})
        if mutate:
            rec['delivery_status'] = status
            if media_id:
                rec['primary_media_id'] = media_id
            if delivery_qc_state:
                rec['qc_status'] = delivery_qc_state
    if mutate and path.exists():
        write_jsonl(path, records)
    report = {'schema_version': 1, 'scope': 'social', 'ready': not blockers, 'deliverables': rows, 'blockers': blockers}
    write_json(root / '06_release/social/delivery_report.json', report)
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description='Reconcile final trailer and social campaign readiness against actual media, approvals, copy, and QC.')
    ap.add_argument('project_dir')
    ap.add_argument('--scope', choices=['all', 'trailers', 'social'], default='all')
    ap.add_argument('--reconcile', action='store_true', help='Persist delivery_status, primary media ID, and QC state into promo manifests.')
    args = ap.parse_args()
    root = project_root(args.project_dir)
    reports = []
    if args.scope in {'all', 'trailers'}:
        reports.append(reconcile_trailers(root, mutate=args.reconcile))
    if args.scope in {'all', 'social'}:
        reports.append(reconcile_social(root, mutate=args.reconcile))
    ready = all(x['ready'] for x in reports)
    print(json.dumps({'schema_version': 1, 'ready': ready, 'reports': reports}, indent=2))
    return 0 if ready else 1


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (MediaRuntimeError, json.JSONDecodeError) as exc:
        print(f'ERROR {exc}')
        raise SystemExit(2)
