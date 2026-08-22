#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
from pathlib import Path

STAGES = ('composition', 'environment-style', 'identity')


def read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def validate_project(root: Path) -> list[str]:
    path = root / '03_preproduction/storyboards/grounding_passes.jsonl'
    errors: list[str] = []
    try:
        rows = read_rows(path)
    except Exception as exc:
        return [f'{path.relative_to(root)}: {exc}']
    by_target: dict[str, list[dict]] = {}
    for row_number, record in enumerate(rows, 1):
        target = record.get('target_id')
        stage = record.get('stage')
        if not isinstance(target, str) or not target:
            errors.append(f'row {row_number}: target_id required')
            continue
        if stage not in STAGES:
            errors.append(f'row {row_number}: invalid stage {stage!r}')
            continue
        refs = record.get('reference_bindings', [])
        if not isinstance(refs, list):
            errors.append(f'row {row_number}: reference_bindings must be an array')
        elif any(not isinstance(item, dict) or not isinstance(item.get('ref_id'), str) for item in refs):
            errors.append(f'row {row_number}: every reference binding must include ref_id')
        scopes = record.get('authority_scopes', [])
        if not isinstance(scopes, list) or any(not isinstance(item, str) for item in scopes):
            errors.append(f'row {row_number}: authority_scopes must be a string array')
        if not isinstance(record.get('prompt', ''), str):
            errors.append(f'row {row_number}: prompt must be a string')
        by_target.setdefault(target, []).append(record)
    for target, passes in by_target.items():
        indexes = [STAGES.index(item['stage']) for item in passes if item.get('stage') in STAGES]
        if indexes != sorted(indexes):
            errors.append(f'{target}: grounding stages are out of order')
        if len(indexes) != len(set(indexes)):
            errors.append(f'{target}: duplicate grounding stage')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate staged storyboard/reference grounding passes.')
    parser.add_argument('project_dir')
    args = parser.parse_args()
    errors = validate_project(Path(args.project_dir).resolve())
    for error in errors:
        print('ERROR', error)
    print('OK staged grounding' if not errors else f'FAILED {len(errors)}')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
