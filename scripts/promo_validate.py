#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from media_runtime import ASPECT_PROFILES, MediaRuntimeError, portable_rel, project_path, project_root, read_json
from render_timeline import validate_timeline

TRL_RX = re.compile(r'^TRL-\d{3,}$')
SOC_RX = re.compile(r'^SOC-\d{3,}$')
CAMP_RX = re.compile(r'^CAMP-\d{3,}$')
COPY_RX = re.compile(r'^COPY-\d{3,}$')


def aspect_ratio_value(value: str) -> float | None:
    if value in ASPECT_PROFILES:
        w, h = ASPECT_PROFILES[value]
        return w / h
    if isinstance(value, str) and re.fullmatch(r'\d+(?:\.\d+)?:\d+(?:\.\d+)?', value):
        a, b = value.split(':', 1)
        bval = float(b)
        return float(a) / bval if bval else None
    return None


def aspect_matches(width: int, height: int, aspect: str, tolerance: float = 0.01) -> bool:
    target = aspect_ratio_value(aspect)
    if target is None or height <= 0:
        return False
    return abs((width / height) - target) <= tolerance


def jsonl(path: Path, errors: list[str]) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f'{path.name}:{n}: invalid JSON: {exc}')
            continue
        if not isinstance(obj, dict):
            errors.append(f'{path.name}:{n}: record must be an object')
            continue
        rows.append(obj)
    return rows


def validate_trailers(root: Path) -> list[str]:
    errors = []
    path = root / '06_release/trailers/trailer_manifest.json'
    if not path.exists():
        return errors
    obj = read_json(path)
    if obj.get('schema_version') != 1:
        errors.append('trailer_manifest.json: unsupported schema_version')
    camp = obj.get('campaign_id')
    if camp and not CAMP_RX.fullmatch(str(camp)):
        errors.append(f'trailer_manifest.json: invalid campaign_id {camp!r}')
    rows = obj.get('trailers')
    if not isinstance(rows, list):
        errors.append('trailer_manifest.json: trailers must be an array')
        return errors
    seen = set()
    for i, rec in enumerate(rows, 1):
        tid = rec.get('trailer_id', '') if isinstance(rec, dict) else ''
        if not isinstance(rec, dict):
            errors.append(f'trailer {i}: must be object')
            continue
        if not TRL_RX.fullmatch(tid):
            errors.append(f'trailer {i}: invalid trailer_id {tid!r}')
        elif tid in seen:
            errors.append(f'trailer {i}: duplicate trailer_id {tid}')
        seen.add(tid)
        target = rec.get('target_duration')
        tol = rec.get('duration_tolerance', 2.0)
        if not isinstance(target, (int, float)) or isinstance(target, bool) or target <= 0:
            errors.append(f'{tid}: target_duration must be positive')
        if not isinstance(tol, (int, float)) or isinstance(tol, bool) or tol < 0:
            errors.append(f'{tid}: duration_tolerance must be nonnegative')
        if not rec.get('spoiler_policy'):
            errors.append(f'{tid}: missing spoiler_policy')
        if not isinstance(rec.get('structure', []), list) or not rec.get('structure'):
            errors.append(f'{tid}: structure must be nonempty array')
        for field in ['timeline_path', 'audio_mix_path', 'output_path']:
            value = rec.get(field)
            if not isinstance(value, str) or not portable_rel(value):
                errors.append(f'{tid}: invalid {field} {value!r}')
        tl_rel = rec.get('timeline_path')
        if isinstance(tl_rel, str) and portable_rel(tl_rel):
            tl = project_path(root, tl_rel)
            if tl.exists():
                tlo = read_json(tl)
                for msg in validate_timeline(root, tlo, require_sources=False):
                    errors.append(f'{tid} timeline: {msg}')
                if tlo.get('timeline_id') != tid:
                    errors.append(f'{tid}: timeline_id does not match trailer_id')
                if tlo.get('output_path') != rec.get('output_path'):
                    errors.append(f'{tid}: timeline output_path does not match trailer output_path')
                aspect = rec.get('aspect_ratio')
                tvideo = tlo.get('video', {}) if isinstance(tlo.get('video'), dict) else {}
                if aspect:
                    ratio = aspect_ratio_value(str(aspect))
                    if ratio is None:
                        errors.append(f'{tid}: invalid aspect_ratio {aspect!r}')
                    elif isinstance(tvideo.get('width'), int) and isinstance(tvideo.get('height'), int) and not aspect_matches(tvideo['width'], tvideo['height'], str(aspect)):
                        errors.append(f'{tid}: timeline dimensions do not match aspect_ratio {aspect}')
                if isinstance(target, (int, float)) and isinstance(tol, (int, float)) and isinstance(tlo.get('events'), list):
                    planned = sum(float(x.get('duration', 0)) for x in tlo['events'] if isinstance(x, dict) and isinstance(x.get('duration'), (int, float)))
                    if abs(planned - float(target)) > float(tol):
                        errors.append(f'{tid}: planned timeline duration {planned:.3f}s outside target {float(target):.3f}s +/- {float(tol):.3f}s')
    return errors


def validate_social(root: Path) -> list[str]:
    errors = []
    campaign_path = root / '06_release/social/campaign.json'
    deliverables_path = root / '06_release/social/deliverables.jsonl'
    if campaign_path.exists():
        obj = read_json(campaign_path)
        if obj.get('schema_version') != 1:
            errors.append('social/campaign.json: unsupported schema_version')
        cid = obj.get('campaign_id', '')
        if not CAMP_RX.fullmatch(str(cid)):
            errors.append(f'social/campaign.json: invalid campaign_id {cid!r}')
        for field in ['verified_release_facts', 'unresolved_release_facts', 'content_pillars', 'platforms']:
            if field in obj and not isinstance(obj[field], (dict if field.endswith('facts') else list)):
                errors.append(f'social/campaign.json: {field} has wrong type')
    seen = set()
    for i, rec in enumerate(jsonl(deliverables_path, errors), 1):
        sid = rec.get('social_id', '')
        if not SOC_RX.fullmatch(str(sid)):
            errors.append(f'deliverables.jsonl:{i}: invalid social_id {sid!r}')
        elif sid in seen:
            errors.append(f'deliverables.jsonl:{i}: duplicate social_id {sid}')
        seen.add(sid)
        if rec.get('media_type') not in {'video', 'image', 'copy', 'audio', 'package'}:
            errors.append(f'{sid}: invalid media_type {rec.get("media_type")!r}')
        aspect = rec.get('aspect_ratio')
        if aspect and aspect not in ASPECT_PROFILES and not re.fullmatch(r'\d+(?:\.\d+)?:\d+(?:\.\d+)?', str(aspect)):
            errors.append(f'{sid}: invalid aspect_ratio {aspect!r}')
        if rec.get('media_type') == 'video':
            target = rec.get('target_duration')
            tol = rec.get('duration_tolerance', 1.0)
            if not isinstance(target, (int, float)) or isinstance(target, bool) or target <= 0:
                errors.append(f'{sid}: video target_duration must be positive')
            if not isinstance(tol, (int, float)) or isinstance(tol, bool) or tol < 0:
                errors.append(f'{sid}: duration_tolerance must be nonnegative')
            tl = rec.get('timeline_path')
            if tl and not portable_rel(tl):
                errors.append(f'{sid}: timeline_path must be portable')
            elif tl:
                tl_path = project_path(root, tl)
                if tl_path.exists():
                    tlo = read_json(tl_path)
                    for msg in validate_timeline(root, tlo, require_sources=False):
                        errors.append(f'{sid} timeline: {msg}')
                    if tlo.get('timeline_id') != sid:
                        errors.append(f'{sid}: timeline_id does not match social_id')
                    if tlo.get('output_path') != rec.get('output_path'):
                        errors.append(f'{sid}: timeline output_path does not match social output_path')
                    tvideo = tlo.get('video', {}) if isinstance(tlo.get('video'), dict) else {}
                    if aspect and isinstance(tvideo.get('width'), int) and isinstance(tvideo.get('height'), int) and not aspect_matches(tvideo['width'], tvideo['height'], str(aspect)):
                        errors.append(f'{sid}: timeline dimensions do not match aspect_ratio {aspect}')
                    if isinstance(target, (int, float)) and isinstance(tol, (int, float)) and isinstance(tlo.get('events'), list):
                        planned = sum(float(x.get('duration', 0)) for x in tlo['events'] if isinstance(x, dict) and isinstance(x.get('duration'), (int, float)))
                        if abs(planned - float(target)) > float(tol):
                            errors.append(f'{sid}: planned timeline duration {planned:.3f}s outside target {float(target):.3f}s +/- {float(tol):.3f}s')
        out = rec.get('output_path')
        if out and not portable_rel(out):
            errors.append(f'{sid}: output_path must be portable')
        copy_id = rec.get('copy_id')
        if copy_id and not COPY_RX.fullmatch(str(copy_id)):
            errors.append(f'{sid}: invalid copy_id {copy_id!r}')
        if not isinstance(rec.get('source_ids', []), list):
            errors.append(f'{sid}: source_ids must be an array')
    copy_path = root / '06_release/social/copy.jsonl'
    copy_seen = set()
    for i, rec in enumerate(jsonl(copy_path, errors), 1):
        cid = rec.get('copy_id', '')
        if not COPY_RX.fullmatch(str(cid)):
            errors.append(f'copy.jsonl:{i}: invalid copy_id {cid!r}')
        elif cid in copy_seen:
            errors.append(f'copy.jsonl:{i}: duplicate copy_id {cid}')
        copy_seen.add(cid)
        if not isinstance(rec.get('verified_facts_used', []), list):
            errors.append(f'copy.jsonl:{i}: verified_facts_used must be an array')
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description='Validate trailer and social campaign manifests.')
    ap.add_argument('project_dir')
    ap.add_argument('--scope', choices=['all', 'trailers', 'social'], default='all')
    args = ap.parse_args()
    root = project_root(args.project_dir)
    errors = []
    if args.scope in {'all', 'trailers'}:
        errors.extend(validate_trailers(root))
    if args.scope in {'all', 'social'}:
        errors.extend(validate_social(root))
    for e in errors:
        print('ERROR', e)
    if errors:
        return 1
    print('OK: promotional manifests valid')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except MediaRuntimeError as exc:
        print(f'ERROR {exc}')
        raise SystemExit(2)
