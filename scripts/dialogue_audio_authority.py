#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def safe_project_path(root: Path, rel: str) -> Path | None:
    candidate = (root / rel).resolve()
    resolved_root = root.resolve()
    return candidate if candidate != resolved_root and resolved_root in candidate.parents else None


def line_manifest(root: Path) -> dict[str, dict]:
    path = root / '02_screenplay/line_manifest.jsonl'
    return {row.get('line_id'): row for row in read_jsonl(path) if isinstance(row, dict) and isinstance(row.get('line_id'), str)}


def media_registry(root: Path) -> dict[str, dict]:
    path = root / '00_project/media_registry.jsonl'
    return {row.get('media_id'): row for row in read_jsonl(path) if isinstance(row, dict) and isinstance(row.get('media_id'), str)}


def validate_project(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / '04_generation/dialogue_audio_authority.jsonl'
    try:
        data = read_jsonl(path)
        lines = line_manifest(root)
        media = media_registry(root)
    except Exception as exc:
        return [f'{path.relative_to(root)}: {exc}']

    seen: set[str] = set()
    for row_number, record in enumerate(data, 1):
        line_id = record.get('line_id')
        media_id = record.get('approved_audio_media_id')
        speaker_id = record.get('speaker_id')
        if not isinstance(line_id, str) or not line_id.startswith('LINE-'):
            errors.append(f'row {row_number}: invalid line_id')
        elif line_id in seen:
            errors.append(f'row {row_number}: duplicate line_id {line_id}')
        seen.add(line_id)
        if not isinstance(media_id, str) or not media_id.startswith('MEDIA-'):
            errors.append(f'row {row_number}: approved_audio_media_id required')
        if not isinstance(speaker_id, str) or not speaker_id.startswith('CHAR-'):
            errors.append(f'row {row_number}: speaker_id must be CHAR-###')
        if record.get('generation_audio_authority') != 'approved-dialogue' or record.get('review_audio_authority') != 'approved-dialogue':
            errors.append(f'row {row_number}: generation/review authority must both be approved-dialogue')
        start = record.get('start_seconds', 0)
        if not isinstance(start, (int, float)) or start < 0:
            errors.append(f'row {row_number}: invalid start_seconds')

        source_line = lines.get(line_id)
        if source_line is not None:
            manifest_speaker = source_line.get('speaker_id') or source_line.get('character_id')
            if manifest_speaker and manifest_speaker != speaker_id:
                errors.append(f'row {row_number}: speaker_id disagrees with line manifest for {line_id}')

        source_media = media.get(media_id)
        if media and source_media is None:
            errors.append(f'row {row_number}: unknown approved_audio_media_id {media_id}')
        elif source_media is not None and source_media.get('status') not in {'primary', 'alternate'}:
            errors.append(f'row {row_number}: approved audio media must be primary or alternate')

        rel = record.get('path')
        expected = record.get('audio_sha256')
        if source_media is not None and isinstance(rel, str) and source_media.get('path') and source_media.get('path') != rel:
            errors.append(f'row {row_number}: path disagrees with media registry for {media_id}')
        if isinstance(rel, str) and rel:
            candidate = safe_project_path(root, rel)
            if candidate is None:
                errors.append(f'row {row_number}: path escapes project')
            elif candidate.exists() and expected and digest(candidate) != expected:
                errors.append(f'row {row_number}: approved audio hash mismatch')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate approved dialogue-audio authority records.')
    parser.add_argument('project_dir')
    args = parser.parse_args()
    errors = validate_project(Path(args.project_dir).resolve())
    for error in errors:
        print('ERROR', error)
    print('OK dialogue audio authority' if not errors else f'FAILED {len(errors)}')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
