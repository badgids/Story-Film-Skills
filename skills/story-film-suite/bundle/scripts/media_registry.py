#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from media_runtime import MediaRuntimeError, portable_rel, project_root, read_json, write_json

MEDIA_RX = re.compile(r'^MEDIA-\d{3,}$')
STATUS = {'candidate', 'primary', 'alternate', 'rejected', 'superseded', 'retired'}
QC = {'pass', 'warn', 'fail', 'not-checked', 'not-applicable'}


def paths(root: Path):
    return root / '00_project/media_registry.jsonl', root / '00_project/media_approvals.json'


def load_records(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise MediaRuntimeError(f'{path.name}:{n}: invalid JSON: {exc}') from exc
        if not isinstance(obj, dict):
            raise MediaRuntimeError(f'{path.name}:{n}: record must be an object')
        rows.append(obj)
    return rows


def save_records(path: Path, records: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = ''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in records)
    path.write_text(text, encoding='utf-8')


def load_approvals(path: Path):
    if not path.exists():
        return {'schema_version': 1, 'groups': {}}
    obj = read_json(path)
    if not isinstance(obj, dict):
        raise MediaRuntimeError('media_approvals.json must be an object')
    obj.setdefault('schema_version', 1)
    obj.setdefault('groups', {})
    return obj


def validate(records: list[dict], approvals: dict) -> list[str]:
    errors = []
    by_id = {}
    primaries = {}
    for i, rec in enumerate(records, 1):
        mid = rec.get('media_id', '')
        group = rec.get('group_id', '')
        if rec.get('schema_version', 1) != 1:
            errors.append(f'record {i}: unsupported schema_version')
        if not isinstance(mid, str) or not MEDIA_RX.fullmatch(mid):
            errors.append(f'record {i}: invalid media_id {mid!r}')
        elif mid in by_id:
            errors.append(f'record {i}: duplicate media_id {mid}')
        by_id[mid] = rec
        if not isinstance(group, str) or not group.strip():
            errors.append(f'record {i}: missing group_id')
        if rec.get('status') not in STATUS:
            errors.append(f'record {i}: invalid status {rec.get("status")!r}')
        if rec.get('qc_status', 'not-checked') not in QC:
            errors.append(f'record {i}: invalid qc_status {rec.get("qc_status")!r}')
        if not isinstance(rec.get('source_ids', []), list):
            errors.append(f'record {i}: source_ids must be an array')
        p = rec.get('path', '')
        if not isinstance(p, str) or not portable_rel(p):
            errors.append(f'record {i}: path must be portable: {p!r}')
        if rec.get('status') == 'primary':
            if group in primaries:
                errors.append(f'group {group}: multiple primary media records')
            primaries[group] = mid

    groups = approvals.get('groups', {})
    if approvals.get('schema_version') != 1:
        errors.append('media_approvals.json: unsupported schema_version')
    if not isinstance(groups, dict):
        errors.append('media_approvals.json: groups must be an object')
        return errors
    for group, rec in groups.items():
        if not isinstance(rec, dict):
            errors.append(f'approval group {group}: record must be object')
            continue
        primary = rec.get('primary_media_id')
        if primary:
            if primary not in by_id:
                errors.append(f'approval group {group}: unknown primary {primary}')
            elif by_id[primary].get('group_id') != group:
                errors.append(f'approval group {group}: primary belongs to {by_id[primary].get("group_id")}')
            elif by_id[primary].get('status') != 'primary':
                errors.append(f'approval group {group}: primary record status is not primary')
            elif by_id[primary].get('qc_status') == 'fail' and rec.get('qc_override') is not True:
                errors.append(f'approval group {group}: QC-failed primary requires qc_override')
            elif by_id[primary].get('qc_status') == 'fail' and not rec.get('reason'):
                errors.append(f'approval group {group}: QC override requires reason')
        alts = rec.get('alternate_media_ids', [])
        if not isinstance(alts, list):
            errors.append(f'approval group {group}: alternate_media_ids must be array')
            continue
        for mid in alts:
            if mid not in by_id:
                errors.append(f'approval group {group}: unknown alternate {mid}')
            elif by_id[mid].get('group_id') != group:
                errors.append(f'approval group {group}: alternate {mid} belongs to another group')
            elif by_id[mid].get('status') != 'alternate':
                errors.append(f'approval group {group}: alternate {mid} record status is not alternate')
    return errors


def next_id(records: list[dict]) -> str:
    nums = [int(r['media_id'].split('-')[1]) for r in records if isinstance(r.get('media_id'), str) and MEDIA_RX.fullmatch(r['media_id'])]
    return f'MEDIA-{max(nums, default=0)+1:03d}'



def register_primary_output(root: Path, *, kind: str, group_id: str, path: str, source_ids: list[str] | None = None, qc_status: str = 'pass', reason: str = 'Deterministic approved render') -> str:
    if not portable_rel(path):
        raise MediaRuntimeError('media path must be project-relative')
    registry_path, approvals_path = paths(root)
    records = load_records(registry_path)
    approvals = load_approvals(approvals_path)
    by_id = {r.get('media_id'): r for r in records}
    rec = next((r for r in records if r.get('group_id') == group_id and r.get('path') == path), None)
    if rec is None:
        rec = {
            'schema_version': 1,
            'media_id': next_id(records),
            'kind': kind,
            'group_id': group_id,
            'source_ids': list(source_ids or []),
            'path': path,
            'status': 'candidate',
            'qc_status': qc_status,
            'created_by': 'story-film-renderer',
            'metadata': {},
        }
        records.append(rec)
        by_id[rec['media_id']] = rec
    else:
        rec['qc_status'] = qc_status
        rec['source_ids'] = list(source_ids or rec.get('source_ids', []))
    if qc_status == 'fail':
        save_records(registry_path, records)
        write_json(approvals_path, approvals)
        return rec['media_id']
    group = approvals.setdefault('groups', {}).setdefault(group_id, {'primary_media_id': '', 'alternate_media_ids': []})
    old = group.get('primary_media_id')
    if old and old != rec['media_id'] and old in by_id and by_id[old].get('status') == 'primary':
        by_id[old]['status'] = 'alternate'
        if old not in group.setdefault('alternate_media_ids', []):
            group['alternate_media_ids'].append(old)
    rec['status'] = 'primary'
    group['primary_media_id'] = rec['media_id']
    group['alternate_media_ids'] = [x for x in group.get('alternate_media_ids', []) if x != rec['media_id']]
    group['reason'] = reason
    group['qc_override'] = False
    save_records(registry_path, records)
    write_json(approvals_path, approvals)
    errs = validate(records, approvals)
    if errs:
        raise MediaRuntimeError('; '.join(errs))
    return rec['media_id']

def main() -> int:
    ap = argparse.ArgumentParser(description='Manage project media approval state.')
    ap.add_argument('project_dir')
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('validate')
    add = sub.add_parser('add')
    add.add_argument('--kind', required=True)
    add.add_argument('--group-id', required=True)
    add.add_argument('--path', required=True)
    add.add_argument('--source-id', action='append', default=[])
    add.add_argument('--qc-status', default='not-checked', choices=sorted(QC))
    add.add_argument('--created-by', default='')
    sel = sub.add_parser('select')
    sel.add_argument('media_id')
    sel.add_argument('--reason', required=True)
    sel.add_argument('--qc-override', action='store_true')
    alt = sub.add_parser('alternate')
    alt.add_argument('media_id')
    rej = sub.add_parser('reject')
    rej.add_argument('media_id')
    rej.add_argument('--reason', required=True)
    sup = sub.add_parser('supersede')
    sup.add_argument('media_id')
    sup.add_argument('--reason', required=True)
    args = ap.parse_args()

    root = project_root(args.project_dir)
    registry_path, approvals_path = paths(root)
    records = load_records(registry_path)
    approvals = load_approvals(approvals_path)

    if args.cmd == 'validate':
        errors = validate(records, approvals)
        for e in errors:
            print('ERROR', e)
        if errors:
            return 1
        print(f'OK: {len(records)} media records, {len(approvals.get("groups", {}))} approval groups')
        return 0

    if args.cmd == 'add':
        if not portable_rel(args.path):
            raise MediaRuntimeError('media path must be project-relative')
        mid = next_id(records)
        records.append({
            'schema_version': 1,
            'media_id': mid,
            'kind': args.kind,
            'group_id': args.group_id,
            'source_ids': args.source_id,
            'path': args.path.replace('\\', '/'),
            'status': 'candidate',
            'qc_status': args.qc_status,
            'created_by': args.created_by,
            'metadata': {},
        })
        save_records(registry_path, records)
        print(mid)
        return 0

    by_id = {r.get('media_id'): r for r in records}
    rec = by_id.get(args.media_id)
    if rec is None:
        raise MediaRuntimeError(f'unknown media_id {args.media_id}')
    group = rec['group_id']
    group_rec = approvals.setdefault('groups', {}).setdefault(group, {'primary_media_id': '', 'alternate_media_ids': []})

    if args.cmd == 'select':
        if rec.get('qc_status') == 'fail' and not args.qc_override:
            raise MediaRuntimeError('QC-failed media requires --qc-override')
        old = group_rec.get('primary_media_id')
        if old and old != args.media_id and old in by_id and by_id[old].get('status') == 'primary':
            by_id[old]['status'] = 'alternate'
            if old not in group_rec.setdefault('alternate_media_ids', []):
                group_rec['alternate_media_ids'].append(old)
        rec['status'] = 'primary'
        group_rec['primary_media_id'] = args.media_id
        group_rec['alternate_media_ids'] = [x for x in group_rec.get('alternate_media_ids', []) if x != args.media_id]
        group_rec['reason'] = args.reason
        group_rec['qc_override'] = bool(args.qc_override)
    elif args.cmd == 'alternate':
        if group_rec.get('primary_media_id') == args.media_id:
            group_rec['primary_media_id'] = ''
        rec['status'] = 'alternate'
        if args.media_id not in group_rec.setdefault('alternate_media_ids', []):
            group_rec['alternate_media_ids'].append(args.media_id)
    elif args.cmd in {'reject', 'supersede'}:
        if group_rec.get('primary_media_id') == args.media_id:
            group_rec['primary_media_id'] = ''
        group_rec['alternate_media_ids'] = [x for x in group_rec.get('alternate_media_ids', []) if x != args.media_id]
        rec['status'] = 'rejected' if args.cmd == 'reject' else 'superseded'
        rec.setdefault('metadata', {})[f'{args.cmd}_reason'] = args.reason

    save_records(registry_path, records)
    write_json(approvals_path, approvals)
    errors = validate(records, approvals)
    if errors:
        for e in errors:
            print('ERROR', e)
        return 1
    print(json.dumps({'media_id': args.media_id, 'group_id': group, 'status': rec['status']}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except MediaRuntimeError as exc:
        print(f'ERROR {exc}')
        raise SystemExit(2)
