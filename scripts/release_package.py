#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from media_runtime import MediaRuntimeError, portable_rel, project_path, project_root, read_json, sha256, write_json


def validate_manifest(root: Path, obj: dict, *, require_files: bool = True) -> tuple[list[str], list[dict]]:
    errors = []
    rows = obj.get('deliverables')
    if obj.get('schema_version') != 1:
        errors.append('unsupported schema_version')
    if not isinstance(rows, list):
        errors.append('deliverables must be an array')
        return errors, []
    seen = set()
    resolved = []
    for i, rec in enumerate(rows, 1):
        if not isinstance(rec, dict):
            errors.append(f'deliverable {i}: must be object')
            continue
        did = rec.get('delivery_id', '')
        if not isinstance(did, str) or not did.startswith('DELIV-'):
            errors.append(f'deliverable {i}: invalid delivery_id {did!r}')
        elif did in seen:
            errors.append(f'deliverable {i}: duplicate delivery_id {did}')
        seen.add(did)
        rel = rec.get('path', '')
        if not isinstance(rel, str) or not portable_rel(rel):
            errors.append(f'{did}: invalid path {rel!r}')
            continue
        required = rec.get('required', True)
        try:
            path = project_path(root, rel, must_exist=require_files and required)
        except Exception as exc:
            errors.append(f'{did}: {exc}')
            continue
        qc = rec.get('qc_status')
        if require_files and required and qc not in {'pass', 'warn', 'not-applicable'}:
            if qc == 'fail':
                errors.append(f'{did}: required deliverable has blocking QC failure')
            else:
                errors.append(f'{did}: required deliverable is missing completed QC state')
        entry = dict(rec)
        if path.exists() and path.is_file():
            entry['sha256'] = sha256(path)
            entry['size_bytes'] = path.stat().st_size
        elif require_files and required:
            errors.append(f'{did}: required deliverable missing')
        resolved.append(entry)
    return errors, resolved


def main() -> int:
    ap = argparse.ArgumentParser(description='Validate and collect release deliverables.')
    ap.add_argument('project_dir')
    ap.add_argument('--manifest', default='06_release/release_manifest.json')
    ap.add_argument('--validate', action='store_true')
    ap.add_argument('--collect', action='store_true')
    args = ap.parse_args()
    root = project_root(args.project_dir)
    path = project_path(root, args.manifest, must_exist=True)
    obj = read_json(path)
    errors, resolved = validate_manifest(root, obj, require_files=True)
    if errors:
        for e in errors:
            print('ERROR', e)
        return 1
    obj['deliverables'] = resolved
    write_json(path, obj)
    sums = []
    for rec in resolved:
        if rec.get('sha256'):
            sums.append(f'{rec["sha256"]}  {rec["path"]}')
    sums_path = root / '06_release/SHA256SUMS.txt'
    sums_path.parent.mkdir(parents=True, exist_ok=True)
    sums_path.write_text('\n'.join(sums) + ('\n' if sums else ''), encoding='utf-8')
    if args.collect:
        package_root = root / '06_release/package'
        for rec in resolved:
            rel = rec['path']
            src = project_path(root, rel, must_exist=rec.get('required', True))
            if not src.exists() or not src.is_file():
                continue
            dest = package_root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    print(json.dumps({'status': 'pass', 'deliverables': len(resolved), 'checksums': len(sums), 'collected': bool(args.collect)}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except MediaRuntimeError as exc:
        print(f'ERROR {exc}')
        raise SystemExit(2)
