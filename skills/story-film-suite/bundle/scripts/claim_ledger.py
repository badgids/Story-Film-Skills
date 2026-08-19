#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from media_runtime import MediaRuntimeError, project_path, project_root

SRC_RX = re.compile(r'^SRC-\d{3}$')
CLAIM_RX = re.compile(r'^CLAIM-\d{3}$')
STATUSES = {'verified', 'supported', 'contested', 'anecdotal', 'inspiration', 'project-decision', 'unresolved'}
CONFIDENCE = {'high', 'medium', 'low', 'unknown'}
PUBLIC_OK = {'verified', 'supported', 'project-decision'}


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise MediaRuntimeError(f'{path}:{n}: invalid JSON: {exc}') from exc
        if not isinstance(obj, dict):
            raise MediaRuntimeError(f'{path}:{n}: row must be object')
        rows.append(obj)
    return rows


def validate(rows: list[dict], public_ids: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    seen_sources: set[str] = set()
    public_ids = public_ids or set()
    for i, row in enumerate(rows, 1):
        cid = row.get('claim_id', '')
        prefix = cid or f'row {i}'
        if not CLAIM_RX.fullmatch(cid or ''):
            errors.append(f'{prefix}: claim_id must be CLAIM-###')
        elif cid in seen:
            errors.append(f'{cid}: duplicate claim_id')
        seen.add(cid)
        if not isinstance(row.get('statement'), str) or not row.get('statement', '').strip():
            errors.append(f'{prefix}: statement is required')
        status = row.get('status')
        if status not in STATUSES:
            errors.append(f'{prefix}: invalid status {status!r}')
        conf = row.get('confidence', 'unknown')
        if conf not in CONFIDENCE:
            errors.append(f'{prefix}: invalid confidence {conf!r}')
        sources = row.get('sources', [])
        if not isinstance(sources, list):
            errors.append(f'{prefix}: sources must be an array')
            sources = []
        for j, src in enumerate(sources, 1):
            if not isinstance(src, dict):
                errors.append(f'{prefix}: source {j} must be object')
                continue
            sid = src.get('source_id')
            if sid is not None:
                if not isinstance(sid, str) or not SRC_RX.fullmatch(sid):
                    errors.append(f'{prefix}: source {j} source_id must be SRC-###')
                elif sid in seen_sources:
                    errors.append(f'{prefix}: duplicate source_id {sid}')
                else:
                    seen_sources.add(sid)
            if not any(str(src.get(k, '')).strip() for k in ('citation', 'url', 'notes')):
                errors.append(f'{prefix}: source {j} needs citation, url, or notes')
        if status == 'verified' and not sources:
            errors.append(f'{prefix}: verified claim requires at least one source')
        if row.get('adopted') and status in {'anecdotal', 'inspiration', 'unresolved'} and not str(row.get('adoption_note', '')).strip():
            errors.append(f'{prefix}: adopting {status} material requires adoption_note')
        used_by = row.get('used_by', [])
        if not isinstance(used_by, list) or not all(isinstance(x, str) and x for x in used_by):
            errors.append(f'{prefix}: used_by must be an array of nonempty strings')
        if cid in public_ids and status not in PUBLIC_OK:
            errors.append(f'{prefix}: public-facing use requires verified, supported, or project-decision status')
    unknown = public_ids - seen
    for cid in sorted(unknown):
        errors.append(f'{cid}: public-facing claim reference is missing from ledger')
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description='Validate project evidence claim ledger.')
    ap.add_argument('project_dir')
    ap.add_argument('--path', default='01_story/research/claims.jsonl')
    ap.add_argument('--public-id', action='append', default=[])
    args = ap.parse_args()
    root = project_root(args.project_dir)
    path = project_path(root, args.path)
    rows = load_jsonl(path)
    errors = validate(rows, set(args.public_id))
    if errors:
        for e in errors:
            print('ERROR', e)
        return 2
    print(json.dumps({'status': 'pass', 'claims': len(rows), 'public_checked': len(set(args.public_id))}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except MediaRuntimeError as exc:
        print(f'ERROR {exc}')
        raise SystemExit(2)
