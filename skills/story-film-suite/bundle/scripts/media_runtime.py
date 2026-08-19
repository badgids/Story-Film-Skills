#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path, PurePosixPath


class MediaRuntimeError(RuntimeError):
    pass


def portable_rel(value: str) -> bool:
    if not isinstance(value, str) or not value or value.startswith('/') or value.startswith('~'):
        return False
    normalized = value.replace('\\', '/')
    if len(normalized) >= 3 and normalized[1:3] == ':/':
        return False
    p = PurePosixPath(normalized)
    return not p.is_absolute() and '..' not in p.parts


def project_root(value: str | Path) -> Path:
    return Path(value).expanduser().resolve()


def project_path(root: Path, rel: str, *, must_exist: bool = False) -> Path:
    if not portable_rel(rel):
        raise MediaRuntimeError(f'path must be project-relative without parent traversal: {rel!r}')
    path = (root / PurePosixPath(rel.replace('\\', '/'))).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise MediaRuntimeError(f'path escapes project root: {rel!r}') from exc
    if must_exist and not path.exists():
        raise MediaRuntimeError(f'missing media: {rel}')
    return path


def read_json(path: Path):
    with path.open(encoding='utf-8') as f:
        return json.load(f)


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def tool(name: str) -> str:
    found = shutil.which(name)
    if not found:
        raise MediaRuntimeError(f'required runtime executable not found: {name}')
    return found


def run(argv: list[str], *, capture: bool = False) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            argv,
            check=True,
            text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
        )
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or '').strip()
        raise MediaRuntimeError(f'command failed ({exc.returncode}): {detail}') from exc


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def ffprobe(path: Path) -> dict:
    proc = run([
        tool('ffprobe'), '-v', 'error', '-print_format', 'json',
        '-show_format', '-show_streams', str(path)
    ], capture=True)
    try:
        return json.loads(proc.stdout or '{}')
    except json.JSONDecodeError as exc:
        raise MediaRuntimeError(f'ffprobe returned invalid JSON for {path.name}') from exc


def frame_rate(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text or text == '0/0':
        return 0.0
    try:
        return float(Fraction(text))
    except Exception:
        try:
            return float(text)
        except Exception:
            return 0.0


def db_to_linear(db: float) -> float:
    return math.pow(10.0, float(db) / 20.0)


ASPECT_PROFILES = {
    '16:9': (1920, 1080),
    '9:16': (1080, 1920),
    '1:1': (1080, 1080),
    '4:5': (1080, 1350),
}
