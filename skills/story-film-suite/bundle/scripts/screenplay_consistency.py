#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Validate Fountain dialogue against canonical characters and line_manifest.jsonl.

This verifier is project-generic. It never hardcodes character names.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
from dataclasses import dataclass
from pathlib import Path

SCENE_HEADING_RX = re.compile(r"^(?:\.|(?:INT|EXT|EST|INT/EXT|EXT/INT|I/E)\.?\b)", re.IGNORECASE)
TRANSITION_RX = re.compile(r"^(?:FADE (?:IN|OUT)|CUT TO|SMASH CUT TO|DISSOLVE TO|MATCH CUT TO|WIPE TO|THE END)\s*:?$", re.IGNORECASE)
CHARACTER_CUE_RX = re.compile(r"^@?[A-Z0-9][A-Z0-9 ._'\-]*(?:\s*\([^\n()]+\))*\^?$")
EXTENSION_RX = re.compile(r"\s*\([^()]+\)\s*$")


@dataclass(frozen=True)
class Dialogue:
    cue: str
    text: str
    source_line: int


def _normalized_name(value: str) -> str:
    value = value.strip().lstrip('@').rstrip('^').strip()
    while True:
        updated = EXTENSION_RX.sub('', value).strip()
        if updated == value:
            break
        value = updated
    return re.sub(r"\s+", " ", value).upper()


def _looks_like_character_cue(line: str, next_line: str) -> bool:
    cue = line.strip()
    if not cue or not next_line.strip():
        return False
    if SCENE_HEADING_RX.match(cue) or TRANSITION_RX.match(cue):
        return False
    if cue.startswith('>') and cue.endswith('<'):
        return False
    if cue.endswith(':'):
        return False
    return bool(CHARACTER_CUE_RX.fullmatch(cue))


def parse_fountain_dialogue(path: Path) -> list[Dialogue]:
    lines = path.read_text(encoding='utf-8').splitlines()
    out: list[Dialogue] = []
    i = 0
    while i < len(lines):
        raw = lines[i]
        nxt = lines[i + 1] if i + 1 < len(lines) else ''
        if not _looks_like_character_cue(raw, nxt):
            i += 1
            continue

        cue = _normalized_name(raw)
        j = i + 1
        spoken: list[str] = []
        while j < len(lines) and lines[j].strip():
            part = lines[j].strip()
            # Fountain parentheticals are performance direction, not spoken text.
            if not (part.startswith('(') and part.endswith(')')):
                spoken.append(part)
            j += 1
        if spoken:
            out.append(Dialogue(cue=cue, text=' '.join(spoken), source_line=i + 1))
        i = max(j, i + 1)
    return out


def load_manifest_dialogue(path: Path) -> list[dict]:
    out: list[dict] = []
    if not path.exists():
        return out
    for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        obj = json.loads(line)
        if obj.get('kind') == 'dialogue':
            rec = dict(obj)
            rec['_manifest_line'] = n
            out.append(rec)
    return out


def canonical_character_aliases(canon: dict) -> tuple[dict[str, str], dict[str, str], list[str]]:
    """Return alias->CHAR id, id->display name, and configuration errors."""
    chars = canon.get('characters', {})
    if not isinstance(chars, dict):
        return {}, {}, ['canon.characters must be an object']

    names: dict[str, str] = {}
    explicit: dict[str, list[str]] = {}
    first_name_counts: dict[str, int] = {}
    errors: list[str] = []

    for cid, rec in chars.items():
        if not isinstance(rec, dict):
            continue
        name = rec.get('name')
        if not isinstance(name, str) or not name.strip():
            continue
        names[cid] = name.strip()
        aliases = [name.strip()]
        for field in ('screenplay_names', 'aliases'):
            vals = rec.get(field, [])
            if isinstance(vals, str):
                vals = [vals]
            if isinstance(vals, list):
                aliases.extend(str(v).strip() for v in vals if str(v).strip())
        explicit[cid] = aliases
        first = _normalized_name(name).split(' ', 1)[0]
        first_name_counts[first] = first_name_counts.get(first, 0) + 1

    alias_to_id: dict[str, str] = {}
    for cid, aliases in explicit.items():
        full_name = names[cid]
        normalized_aliases = {_normalized_name(v) for v in aliases if _normalized_name(v)}
        first = _normalized_name(full_name).split(' ', 1)[0]
        if first_name_counts.get(first) == 1:
            normalized_aliases.add(first)
        for alias in sorted(normalized_aliases):
            prior = alias_to_id.get(alias)
            if prior and prior != cid:
                errors.append(f'character alias {alias!r} is ambiguous between {prior} and {cid}')
            else:
                alias_to_id[alias] = cid
    return alias_to_id, names, errors


def validate_project(root: Path) -> list[str]:
    screenplay = root / '02_screenplay/screenplay.fountain'
    manifest = root / '02_screenplay/line_manifest.jsonl'
    canon_path = root / '00_project/canon.json'
    if not screenplay.exists() or not manifest.exists():
        return []
    if not canon_path.exists():
        return ['screenplay consistency: missing 00_project/canon.json']

    canon = json.loads(canon_path.read_text(encoding='utf-8'))
    aliases, names, errors = canonical_character_aliases(canon)
    fountain = parse_fountain_dialogue(screenplay)
    manifest_rows = load_manifest_dialogue(manifest)

    known_aliases = sorted(aliases)
    # Older or partially initialized projects can have an empty canon. In that
    # case text/count checks still run, but speaker identity waits until canon
    # contains characters.
    if known_aliases:
        for entry in fountain:
            if entry.cue in aliases:
                continue
            close = difflib.get_close_matches(entry.cue, known_aliases, n=1, cutoff=0.72)
            if close:
                suggestion = close[0]
                cid = aliases[suggestion]
                display = names.get(cid, cid)
                errors.append(
                    f'screenplay.fountain:{entry.source_line}: unknown dialogue cue {entry.cue!r}; '
                    f'did you mean {suggestion!r} ({cid}, {display})?'
                )
            else:
                errors.append(f'screenplay.fountain:{entry.source_line}: dialogue cue {entry.cue!r} does not resolve to canon.characters')

    if len(fountain) != len(manifest_rows):
        errors.append(
            f'screenplay dialogue count {len(fountain)} does not match line manifest dialogue count {len(manifest_rows)}'
        )

    for index, (screen, manifest_row) in enumerate(zip(fountain, manifest_rows), 1):
        line_id = manifest_row.get('line_id', f'dialogue #{index}')
        expected_text = manifest_row.get('text')
        if screen.text != expected_text:
            errors.append(
                f'{line_id}: dialogue text mismatch; screenplay line {screen.source_line} has {screen.text!r}, '
                f'manifest line {manifest_row.get("_manifest_line")} has {expected_text!r}'
            )
        cid = manifest_row.get('character_id')
        resolved = aliases.get(screen.cue)
        if resolved and isinstance(cid, str) and cid and resolved != cid:
            errors.append(
                f'{line_id}: speaker mismatch; screenplay cue {screen.cue!r} resolves to {resolved}, manifest uses {cid}'
            )

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description='Validate Fountain dialogue and speaker identity against Story-Film canon and line manifest.')
    ap.add_argument('project_dir')
    args = ap.parse_args()
    root = Path(args.project_dir).expanduser().resolve()
    errors = validate_project(root)
    if errors:
        for error in errors:
            print('ERROR', error)
        return 1
    screenplay = root / '02_screenplay/screenplay.fountain'
    manifest = root / '02_screenplay/line_manifest.jsonl'
    if screenplay.exists() and manifest.exists():
        print(f'OK screenplay consistency: {len(parse_fountain_dialogue(screenplay))} dialogue blocks match canon and line manifest')
    else:
        print('OK screenplay consistency: screenplay or line manifest not present; nothing to compare')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
