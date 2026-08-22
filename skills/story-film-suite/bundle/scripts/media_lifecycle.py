#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import shutil
from pathlib import Path

from media_registry import load_approvals, load_records, paths, save_records

DELETABLE = {'rejected', 'superseded', 'retired'}


def safe(root: Path, rel: str) -> Path | None:
    candidate = (root / rel).resolve()
    resolved_root = root.resolve()
    return candidate if candidate != resolved_root and resolved_root in candidate.parents else None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def append_ledger(root: Path, record: dict) -> None:
    path = root / '00_project/media_cleanup.jsonl'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(record, sort_keys=True) + '\n')


def _state(root: Path):
    registry_path, approvals_path = paths(root)
    records = load_records(registry_path)
    approvals = load_approvals(approvals_path)
    return registry_path, approvals_path, records, approvals


def _record(records: list[dict], media_id: str) -> dict:
    record = next((item for item in records if item.get('media_id') == media_id), None)
    if record is None:
        raise ValueError(f'unknown media_id {media_id}')
    return record


def _is_approved_primary(approvals: dict, media_id: str) -> bool:
    return any(
        isinstance(group, dict) and group.get('primary_media_id') == media_id
        for group in approvals.get('groups', {}).values()
    )


def delete_media(root: Path, media_id: str) -> bool:
    registry_path, _, records, approvals = _state(root)
    record = _record(records, media_id)
    if record.get('status') not in DELETABLE:
        raise ValueError('media must be rejected, superseded, or retired')
    if _is_approved_primary(approvals, media_id):
        raise ValueError('approved primary media cannot be deleted')
    rel = record.get('path', '')
    path = safe(root, rel)
    if path is None:
        raise ValueError('unsafe media path')
    if any(item is not record and item.get('path') == rel and item.get('status') not in DELETABLE for item in records):
        raise ValueError('path is shared by active media')
    existed = path.exists()
    if existed:
        if not path.is_file():
            raise ValueError('registered media path is not a file')
        path.unlink()
    record.setdefault('metadata', {})['physical_deleted'] = True
    save_records(registry_path, records)
    append_ledger(root, {
        'media_id': media_id,
        'path': rel,
        'operation': 'delete',
        'existed': existed,
        'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    })
    return existed


def repair_approved_copy(root: Path, media_id: str, dest_rel: str) -> str:
    _, _, records, approvals = _state(root)
    record = _record(records, media_id)
    if record.get('status') != 'primary' or not _is_approved_primary(approvals, media_id):
        raise ValueError('repair source must be the approved primary media for its group')
    source = safe(root, record.get('path', ''))
    destination = safe(root, dest_rel)
    if source is None or destination is None or not source.is_file():
        raise ValueError('unsafe or missing approved repair source/destination')
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    digest = sha256(destination)
    append_ledger(root, {
        'media_id': media_id,
        'source_path': record.get('path'),
        'destination_path': dest_rel,
        'operation': 'repair-copy',
        'sha256': digest,
        'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    })
    return digest


def main() -> int:
    parser = argparse.ArgumentParser(description='Safely clean rejected media or repair a disposable copy from approved media.')
    parser.add_argument('project_dir')
    sub = parser.add_subparsers(dest='command', required=True)
    delete = sub.add_parser('delete')
    delete.add_argument('media_id')
    repair = sub.add_parser('repair-copy')
    repair.add_argument('media_id')
    repair.add_argument('--dest', required=True)
    args = parser.parse_args()
    root = Path(args.project_dir).resolve()
    try:
        if args.command == 'delete':
            print(json.dumps({'media_id': args.media_id, 'deleted': delete_media(root, args.media_id)}))
            return 0
        digest = repair_approved_copy(root, args.media_id, args.dest)
        print(json.dumps({'media_id': args.media_id, 'destination': args.dest, 'sha256': digest}, indent=2))
        return 0
    except Exception as exc:
        print('ERROR', exc)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
