#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line_no, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f'{path}: invalid JSONL line {line_no}: {exc}') from exc
        if not isinstance(value, dict):
            raise ValueError(f'{path}: JSONL line {line_no} must be an object')
        out.append(value)
    return out


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f'.{path.name}.', dir=str(path.parent))
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        try:
            dir_fd = os.open(path.parent, os.O_DIRECTORY)
        except (AttributeError, OSError):
            return
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if tmp.exists():
            tmp.unlink()


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8', newline='\n') as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + '\n')
        handle.flush()
        os.fsync(handle.fileno())


def safe_rel(root: Path, value: str | Path) -> Path:
    p = Path(value)
    if p.is_absolute():
        raise ValueError(f'project path must be relative: {value}')
    resolved = (root / p).resolve()
    root_resolved = root.resolve()
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(f'project path escapes project root: {value}') from exc
    return resolved


def rel(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def id_values(value: Any) -> set[str]:
    out: set[str] = set()
    if isinstance(value, str):
        import re
        out.update(re.findall(r'\b(?:SEQ|SCN|SHOT|LINE|TAKE|MEDIA|CHAR|LOC|PROP|REF|VOICE|MUS|SFX|AUD|EVT|MASTER|TRL|SOC|COPY|DELIV|JOB|BATCH|UNIT|DEC)-\d{3,}\b', value))
    elif isinstance(value, dict):
        for v in value.values():
            out.update(id_values(v))
    elif isinstance(value, list):
        for v in value:
            out.update(id_values(v))
    return out


def records_from_json(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    if not isinstance(value, dict):
        return []
    for key in ('scenes', 'shots', 'events', 'records', 'items', 'sequences', 'jobs', 'deliverables'):
        items = value.get(key)
        if isinstance(items, list):
            return [x for x in items if isinstance(x, dict)]
    if value and all(isinstance(v, dict) for v in value.values()):
        out = []
        for key, rec in value.items():
            item = dict(rec)
            if not any(str(v).startswith(('SCN-', 'SHOT-', 'SEQ-', 'LINE-', 'MEDIA-')) for v in item.values() if isinstance(v, str)):
                item.setdefault('id', key)
            out.append(item)
        return out
    return []


def first_id(record: dict[str, Any], prefixes: Iterable[str]) -> str:
    for key in ('sequence_id', 'scene_id', 'shot_id', 'line_id', 'media_id', 'take_id', 'event_id', 'job_id', 'id'):
        value = record.get(key)
        if isinstance(value, str) and any(value.startswith(p) for p in prefixes):
            return value
    for token in sorted(id_values(record)):
        if any(token.startswith(p) for p in prefixes):
            return token
    return ''
