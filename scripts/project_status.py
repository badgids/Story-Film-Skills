#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from datetime import datetime, timezone
from pathlib import Path


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def reverse_graph(artifacts: dict) -> dict[str, set[str]]:
    rev = {k: set() for k in artifacts}
    for key, rec in artifacts.items():
        for dep in rec.get('depends_on', []):
            rev.setdefault(dep, set()).add(key)
    return rev


def descendants(start: set[str], rev: dict[str, set[str]]) -> set[str]:
    seen = set(start)
    q = deque(start)
    while q:
        cur = q.popleft()
        for nxt in rev.get(cur, set()):
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return seen


def set_state_status(state: dict, key: str, status: str, path: str | None = None):
    arts = state.setdefault('artifacts', {})
    old = arts.get(key)
    if isinstance(old, dict):
        old['status'] = status
        if path and not old.get('path'):
            old['path'] = path
    else:
        rec = {'status': status}
        if path:
            rec['path'] = path
        arts[key] = rec


def main() -> int:
    ap = argparse.ArgumentParser(description='Calculate story-film artifact changes and downstream invalidation.')
    ap.add_argument('project_dir')
    ap.add_argument('--snapshot', action='store_true', help='Record current hashes as the approved baseline.')
    ap.add_argument('--apply', action='store_true', help='Mark affected downstream artifacts stale in state.json.')
    ap.add_argument('--changed', action='append', default=[], help='Artifact key known to have changed. Repeatable.')
    args = ap.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    dep_path = root / '00_project/dependencies.json'
    state_path = root / '00_project/state.json'
    hash_path = root / '00_project/artifact_hashes.json'

    deps = load_json(dep_path, {'schema_version': 1, 'artifacts': {}})
    artifacts = deps.get('artifacts', {})
    if not artifacts:
        print('ERROR no artifacts in 00_project/dependencies.json')
        return 1

    current = {}
    for key, rec in artifacts.items():
        rel = rec.get('path')
        if not rel:
            current[key] = None
        else:
            current[key] = sha256(root / rel)

    previous_doc = load_json(hash_path, {'schema_version': 1, 'hashes': {}})
    previous = previous_doc.get('hashes', {})

    if args.snapshot:
        hash_path.write_text(json.dumps({
            'schema_version': 1,
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'hashes': current,
        }, indent=2) + '\n', encoding='utf-8')
        print(f'OK snapshot: {sum(v is not None for v in current.values())} existing artifacts')
        return 0

    changed = set(args.changed)
    for key, cur in current.items():
        if key in previous and previous.get(key) != cur:
            changed.add(key)

    unknown = sorted(k for k in changed if k not in artifacts)
    if unknown:
        for k in unknown:
            print(f'ERROR unknown artifact key: {k}')
        return 1

    rev = reverse_graph(artifacts)
    affected_all = descendants(changed, rev) if changed else set()
    downstream = affected_all - changed

    print('Changed:')
    for key in sorted(changed):
        print(f'  {key}')
    print('Downstream stale:')
    for key in sorted(downstream):
        print(f'  {key}')
    if not changed:
        print('  none detected')

    if args.apply and changed:
        state = load_json(state_path, {'schema_version': 1, 'artifacts': {}})
        for key in changed:
            rec = artifacts.get(key, {})
            set_state_status(state, key, 'draft', rec.get('path'))
        for key in downstream:
            rec = artifacts.get(key, {})
            set_state_status(state, key, 'stale', rec.get('path'))
        state['last_updated'] = datetime.now(timezone.utc).isoformat()
        state_path.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
        print(f'OK state updated: {len(downstream)} downstream artifacts marked stale')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
