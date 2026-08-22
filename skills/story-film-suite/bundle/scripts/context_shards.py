#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from feature_common import atomic_write_json, atomic_write_text, id_values, load_json, load_jsonl, now, records_from_json, sha256_file
from sequence_manager import validate_manifest

SOURCES = [
    ('scenes', '02_screenplay/scene_manifest.json', 'json'),
    ('lines', '02_screenplay/line_manifest.jsonl', 'jsonl'),
    ('blocking', '03_preproduction/performance_blocking.jsonl', 'jsonl'),
    ('storyboards', '03_preproduction/storyboards/anchors.jsonl', 'jsonl'),
    ('shots', '04_generation/shot_briefs.jsonl', 'jsonl'),
    ('images', '04_generation/image_briefs.jsonl', 'jsonl'),
    ('voices', '04_generation/voice_cues.jsonl', 'jsonl'),
    ('music', '04_generation/music_cues.jsonl', 'jsonl'),
    ('sound', '04_generation/sfx_cues.jsonl', 'jsonl'),
    ('takes', '04_generation/take_manifest.jsonl', 'jsonl'),
    ('take_qc', '04_generation/take_qc.jsonl', 'jsonl'),
    ('media', '00_project/media_registry.jsonl', 'jsonl'),
    ('timeline', '05_post/timeline.json', 'json'),
]


def read_records(root: Path, rel: str, kind: str) -> list[dict[str, Any]]:
    path = root / rel
    if kind == 'jsonl':
        return load_jsonl(path)
    return records_from_json(load_json(path, {}))


def scoped_canon_and_state(root: Path, active: set[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    canon = load_json(root / '00_project/canon.json', {}) or {}
    story_state = load_json(root / '01_story/story_state.json', {}) or {}
    char_ids = {x for x in active if x.startswith('CHAR-')}
    loc_ids = {x for x in active if x.startswith('LOC-')}
    prop_ids = {x for x in active if x.startswith('PROP-')}

    canon_subset = {
        'characters': {k: v for k, v in (canon.get('characters', {}) or {}).items() if k in char_ids},
        'locations': {k: v for k, v in (canon.get('locations', {}) or {}).items() if k in loc_ids},
        'props': {k: v for k, v in (canon.get('props', {}) or {}).items() if k in prop_ids},
        'relationship_baselines': {},
    }
    baselines = canon.get('relationship_baselines', {}) if isinstance(canon.get('relationship_baselines', {}), dict) else {}
    for key, record in baselines.items():
        pair = record.get('characters', []) if isinstance(record, dict) else []
        if isinstance(pair, list) and len(pair) == 2 and all(cid in char_ids for cid in pair):
            canon_subset['relationship_baselines'][key] = record

    state_characters = {}
    for cid, record in (story_state.get('characters', {}) or {}).items():
        if cid not in char_ids or not isinstance(record, dict):
            continue
        copy = dict(record)
        relationships = copy.get('relationships')
        if isinstance(relationships, dict):
            copy['relationships'] = {target: value for target, value in relationships.items() if target in char_ids}
        state_characters[cid] = copy
    state_subset = {
        'characters': state_characters,
        'props': {k: v for k, v in (story_state.get('props', {}) or {}).items() if k in prop_ids},
    }
    return canon_subset, state_subset


def build_one(root: Path, seq: dict[str, Any], all_sources: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    active: set[str] = set(seq.get('scene_ids') or []) | {seq['sequence_id']}
    selected: dict[str, list[dict[str, Any]]] = {name: [] for name, _, _ in SOURCES}
    selected_keys: dict[str, set[int]] = {name: set() for name, _, _ in SOURCES}
    for _ in range(5):
        changed = False
        for name, _, _ in SOURCES:
            for index, rec in enumerate(all_sources[name]):
                if index in selected_keys[name]:
                    continue
                ids = id_values(rec)
                if ids & active:
                    selected[name].append(rec)
                    selected_keys[name].add(index)
                    before = len(active)
                    active.update(ids)
                    changed = changed or len(active) != before
        if not changed:
            break
    refs = sorted(x for x in active if x.startswith(('CHAR-', 'LOC-', 'PROP-', 'REF-')))
    canon_subset, state_subset = scoped_canon_and_state(root, active)
    source_files = []
    source_paths = [relpath for _, relpath, _ in SOURCES] + ['00_project/canon.json', '01_story/story_state.json']
    for relpath in source_paths:
        path = root / relpath
        if path.is_file():
            source_files.append({'path': relpath, 'sha256': sha256_file(path)})
    return {
        'schema_version': 1,
        'sequence_id': seq['sequence_id'],
        'sequence_status': seq.get('status', 'planned'),
        'scene_ids': seq.get('scene_ids', []),
        'related_ids': sorted(active),
        'reference_ids': refs,
        'records': {name: rows for name, rows in selected.items() if rows},
        'canon': canon_subset,
        'story_state': state_subset,
        'source_snapshots': source_files,
        'generated_at': now(),
        'rule': 'Load this shard first. Load a source file only when the shard points to it or validation requires it.',
    }


def render_md(shard: dict[str, Any]) -> str:
    lines = [
        f"# {shard['sequence_id']} Context Shard",
        '',
        '[Feature-scale guide](../../../docs/production/feature-scale.md) | [Documentation home](../../../docs/README.md)',
        '',
        f"Status: `{shard['sequence_status']}`",
        '',
        '## Scenes', '',
    ]
    lines.extend(f'- `{x}`' for x in shard.get('scene_ids', []))
    lines += ['', '## Record counts', '']
    for name, rows in shard.get('records', {}).items():
        lines.append(f'- {name}: {len(rows)}')
    canon = shard.get('canon', {})
    state = shard.get('story_state', {})
    lines += ['', '## Scoped canon and current state', '']
    lines.append(f"- canon characters: {len(canon.get('characters', {}))}")
    lines.append(f"- canon locations: {len(canon.get('locations', {}))}")
    lines.append(f"- canon props: {len(canon.get('props', {}))}")
    lines.append(f"- relationship baselines: {len(canon.get('relationship_baselines', {}))}")
    lines.append(f"- current character states: {len(state.get('characters', {}))}")
    lines.append(f"- current prop states: {len(state.get('props', {}))}")
    lines += ['', '## Related stable IDs', '']
    ids = shard.get('related_ids', [])
    if ids:
        for i in range(0, len(ids), 12):
            lines.append('- ' + ', '.join(f'`{x}`' for x in ids[i:i+12]))
    else:
        lines.append('- None')
    lines += ['', '## Agent rule', '', 'Use this file as the normal context entry point for this sequence. Do not load the full feature state unless a global gate requires it.', '']
    return '\n'.join(lines)


def build_all(root: Path) -> dict[str, Any]:
    manifest = load_json(root / '00_project/sequence_manifest.json', {}) or {}
    errors = validate_manifest(manifest)
    if errors:
        raise ValueError('; '.join(errors))
    all_sources = {name: read_records(root, relpath, kind) for name, relpath, kind in SOURCES}
    index = {'schema_version': 1, 'generated_at': now(), 'shards': []}
    for seq in manifest.get('sequences', []):
        shard = build_one(root, seq, all_sources)
        folder = root / '00_project/shards' / seq['sequence_id']
        folder.mkdir(parents=True, exist_ok=True)
        atomic_write_json(folder / 'context.json', shard)
        atomic_write_text(folder / 'context.md', render_md(shard))
        index['shards'].append({
            'sequence_id': seq['sequence_id'],
            'path': f"00_project/shards/{seq['sequence_id']}/context.json",
            'markdown': f"00_project/shards/{seq['sequence_id']}/context.md",
            'scene_count': len(seq.get('scene_ids', [])),
            'related_id_count': len(shard.get('related_ids', [])),
        })
    atomic_write_json(root / '00_project/shards/index.json', index)
    md = ['# Context Shard Index', '', '[Documentation home](../../../docs/README.md)', '', '| Sequence | Scenes | Related IDs | Context |', '|---|---:|---:|---|']
    for rec in index['shards']:
        md.append(f"| {rec['sequence_id']} | {rec['scene_count']} | {rec['related_id_count']} | [{rec['sequence_id']}](./{rec['sequence_id']}/context.md) |")
    md += ['', 'Open only the sequence that you need. Open the whole project only for a global check.', '']
    atomic_write_text(root / '00_project/shards/index.md', '\n'.join(md))
    return index


def validate_shards(root: Path) -> list[str]:
    errors = []
    index = load_json(root / '00_project/shards/index.json', {}) or {}
    for rec in index.get('shards', []):
        path = root / rec.get('path', '')
        md = root / rec.get('markdown', '')
        if not path.is_file(): errors.append(f"missing shard {rec.get('sequence_id')}: {rec.get('path')}")
        if not md.is_file(): errors.append(f"missing shard Markdown {rec.get('sequence_id')}: {rec.get('markdown')}")
        if path.is_file():
            value = load_json(path, {}) or {}
            if value.get('sequence_id') != rec.get('sequence_id'):
                errors.append(f"{rec.get('sequence_id')}: shard identity mismatch")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description='Build feature-scale per-sequence context shards.')
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('build', 'validate'):
        p = sub.add_parser(name); p.add_argument('project')
    args = ap.parse_args()
    root = Path(args.project).expanduser().resolve()
    try:
        if args.cmd == 'build':
            value = build_all(root)
            print(json.dumps({'shards': len(value['shards'])}, indent=2))
        else:
            errors = validate_shards(root)
            if errors:
                for error in errors: print('ERROR', error)
                return 1
            print('OK context shards')
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print('ERROR', exc)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
