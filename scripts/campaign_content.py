#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from media_runtime import MediaRuntimeError, project_path, project_root
from claim_ledger import load_jsonl as load_claims, validate as validate_claims, PUBLIC_OK

CONTENT_RX = re.compile(r'^CONTENT-\d{3}$')
COPY_RX = re.compile(r'^COPY-\d{3}$')


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        raise MediaRuntimeError(f'invalid JSON: {path}') from exc


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
        rows.append(obj)
    return rows


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    brand = load_json(project_path(root, '06_release/social/brand_voice.json'), {})
    lineage = load_jsonl(project_path(root, '06_release/social/content_lineage.jsonl'))
    copy_rows = load_jsonl(project_path(root, '06_release/social/copy.jsonl'))
    claims = load_claims(project_path(root, '01_story/research/claims.jsonl'))

    if brand:
        if brand.get('schema_version') != 1:
            errors.append('brand_voice.json: schema_version must be 1')
        attrs = brand.get('voice_attributes', [])
        if not isinstance(attrs, list) or not attrs:
            errors.append('brand_voice.json: voice_attributes must be a nonempty array')
        for field in ('preferred_vocabulary', 'avoid_vocabulary', 'prohibited_claims'):
            if field in brand and not isinstance(brand.get(field), list):
                errors.append(f'brand_voice.json: {field} must be an array')

    copy_ids = set()
    for row in copy_rows:
        cid = row.get('copy_id', '')
        if cid:
            if not COPY_RX.fullmatch(cid):
                errors.append(f'copy record: invalid copy_id {cid!r}')
            if cid in copy_ids:
                errors.append(f'copy record: duplicate copy_id {cid}')
            copy_ids.add(cid)

    claim_by_id = {r.get('claim_id'): r for r in claims if r.get('claim_id')}
    public_claim_ids: set[str] = set()
    seen_content: set[str] = set()
    for i, row in enumerate(lineage, 1):
        cid = row.get('content_id', '')
        prefix = cid or f'content row {i}'
        if not CONTENT_RX.fullmatch(cid or ''):
            errors.append(f'{prefix}: content_id must be CONTENT-###')
        elif cid in seen_content:
            errors.append(f'{cid}: duplicate content_id')
        seen_content.add(cid)
        sources = row.get('source_ids', [])
        if not isinstance(sources, list) or not sources:
            errors.append(f'{prefix}: source_ids must be a nonempty array')
        copy_id = row.get('copy_id')
        if copy_id and copy_id not in copy_ids:
            errors.append(f'{prefix}: copy_id {copy_id} does not resolve')
        claim_ids = row.get('claim_ids', [])
        if not isinstance(claim_ids, list):
            errors.append(f'{prefix}: claim_ids must be an array')
            claim_ids = []
        for claim_id in claim_ids:
            public_claim_ids.add(claim_id)
            rec = claim_by_id.get(claim_id)
            if rec is None:
                errors.append(f'{prefix}: claim {claim_id} does not resolve')
            elif rec.get('status') not in PUBLIC_OK:
                errors.append(f'{prefix}: public claim {claim_id} has non-public status {rec.get("status")!r}')
        if not str(row.get('destination', '')).strip():
            errors.append(f'{prefix}: destination is required')
        if not str(row.get('transformation', '')).strip():
            errors.append(f'{prefix}: transformation is required')

    errors.extend(validate_claims(claims, public_claim_ids))
    return list(dict.fromkeys(errors))


def main() -> int:
    ap = argparse.ArgumentParser(description='Validate campaign brand voice, content lineage, copy, and public claim references.')
    ap.add_argument('project_dir')
    ap.add_argument('--validate', action='store_true')
    args = ap.parse_args()
    root = project_root(args.project_dir)
    errors = validate(root)
    if errors:
        for e in errors:
            print('ERROR', e)
        return 2
    print(json.dumps({'status': 'pass'}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except MediaRuntimeError as exc:
        print(f'ERROR {exc}')
        raise SystemExit(2)
