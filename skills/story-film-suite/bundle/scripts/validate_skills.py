#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
NAME_RX = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

def frontmatter(text: str):
    if not text.startswith('---\n'):
        return None
    end = text.find('\n---\n', 4)
    if end < 0:
        return None
    raw = text[4:end]
    if yaml is not None:
        try:
            out = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            raise ValueError(f'invalid YAML frontmatter: {exc}') from exc
        if not isinstance(out, dict):
            raise ValueError('frontmatter must be a YAML mapping')
        return out

    # Dependency-free fallback for normal installations. This does not try to
    # implement all YAML. It rejects the common unsafe plain-scalar pattern
    # that Pi's YAML parser also rejects, including an unquoted ': ' value.
    out = {}
    for line in raw.splitlines():
        if ':' not in line:
            continue
        k, v = line.split(':', 1)
        value = v.strip()
        if value and value[0] not in {'"', "'", '[', '{'} and ': ' in value:
            raise ValueError(f'unsafe unquoted YAML scalar for {k.strip()!r}; quote values containing colon-space')
        out[k.strip()] = value.strip('"\'')
    return out

def main():
    errors = []
    skills = sorted((ROOT / 'skills').glob('*/SKILL.md'))
    if not skills:
        errors.append('no skills found')
    for p in skills:
        try:
            fm = frontmatter(p.read_text(encoding='utf-8'))
        except ValueError as exc:
            errors.append(f'{p}: {exc}')
            continue
        if fm is None:
            errors.append(f'{p}: missing or malformed frontmatter')
            continue
        name = fm.get('name', '')
        desc = fm.get('description', '')
        if not NAME_RX.match(name):
            errors.append(f'{p}: invalid name {name!r}')
        if name != p.parent.name:
            errors.append(f'{p}: name does not match parent directory')
        if len(name) > 64:
            errors.append(f'{p}: name longer than 64 chars')
        if not desc:
            errors.append(f'{p}: missing description')
        if len(desc) > 1024:
            errors.append(f'{p}: description longer than 1024 chars')
    for p in ROOT.rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.md', '.txt', '.py', '.sh', '.json', '.jsonl', '.csv'}:
            # Bundled and user-supplied ComfyUI workflow JSON is imported executable/source
            # asset content, not Story-Film-authored prose. Preserve it exactly instead of
            # applying documentation typography rules to workflow prompts, notes, or metadata.
            if 'comfyui_workflows' in p.parts:
                continue
            try:
                text = p.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                continue
            if '\u2014' in text:
                errors.append(f'{p}: contains em dash')
    for e in errors:
        print('ERROR', e)
    if errors:
        raise SystemExit(1)
    print(f'OK: {len(skills)} skills validated')

if __name__ == '__main__':
    main()
