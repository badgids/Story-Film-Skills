#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath
from pipeline_progress import validate_progress as validate_pipeline_progress

from audio_master import validate_manifest as validate_audio_mix
from media_registry import load_approvals as load_media_approvals, load_records as load_media_records, validate as validate_media_registry
from promo_validate import validate_social as validate_social_campaign, validate_trailers as validate_trailer_campaign
from release_package import validate_manifest as validate_release_manifest
from render_timeline import validate_timeline as validate_executable_timeline
from editor_project_export import validate_editor_project
from claim_ledger import load_jsonl as load_claim_rows, validate as validate_claim_ledger
from campaign_content import validate as validate_campaign_content
from production_documents import load_manifest as load_document_manifest, validate_manifest as validate_document_manifest
from motion_graphics import validate_manifest as validate_motion_graphics
from remotion_adapter import read_manifest as read_programmatic_manifest, validate as validate_programmatic_manifest
from design_system import validate as validate_design_system
from work_units import validate as validate_work_units
from decision_map import validate as validate_decision_map
from document_companions import audit as audit_document_companions
from comfyui_batch import load_manifest as load_offline_batch, validate as validate_offline_batch
from sequence_manager import validate_manifest as validate_sequence_manifest
from context_shards import validate_shards as validate_context_shards

ID_RX = re.compile(r'^(CHAR|LOC|PROP|CH|SCN|LINE|SHOT|VOICE|MUS|SFX|REF|QST|PROM|TAKE|MEDIA|AUD|EVT|MASTER|TRL|CAMP|SOC|COPY|DELIV|TOOL|CLIP|EDIT|SRC|CLAIM|GFX|COMP|CONTENT|DOC|DEC|UNIT|BATCH|JOB|UP|WIZ|SEQ|CONT)-\d{3,}$')


def load_json(path: Path):
    with path.open(encoding='utf-8') as f:
        return json.load(f)


def validate_jsonl(path: Path, errors: list[str]):
    rows = []
    if not path.exists():
        return rows
    for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append((n, json.loads(line)))
        except json.JSONDecodeError as exc:
            errors.append(f'{path.name}:{n}: invalid json: {exc}')
    return rows


def portable_path(value: str) -> bool:
    if not value:
        return True
    if value.startswith('/') or value.startswith('~'):
        return False
    if re.match(r'^[A-Za-z]:[\\/]', value):
        return False
    try:
        return not PurePosixPath(value.replace('\\', '/')).is_absolute()
    except Exception:
        return False


def walk_strings(obj, prefix=''):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from walk_strings(value, f'{prefix}.{key}' if prefix else str(key))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from walk_strings(value, f'{prefix}[{i}]')
    elif isinstance(obj, str):
        yield prefix, obj


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('project_dir')
    args = ap.parse_args()
    root = Path(args.project_dir).expanduser().resolve()
    errors = []

    required = [
        '00_project/state.json',
        '00_project/canon.json',
        '00_project/dependencies.json',
        '03_preproduction/references/reference_manifest.json',
    ]
    for rel in required:
        if not (root / rel).exists():
            errors.append(f'missing {rel}')

    # Durable planning artifacts. They may remain empty until the user chooses these workflows.
    sequence_manifest_path = root / '00_project/sequence_manifest.json'
    if sequence_manifest_path.exists():
        try:
            sequence_doc = load_json(sequence_manifest_path)
            if isinstance(sequence_doc.get('sequences'), list) and sequence_doc.get('sequences'):
                errors.extend(f'sequence manifest: {e}' for e in validate_sequence_manifest(sequence_doc))
                errors.extend(f'context shards: {e}' for e in validate_context_shards(root))
        except Exception as exc:
            errors.append(f'00_project/sequence_manifest.json: {exc}')

    work_units_path = root / '00_project/work_units.json'
    if work_units_path.exists():
        try:
            errors.extend(f'work units: {e}' for e in validate_work_units(load_json(work_units_path)))
        except Exception as exc:
            errors.append(f'00_project/work_units.json: {exc}')
    decision_map_path = root / '00_project/decision_map.json'
    if decision_map_path.exists():
        try:
            errors.extend(f'decision map: {e}' for e in validate_decision_map(load_json(decision_map_path)))
        except Exception as exc:
            errors.append(f'00_project/decision_map.json: {exc}')

    # Every rich/binary document artifact must have a human-readable Markdown companion.
    for rel in audit_document_companions(root):
        errors.append(f'{rel}: missing Markdown companion {Path(rel).with_suffix(".md").as_posix()}')

    # Evidence-backed public claims. Optional until used.
    claims_path = root / '01_story/research/claims.jsonl'
    if claims_path.exists():
        try:
            errors.extend(f'claims: {e}' for e in validate_claim_ledger(load_claim_rows(claims_path)))
        except Exception as exc:
            errors.append(f'01_story/research/claims.jsonl: {exc}')

    # Campaign brand/content lineage. Optional until campaign work exists.
    if any((root / rel).exists() for rel in [
        '06_release/social/brand_voice.json',
        '06_release/social/content_lineage.jsonl',
        '06_release/social/copy.jsonl',
    ]):
        try:
            errors.extend(f'campaign content: {e}' for e in validate_campaign_content(root))
        except Exception as exc:
            errors.append(f'campaign content validation failed: {exc}')

    # Motion-graphics manifest. Optional until requested.
    graphics_path = root / '05_post/graphics/graphics.json'
    if graphics_path.exists():
        try:
            graphics_obj = load_json(graphics_path)
            errors.extend(f'motion graphics: {e}' for e in validate_motion_graphics(graphics_obj))
        except Exception as exc:
            errors.append(f'05_post/graphics/graphics.json: {exc}')

    # Programmatic composition manifests. Optional until requested.
    compositions_path = root / '05_post/programmatic/compositions.json'
    if compositions_path.exists():
        try:
            compositions_obj = read_programmatic_manifest(compositions_path)
            errors.extend(f'programmatic video: {e}' for e in validate_programmatic_manifest(compositions_obj))
        except Exception as exc:
            errors.append(f'05_post/programmatic/compositions.json: {exc}')

    # Reusable release design system. Optional until requested.
    design_system_path = root / '06_release/artwork/design_system.json'
    if design_system_path.exists():
        try:
            errors.extend(f'design system: {e}' for e in validate_design_system(load_json(design_system_path)))
        except Exception as exc:
            errors.append(f'06_release/artwork/design_system.json: {exc}')

    # Production-document manifest. Optional until requested.
    document_manifest_path = root / '00_project/document_manifest.json'
    if document_manifest_path.exists():
        try:
            doc_manifest = load_document_manifest(document_manifest_path)
            errors.extend(f'document manifest: {e}' for e in validate_document_manifest(root, doc_manifest))
        except Exception as exc:
            errors.append(f'00_project/document_manifest.json: {exc}')

    if errors:
        for e in errors:
            print('ERROR', e)
        return 1

    state = load_json(root / '00_project/state.json')
    canon = load_json(root / '00_project/canon.json')
    deps = load_json(root / '00_project/dependencies.json')
    refs = load_json(root / '03_preproduction/references/reference_manifest.json')

    for label, obj in [('state', state), ('canon', canon), ('dependencies', deps), ('reference manifest', refs)]:
        if obj.get('schema_version') != 1:
            errors.append(f'unsupported {label} schema_version')

    known_ids = set()
    for group in ['characters', 'locations', 'props']:
        obj = canon.get(group, {})
        if not isinstance(obj, dict):
            errors.append(f'canon.{group} must be an object')
            continue
        for ident in obj:
            if not ID_RX.match(ident):
                errors.append(f'invalid canon id {ident}')
            known_ids.add(ident)

    ref_ids = set()
    records = refs.get('references', [])
    if not isinstance(records, list):
        errors.append('reference_manifest.references must be an array')
        records = []
    for i, rec in enumerate(records, 1):
        if not isinstance(rec, dict):
            errors.append(f'reference manifest entry {i} must be an object')
            continue
        rid = rec.get('ref_id', '')
        if not rid.startswith('REF-') or not ID_RX.match(rid):
            errors.append(f'reference manifest entry {i}: invalid ref_id {rid!r}')
        if rid in ref_ids:
            errors.append(f'reference manifest entry {i}: duplicate ref_id {rid}')
        ref_ids.add(rid)
        if not rec.get('role'):
            errors.append(f'reference manifest entry {i}: missing role')
        if rec.get('status') not in {None, 'draft', 'approved', 'superseded', 'rejected'}:
            errors.append(f'reference manifest entry {i}: invalid status {rec.get("status")!r}')
        path = rec.get('path')
        if isinstance(path, str) and not portable_path(path):
            errors.append(f'reference manifest entry {i}: non-portable path {path!r}')

    dep_artifacts = deps.get('artifacts', {})
    if not isinstance(dep_artifacts, dict):
        errors.append('dependencies.artifacts must be an object')
        dep_artifacts = {}
    for key, rec in dep_artifacts.items():
        if not isinstance(rec, dict):
            errors.append(f'dependency {key}: record must be object')
            continue
        for dep in rec.get('depends_on', []):
            if dep not in dep_artifacts:
                errors.append(f'dependency {key}: unknown depends_on {dep}')

    visiting, visited = set(), set()
    def visit(key):
        if key in visited:
            return
        if key in visiting:
            errors.append(f'dependency cycle at {key}')
            return
        visiting.add(key)
        for dep in dep_artifacts.get(key, {}).get('depends_on', []):
            if dep in dep_artifacts:
                visit(dep)
        visiting.remove(key)
        visited.add(key)
    for key in dep_artifacts:
        visit(key)

    # Stable screenplay production-unit validation. Optional for projects created before 00.00.05.
    line_records = {}
    line_orders = set()
    allowed_line_kinds = {'dialogue', 'action', 'movement', 'transition'}
    for n, obj in validate_jsonl(root / '02_screenplay/line_manifest.jsonl', errors):
        if not isinstance(obj, dict):
            errors.append(f'line_manifest.jsonl:{n}: record must be an object')
            continue
        lid = obj.get('line_id', '')
        sid = obj.get('scene_id', '')
        kind = obj.get('kind')
        if not isinstance(lid, str) or not lid.startswith('LINE-') or not ID_RX.match(lid):
            errors.append(f'line_manifest.jsonl:{n}: invalid line_id {lid!r}')
        if lid in line_records:
            errors.append(f'line_manifest.jsonl:{n}: duplicate line_id {lid}')
        if not isinstance(sid, str) or not sid.startswith('SCN-') or not ID_RX.match(sid):
            errors.append(f'line_manifest.jsonl:{n}: invalid scene_id {sid!r}')
        if kind not in allowed_line_kinds:
            errors.append(f'line_manifest.jsonl:{n}: invalid kind {kind!r}')
        order = obj.get('order')
        if not isinstance(order, int) or isinstance(order, bool) or order < 1:
            errors.append(f'line_manifest.jsonl:{n}: order must be a positive integer')
        elif isinstance(sid, str):
            order_key = (sid, order)
            if order_key in line_orders:
                errors.append(f'line_manifest.jsonl:{n}: duplicate order {order} in {sid}')
            line_orders.add(order_key)
        cid = obj.get('character_id')
        if cid is not None:
            if not isinstance(cid, str) or not cid.startswith('CHAR-') or not ID_RX.match(cid):
                errors.append(f'line_manifest.jsonl:{n}: invalid character_id {cid!r}')
            elif canon.get('characters') and cid not in canon.get('characters', {}):
                errors.append(f'line_manifest.jsonl:{n}: unresolved character_id {cid}')
        if kind == 'dialogue':
            if not isinstance(cid, str) or not cid:
                errors.append(f'line_manifest.jsonl:{n}: dialogue requires character_id')
            if not isinstance(obj.get('text'), str):
                errors.append(f'line_manifest.jsonl:{n}: dialogue text must be a string')
        for field in ['audible', 'on_screen', 'blocking_required']:
            if field in obj and not isinstance(obj[field], bool):
                errors.append(f'line_manifest.jsonl:{n}: {field} must be boolean')
        if isinstance(lid, str):
            line_records[lid] = obj

    # Project-specific executable capability registry.
    capabilities_path = root / '03_preproduction/production_capabilities.json'
    capabilities = {}
    capability_actions = set()
    capability_cameras = set()
    if capabilities_path.exists():
        try:
            capabilities = load_json(capabilities_path)
        except Exception as exc:
            errors.append(f'03_preproduction/production_capabilities.json: invalid JSON: {exc}')
            capabilities = {}
        if capabilities.get('schema_version') != 1:
            errors.append('03_preproduction/production_capabilities.json: unsupported schema_version')
        allowed_cap_status = {'available', 'unavailable', 'conditional', 'unknown'}
        for field in ['locations', 'blocking_anchors', 'actions', 'camera_behaviors', 'audio', 'generation']:
            value = capabilities.get(field, {})
            if not isinstance(value, dict):
                errors.append(f'03_preproduction/production_capabilities.json: {field} must be an object')
                continue
            if field == 'actions':
                capability_actions = set(value)
            elif field == 'camera_behaviors':
                capability_cameras = set(value)
            for key, rec in value.items():
                if field == 'locations' and isinstance(key, str) and key.startswith('LOC-') and not ID_RX.match(key):
                    errors.append(f'03_preproduction/production_capabilities.json: invalid location key {key!r}')
                if isinstance(rec, dict) and rec.get('status') not in {None, *allowed_cap_status}:
                    errors.append(f'03_preproduction/production_capabilities.json: {field}.{key} invalid status {rec.get("status")!r}')
        for field in ['constraints', 'unknowns']:
            if not isinstance(capabilities.get(field, []), list):
                errors.append(f'03_preproduction/production_capabilities.json: {field} must be an array')
        for dotted, value in walk_strings(capabilities):
            if '://' in value:
                continue
            if ('/' in value or '\\' in value) and not portable_path(value):
                errors.append(f'03_preproduction/production_capabilities.json: non-portable string at {dotted}: {value!r}')

    # Physical performer blocking keyed to stable screenplay units.
    allowed_timing_sources = {'estimated', 'measured-speech', 'measured-media', 'locked'}
    blocking_lines = set()
    for n, obj in validate_jsonl(root / '03_preproduction/performance_blocking.jsonl', errors):
        if not isinstance(obj, dict):
            errors.append(f'performance_blocking.jsonl:{n}: record must be an object')
            continue
        lid = obj.get('line_id', '')
        sid = obj.get('scene_id', '')
        if lid not in line_records:
            errors.append(f'performance_blocking.jsonl:{n}: unresolved line_id {lid!r}')
        elif sid and sid != line_records[lid].get('scene_id'):
            errors.append(f'performance_blocking.jsonl:{n}: scene_id {sid!r} does not match {lid}')
        if sid and (not isinstance(sid, str) or not sid.startswith('SCN-') or not ID_RX.match(sid)):
            errors.append(f'performance_blocking.jsonl:{n}: invalid scene_id {sid!r}')
        cids = obj.get('character_ids', [])
        if not isinstance(cids, list):
            errors.append(f'performance_blocking.jsonl:{n}: character_ids must be an array')
            cids = []
        for cid in cids:
            if not isinstance(cid, str) or not cid.startswith('CHAR-') or not ID_RX.match(cid):
                errors.append(f'performance_blocking.jsonl:{n}: invalid character_id {cid!r}')
        for group in ['moves', 'actions']:
            records = obj.get(group, [])
            if not isinstance(records, list):
                errors.append(f'performance_blocking.jsonl:{n}: {group} must be an array')
                continue
            for j, rec in enumerate(records, 1):
                if not isinstance(rec, dict):
                    errors.append(f'performance_blocking.jsonl:{n}: {group}[{j}] must be an object')
                    continue
                cid = rec.get('character_id')
                if cid and (not isinstance(cid, str) or not cid.startswith('CHAR-') or not ID_RX.match(cid)):
                    errors.append(f'performance_blocking.jsonl:{n}: {group}[{j}] invalid character_id {cid!r}')
                cap = rec.get('capability_key')
                if cap and capabilities_path.exists() and cap not in capability_actions:
                    errors.append(f'performance_blocking.jsonl:{n}: {group}[{j}] unknown action capability {cap!r}')
        timing = obj.get('timing', {})
        if timing is not None and not isinstance(timing, dict):
            errors.append(f'performance_blocking.jsonl:{n}: timing must be an object')
        elif isinstance(timing, dict) and timing.get('source') not in {None, *allowed_timing_sources}:
            errors.append(f'performance_blocking.jsonl:{n}: invalid timing source {timing.get("source")!r}')
        if isinstance(lid, str):
            blocking_lines.add(lid)

    seen_shots = set()
    for n, obj in validate_jsonl(root / '04_generation/shot_briefs.jsonl', errors):
        sid = obj.get('shot_id', '')
        if not sid.startswith('SHOT-') or not ID_RX.match(sid):
            errors.append(f'shot_briefs.jsonl:{n}: invalid shot_id {sid!r}')
        if sid in seen_shots:
            errors.append(f'shot_briefs.jsonl:{n}: duplicate shot_id {sid}')
        seen_shots.add(sid)
        scn = obj.get('scene_id', '')
        if scn and (not scn.startswith('SCN-') or not ID_RX.match(scn)):
            errors.append(f'shot_briefs.jsonl:{n}: invalid scene_id {scn!r}')
        line_ids = obj.get('line_ids', [])
        if line_ids is not None and not isinstance(line_ids, list):
            errors.append(f'shot_briefs.jsonl:{n}: line_ids must be an array')
        elif isinstance(line_ids, list):
            for lid in line_ids:
                if not isinstance(lid, str) or not lid.startswith('LINE-') or not ID_RX.match(lid):
                    errors.append(f'shot_briefs.jsonl:{n}: invalid line_id {lid!r}')
                elif line_records and lid not in line_records:
                    errors.append(f'shot_briefs.jsonl:{n}: unresolved line_id {lid}')
                elif lid in line_records and scn and line_records[lid].get('scene_id') != scn:
                    errors.append(f'shot_briefs.jsonl:{n}: line_id {lid} belongs to {line_records[lid].get("scene_id")}, not {scn}')
        frame_regions = obj.get('frame_regions', [])
        if frame_regions is not None and not isinstance(frame_regions, list):
            errors.append(f'shot_briefs.jsonl:{n}: frame_regions must be an array')
        elif isinstance(frame_regions, list):
            for j, region in enumerate(frame_regions, 1):
                if not isinstance(region, dict):
                    errors.append(f'shot_briefs.jsonl:{n}: frame_regions[{j}] must be an object')
                    continue
                subject_id = region.get('subject_id')
                if subject_id and (not isinstance(subject_id, str) or not ID_RX.match(subject_id)):
                    errors.append(f'shot_briefs.jsonl:{n}: frame_regions[{j}] invalid subject_id {subject_id!r}')
                box = region.get('box')
                if box is not None:
                    valid_box = isinstance(box, list) and len(box) == 4 and all(isinstance(x, (int, float)) and not isinstance(x, bool) and 0 <= x <= 1 for x in box)
                    if not valid_box:
                        errors.append(f'shot_briefs.jsonl:{n}: frame_regions[{j}] box must contain four normalized numbers')
                    elif not (box[0] < box[2] and box[1] < box[3]):
                        errors.append(f'shot_briefs.jsonl:{n}: frame_regions[{j}] box must satisfy x0<x1 and y0<y1')
        camera_cap = obj.get('camera_capability_key')
        if camera_cap and capabilities_path.exists() and camera_cap not in capability_cameras:
            errors.append(f'shot_briefs.jsonl:{n}: unknown camera capability {camera_cap!r}')
        action_caps = obj.get('action_capability_keys', [])
        if action_caps is not None and not isinstance(action_caps, list):
            errors.append(f'shot_briefs.jsonl:{n}: action_capability_keys must be an array')
        elif isinstance(action_caps, list) and capabilities_path.exists():
            for cap in action_caps:
                if cap not in capability_actions:
                    errors.append(f'shot_briefs.jsonl:{n}: unknown action capability {cap!r}')
        for rid in obj.get('references', []):
            if isinstance(rid, str) and rid.startswith('REF-') and rid not in ref_ids:
                errors.append(f'shot_briefs.jsonl:{n}: unresolved reference {rid}')

    for rel in ['04_generation/image_briefs.jsonl', '04_generation/music_cues.jsonl', '04_generation/sfx_cues.jsonl']:
        validate_jsonl(root / rel, errors)

    for n, obj in validate_jsonl(root / '04_generation/voice_cues.jsonl', errors):
        if not isinstance(obj, dict):
            errors.append(f'voice_cues.jsonl:{n}: record must be an object')
            continue
        lid = obj.get('line_id')
        if line_records:
            if not isinstance(lid, str) or lid not in line_records:
                errors.append(f'voice_cues.jsonl:{n}: unresolved line_id {lid!r}')
            else:
                source = line_records[lid]
                if source.get('kind') != 'dialogue':
                    errors.append(f'voice_cues.jsonl:{n}: {lid} is not dialogue')
                if isinstance(obj.get('text'), str) and obj.get('text') != source.get('text'):
                    errors.append(f'voice_cues.jsonl:{n}: exact text drift for {lid}')
                speaker = obj.get('speaker') or obj.get('character_id')
                if speaker and source.get('character_id') and speaker != source.get('character_id'):
                    errors.append(f'voice_cues.jsonl:{n}: speaker {speaker!r} does not match {lid}')
        duration = obj.get('measured_duration_s')
        if duration is not None and (not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration < 0):
            errors.append(f'voice_cues.jsonl:{n}: invalid measured_duration_s {duration!r}')

    # Portable shooting-script validation.
    shooting_path = root / '03_preproduction/shooting_script.json'
    if shooting_path.exists():
        try:
            shooting = load_json(shooting_path)
        except Exception as exc:
            errors.append(f'03_preproduction/shooting_script.json: invalid JSON: {exc}')
            shooting = {}
        if shooting.get('schema_version') != 1:
            errors.append('03_preproduction/shooting_script.json: unsupported schema_version')
        for field in ['source_screenplay', 'line_manifest']:
            value = shooting.get(field)
            if isinstance(value, str) and value and not portable_path(value):
                errors.append(f'03_preproduction/shooting_script.json: non-portable {field} {value!r}')
        scenes = shooting.get('scenes', [])
        if not isinstance(scenes, list):
            errors.append('03_preproduction/shooting_script.json: scenes must be an array')
            scenes = []
        shooting_seen = set()
        for si, scene in enumerate(scenes, 1):
            if not isinstance(scene, dict):
                errors.append(f'03_preproduction/shooting_script.json: scene {si} must be an object')
                continue
            sid = scene.get('scene_id')
            if not isinstance(sid, str) or not sid.startswith('SCN-') or not ID_RX.match(sid):
                errors.append(f'03_preproduction/shooting_script.json: scene {si} invalid scene_id {sid!r}')
            units = scene.get('units', [])
            if not isinstance(units, list):
                errors.append(f'03_preproduction/shooting_script.json: {sid} units must be an array')
                continue
            for ui, unit in enumerate(units, 1):
                if not isinstance(unit, dict):
                    errors.append(f'03_preproduction/shooting_script.json: {sid} unit {ui} must be an object')
                    continue
                lid = unit.get('line_id')
                if lid in shooting_seen:
                    errors.append(f'03_preproduction/shooting_script.json: duplicate line unit {lid}')
                shooting_seen.add(lid)
                if line_records and lid not in line_records:
                    errors.append(f'03_preproduction/shooting_script.json: unresolved line_id {lid!r}')
                elif lid in line_records:
                    src = line_records[lid]
                    if src.get('scene_id') != sid:
                        errors.append(f'03_preproduction/shooting_script.json: {lid} belongs to {src.get("scene_id")}, not {sid}')
                    if src.get('kind') == 'dialogue' and unit.get('text') != src.get('text'):
                        errors.append(f'03_preproduction/shooting_script.json: exact dialogue drift for {lid}')
                shot_ids = unit.get('shot_ids', [])
                if not isinstance(shot_ids, list):
                    errors.append(f'03_preproduction/shooting_script.json: {lid} shot_ids must be an array')
                else:
                    for shot_id in shot_ids:
                        if shot_id not in seen_shots:
                            errors.append(f'03_preproduction/shooting_script.json: {lid} unresolved shot_id {shot_id!r}')
                for group in ['moves', 'actions']:
                    for rec in unit.get(group, []) if isinstance(unit.get(group, []), list) else []:
                        if not isinstance(rec, dict):
                            continue
                        cap = rec.get('capability_key')
                        if cap and capabilities_path.exists() and cap not in capability_actions:
                            errors.append(f'03_preproduction/shooting_script.json: {lid} unknown action capability {cap!r}')
                camera_cap = unit.get('camera_capability_key')
                if camera_cap and capabilities_path.exists() and camera_cap not in capability_cameras:
                    errors.append(f'03_preproduction/shooting_script.json: {lid} unknown camera capability {camera_cap!r}')
                timing = unit.get('timing', {})
                if timing is not None and not isinstance(timing, dict):
                    errors.append(f'03_preproduction/shooting_script.json: {lid} timing must be an object')
                elif isinstance(timing, dict) and timing.get('source') not in {None, *allowed_timing_sources}:
                    errors.append(f'03_preproduction/shooting_script.json: {lid} invalid timing source {timing.get("source")!r}')

    # Mutable narrative-state validation. Optional for projects created before 00.00.04.
    story_state_path = root / '01_story/story_state.json'
    if story_state_path.exists():
        try:
            story_state = load_json(story_state_path)
        except Exception as exc:
            errors.append(f'01_story/story_state.json: invalid JSON: {exc}')
            story_state = {}
        if story_state.get('schema_version') != 1:
            errors.append('01_story/story_state.json: unsupported schema_version')
        scene_order = story_state.get('scene_order', [])
        if not isinstance(scene_order, list):
            errors.append('01_story/story_state.json: scene_order must be an array')
            scene_order = []
        positions = {}
        for i, sid in enumerate(scene_order):
            if not isinstance(sid, str) or not sid.startswith('SCN-') or not ID_RX.match(sid):
                errors.append(f'01_story/story_state.json: invalid scene_order entry {sid!r}')
                continue
            if sid in positions:
                errors.append(f'01_story/story_state.json: duplicate scene_order entry {sid}')
            positions[sid] = i

        characters = story_state.get('characters', {})
        if not isinstance(characters, dict):
            errors.append('01_story/story_state.json: characters must be an object')
            characters = {}
        allowed_life = {'alive', 'dead', 'unknown', 'not-yet-introduced'}
        for cid, rec in characters.items():
            if not isinstance(cid, str) or not cid.startswith('CHAR-') or not ID_RX.match(cid):
                errors.append(f'01_story/story_state.json: invalid character id {cid!r}')
            if not isinstance(rec, dict):
                errors.append(f'01_story/story_state.json: character {cid} must be an object')
                continue
            if rec.get('life_state') not in {None, *allowed_life}:
                errors.append(f'01_story/story_state.json: character {cid} invalid life_state {rec.get("life_state")!r}')
            death_scene = rec.get('death_scene')
            if death_scene and death_scene not in positions:
                errors.append(f'01_story/story_state.json: character {cid} death_scene {death_scene!r} missing from scene_order')
            location = rec.get('current_location')
            if location and (not isinstance(location, str) or not location.startswith('LOC-') or not ID_RX.match(location)):
                errors.append(f'01_story/story_state.json: character {cid} invalid current_location {location!r}')
            possessions = rec.get('possessions', [])
            if possessions is not None and not isinstance(possessions, list):
                errors.append(f'01_story/story_state.json: character {cid} possessions must be an array')
            elif isinstance(possessions, list):
                for prop_id in possessions:
                    if not isinstance(prop_id, str) or not prop_id.startswith('PROP-') or not ID_RX.match(prop_id):
                        errors.append(f'01_story/story_state.json: character {cid} invalid possession {prop_id!r}')

        props_state = story_state.get('props', {})
        if not isinstance(props_state, dict):
            errors.append('01_story/story_state.json: props must be an object')
            props_state = {}
        allowed_prop = {'active', 'lost', 'destroyed', 'consumed', 'hidden', 'unknown'}
        for pid, rec in props_state.items():
            if not isinstance(pid, str) or not pid.startswith('PROP-') or not ID_RX.match(pid):
                errors.append(f'01_story/story_state.json: invalid prop id {pid!r}')
            if not isinstance(rec, dict):
                errors.append(f'01_story/story_state.json: prop {pid} must be an object')
                continue
            if rec.get('status') not in {None, *allowed_prop}:
                errors.append(f'01_story/story_state.json: prop {pid} invalid status {rec.get("status")!r}')
            owner = rec.get('owner')
            if owner and (not isinstance(owner, str) or not owner.startswith('CHAR-') or not ID_RX.match(owner)):
                errors.append(f'01_story/story_state.json: prop {pid} invalid owner {owner!r}')
            location = rec.get('location')
            if location and (not isinstance(location, str) or not location.startswith('LOC-') or not ID_RX.match(location)):
                errors.append(f'01_story/story_state.json: prop {pid} invalid location {location!r}')

        questions = story_state.get('questions', {})
        if not isinstance(questions, dict):
            errors.append('01_story/story_state.json: questions must be an object')
            questions = {}
        allowed_question = {'open', 'partially-answered', 'resolved', 'abandoned', 'intentional-open-ending'}
        for qid, rec in questions.items():
            if not isinstance(qid, str) or not qid.startswith('QST-') or not ID_RX.match(qid):
                errors.append(f'01_story/story_state.json: invalid question id {qid!r}')
            if not isinstance(rec, dict):
                errors.append(f'01_story/story_state.json: question {qid} must be an object')
                continue
            if rec.get('status') not in {None, *allowed_question}:
                errors.append(f'01_story/story_state.json: question {qid} invalid status {rec.get("status")!r}')
            introduced = rec.get('introduced_in')
            resolved = rec.get('resolved_in')
            if introduced and introduced not in positions:
                errors.append(f'01_story/story_state.json: question {qid} introduced_in {introduced!r} missing from scene_order')
            if resolved and resolved not in positions:
                errors.append(f'01_story/story_state.json: question {qid} resolved_in {resolved!r} missing from scene_order')
            if introduced in positions and resolved in positions and positions[resolved] < positions[introduced]:
                errors.append(f'01_story/story_state.json: question {qid} resolves before introduction')
            if rec.get('status') == 'resolved' and not resolved:
                errors.append(f'01_story/story_state.json: resolved question {qid} missing resolved_in')

        promises = story_state.get('promises', {})
        if not isinstance(promises, dict):
            errors.append('01_story/story_state.json: promises must be an object')
            promises = {}
        allowed_promise = {'open', 'paid', 'subverted', 'cancelled', 'intentionally-unpaid'}
        for pid, rec in promises.items():
            if not isinstance(pid, str) or not pid.startswith('PROM-') or not ID_RX.match(pid):
                errors.append(f'01_story/story_state.json: invalid promise id {pid!r}')
            if not isinstance(rec, dict):
                errors.append(f'01_story/story_state.json: promise {pid} must be an object')
                continue
            if rec.get('status') not in {None, *allowed_promise}:
                errors.append(f'01_story/story_state.json: promise {pid} invalid status {rec.get("status")!r}')
            setup = rec.get('setup_in')
            payoff = rec.get('payoff_in')
            if setup and setup not in positions:
                errors.append(f'01_story/story_state.json: promise {pid} setup_in {setup!r} missing from scene_order')
            if payoff and payoff not in positions:
                errors.append(f'01_story/story_state.json: promise {pid} payoff_in {payoff!r} missing from scene_order')
            if setup in positions and payoff in positions and positions[payoff] < positions[setup]:
                errors.append(f'01_story/story_state.json: promise {pid} pays off before setup')
            if rec.get('status') in {'paid', 'subverted'} and not payoff:
                errors.append(f'01_story/story_state.json: {rec.get("status")} promise {pid} missing payoff_in')

        events = story_state.get('events', [])
        if not isinstance(events, list):
            errors.append('01_story/story_state.json: events must be an array')
            events = []
        for i, event in enumerate(events, 1):
            if not isinstance(event, dict):
                errors.append(f'01_story/story_state.json: event {i} must be an object')
                continue
            sid = event.get('scene_id')
            if sid and sid not in positions:
                errors.append(f'01_story/story_state.json: event {i} scene_id {sid!r} missing from scene_order')
            active = event.get('active_characters', [])
            mentions = event.get('mentions', [])
            if not isinstance(active, list) or not isinstance(mentions, list):
                errors.append(f'01_story/story_state.json: event {i} active_characters and mentions must be arrays')
                continue
            for cid in active + mentions:
                if not isinstance(cid, str) or not cid.startswith('CHAR-') or not ID_RX.match(cid):
                    errors.append(f'01_story/story_state.json: event {i} invalid character reference {cid!r}')
            if event.get('flashback') is True or sid not in positions:
                continue
            for cid in active:
                rec = characters.get(cid, {}) if isinstance(cid, str) else {}
                death_scene = rec.get('death_scene') if isinstance(rec, dict) else None
                if death_scene in positions and positions[sid] > positions[death_scene]:
                    errors.append(f'01_story/story_state.json: event {i} has active appearance of {cid} after death in {death_scene}; use mentions or mark chronology exception')

    # Generated take and selection validation.
    take_ids = {}
    for n, obj in validate_jsonl(root / '04_generation/take_manifest.jsonl', errors):
        if not isinstance(obj, dict):
            errors.append(f'take_manifest.jsonl:{n}: record must be an object')
            continue
        tid = obj.get('take_id', '')
        sid = obj.get('shot_id', '')
        if not tid.startswith('TAKE-') or not ID_RX.match(tid):
            errors.append(f'take_manifest.jsonl:{n}: invalid take_id {tid!r}')
        if tid in take_ids:
            errors.append(f'take_manifest.jsonl:{n}: duplicate take_id {tid}')
        if not sid.startswith('SHOT-') or not ID_RX.match(sid):
            errors.append(f'take_manifest.jsonl:{n}: invalid shot_id {sid!r}')
        elif sid not in seen_shots:
            errors.append(f'take_manifest.jsonl:{n}: shot_id {sid} has no shot brief')
        if obj.get('status') not in {None, 'candidate', 'selected', 'rejected', 'superseded'}:
            errors.append(f'take_manifest.jsonl:{n}: invalid status {obj.get("status")!r}')
        path = obj.get('path')
        if isinstance(path, str) and path and not portable_path(path):
            errors.append(f'take_manifest.jsonl:{n}: non-portable path {path!r}')
        take_ids[tid] = sid

    # Generated-media QC is observable evidence, not creative preference.
    take_qc = {}
    allowed_qc = {'pass', 'warn', 'fail', 'not-applicable', 'not-checked'}
    for n, obj in validate_jsonl(root / '04_generation/take_qc.jsonl', errors):
        if not isinstance(obj, dict):
            errors.append(f'take_qc.jsonl:{n}: record must be an object')
            continue
        tid = obj.get('take_id', '')
        sid = obj.get('shot_id', '')
        if tid not in take_ids:
            errors.append(f'take_qc.jsonl:{n}: unknown take_id {tid!r}')
        elif take_ids.get(tid) != sid:
            errors.append(f'take_qc.jsonl:{n}: shot_id {sid!r} does not match take {tid}')
        overall = obj.get('overall')
        if overall not in allowed_qc:
            errors.append(f'take_qc.jsonl:{n}: invalid overall {overall!r}')
        checks = obj.get('checks', {})
        if not isinstance(checks, dict):
            errors.append(f'take_qc.jsonl:{n}: checks must be an object')
        else:
            for name, rec in checks.items():
                if not isinstance(rec, dict) or rec.get('status') not in allowed_qc:
                    errors.append(f'take_qc.jsonl:{n}: check {name!r} has invalid status')
        metrics = obj.get('metrics', [])
        if metrics is not None and not isinstance(metrics, list):
            errors.append(f'take_qc.jsonl:{n}: metrics must be an array')
        if isinstance(tid, str):
            take_qc[tid] = overall

    selections_path = root / '04_generation/selections.json'
    if selections_path.exists():
        try:
            selections = load_json(selections_path)
        except Exception as exc:
            errors.append(f'04_generation/selections.json: invalid JSON: {exc}')
            selections = {}
        if selections.get('schema_version') != 1:
            errors.append('04_generation/selections.json: unsupported schema_version')
        shots = selections.get('shots', {})
        if not isinstance(shots, dict):
            errors.append('04_generation/selections.json: shots must be an object')
            shots = {}
        for sid, rec in shots.items():
            if not isinstance(sid, str) or not sid.startswith('SHOT-') or not ID_RX.match(sid):
                errors.append(f'04_generation/selections.json: invalid shot id {sid!r}')
            if not isinstance(rec, dict):
                errors.append(f'04_generation/selections.json: {sid} selection must be an object')
                continue
            tid = rec.get('selected_take_id')
            if tid:
                if tid not in take_ids:
                    errors.append(f'04_generation/selections.json: {sid} selects unknown take {tid}')
                elif take_ids.get(tid) != sid:
                    errors.append(f'04_generation/selections.json: {sid} selects take {tid} belonging to {take_ids.get(tid)}')
                elif take_qc.get(tid) == 'fail' and rec.get('qc_override') is not True:
                    errors.append(f'04_generation/selections.json: {sid} selects QC-failed take {tid} without qc_override')
                elif take_qc.get(tid) == 'fail' and rec.get('qc_override') is True and not rec.get('reason'):
                    errors.append(f'04_generation/selections.json: {sid} QC override for {tid} requires a reason')


    # Generalized media registry and finishing/release manifests. Optional for projects created before 00.00.06.
    media_registry_path = root / '00_project/media_registry.jsonl'
    media_approvals_path = root / '00_project/media_approvals.json'
    if media_registry_path.exists() or media_approvals_path.exists():
        try:
            media_records = load_media_records(media_registry_path)
            media_approvals = load_media_approvals(media_approvals_path)
            for msg in validate_media_registry(media_records, media_approvals):
                errors.append(f'media registry: {msg}')
        except Exception as exc:
            errors.append(f'media registry: {exc}')

    audio_mix_path = root / '05_post/audio_mix.json'
    if audio_mix_path.exists():
        try:
            audio_mix = load_json(audio_mix_path)
            for msg in validate_audio_mix(root, audio_mix, require_sources=False):
                errors.append(f'05_post/audio_mix.json: {msg}')
        except Exception as exc:
            errors.append(f'05_post/audio_mix.json: {exc}')

    finish_path = root / '05_post/video_finish.jsonl'
    for n, obj in validate_jsonl(finish_path, errors):
        if not isinstance(obj, dict):
            errors.append(f'video_finish.jsonl:{n}: record must be an object')
            continue
        finish_id = obj.get('finish_id')
        if not isinstance(finish_id, str) or not finish_id.startswith('MEDIA-') or not ID_RX.match(finish_id):
            errors.append(f'video_finish.jsonl:{n}: invalid finish_id {finish_id!r}')
        for field in ['input_path', 'output_path']:
            value = obj.get(field)
            if not isinstance(value, str) or not portable_path(value):
                errors.append(f'video_finish.jsonl:{n}: invalid {field} {value!r}')
        if obj.get('fit', 'contain') not in {'contain', 'cover'}:
            errors.append(f'video_finish.jsonl:{n}: fit must be contain or cover')
        for field in ['width', 'height']:
            value = obj.get(field, 0)
            if not isinstance(value, int) or isinstance(value, bool) or value < 16:
                errors.append(f'video_finish.jsonl:{n}: {field} must be integer >= 16')
        fps = obj.get('fps', 0)
        if not isinstance(fps, (int, float)) or isinstance(fps, bool) or fps <= 0:
            errors.append(f'video_finish.jsonl:{n}: fps must be positive')

    timeline_path = root / '05_post/timeline.json'
    if timeline_path.exists():
        try:
            timeline = load_json(timeline_path)
            tid = timeline.get('timeline_id')
            if not isinstance(tid, str) or not tid.startswith('MASTER-') or not ID_RX.match(tid):
                errors.append(f'05_post/timeline.json: invalid main timeline_id {tid!r}')
            for msg in validate_executable_timeline(root, timeline, require_sources=False):
                errors.append(f'05_post/timeline.json: {msg}')
        except Exception as exc:
            errors.append(f'05_post/timeline.json: {exc}')

    editor_project_path = root / '05_post/editorial/editor_project.json'
    if editor_project_path.exists():
        try:
            editor_obj = load_json(editor_project_path)
            for msg in validate_editor_project(root, editor_obj, require_sources=False):
                errors.append(f'05_post/editorial/editor_project.json: {msg}')
        except Exception as exc:
            errors.append(f'05_post/editorial/editor_project.json: {exc}')

    delivery_specs_path = root / '06_release/delivery_specs.json'
    if delivery_specs_path.exists():
        try:
            delivery_specs = load_json(delivery_specs_path)
        except Exception as exc:
            errors.append(f'06_release/delivery_specs.json: invalid JSON: {exc}')
            delivery_specs = {}
        if delivery_specs.get('schema_version') != 1:
            errors.append('06_release/delivery_specs.json: unsupported schema_version')
        deliverables = delivery_specs.get('deliverables', [])
        if not isinstance(deliverables, list):
            errors.append('06_release/delivery_specs.json: deliverables must be an array')
        else:
            seen_delivery_ids = set()
            for i, rec in enumerate(deliverables, 1):
                if not isinstance(rec, dict):
                    errors.append(f'06_release/delivery_specs.json: deliverable {i} must be object')
                    continue
                did = rec.get('delivery_id', '')
                if not isinstance(did, str) or not did.startswith('DELIV-') or not ID_RX.match(did):
                    errors.append(f'06_release/delivery_specs.json: deliverable {i} invalid delivery_id {did!r}')
                elif did in seen_delivery_ids:
                    errors.append(f'06_release/delivery_specs.json: duplicate delivery_id {did}')
                seen_delivery_ids.add(did)
                value = rec.get('path')
                if not isinstance(value, str) or not portable_path(value):
                    errors.append(f'06_release/delivery_specs.json: {did} invalid path {value!r}')

    for msg in validate_trailer_campaign(root):
        errors.append(f'trailer campaign: {msg}')
    for msg in validate_social_campaign(root):
        errors.append(f'social campaign: {msg}')

    release_manifest_path = root / '06_release/release_manifest.json'
    if release_manifest_path.exists():
        try:
            release_obj = load_json(release_manifest_path)
            release_errors, _ = validate_release_manifest(root, release_obj, require_files=False)
            for msg in release_errors:
                errors.append(f'06_release/release_manifest.json: {msg}')
        except Exception as exc:
            errors.append(f'06_release/release_manifest.json: {exc}')

    # Native previz validation.
    previz_root = root / '03_preproduction/previz'
    if previz_root.exists():
        for p in previz_root.glob('SCN-*.json'):
            try:
                obj = load_json(p)
            except Exception as exc:
                errors.append(f'{p.relative_to(root)}: invalid JSON: {exc}')
                continue
            sid = obj.get('scene_id', '')
            if not sid.startswith('SCN-') or not ID_RX.match(sid):
                errors.append(f'{p.relative_to(root)}: invalid scene_id {sid!r}')
            space = obj.get('space')
            if not isinstance(space, dict):
                errors.append(f'{p.relative_to(root)}: missing space object')
            else:
                for field in ['verified_geometry', 'assumed_geometry']:
                    if not isinstance(space.get(field, []), list):
                        errors.append(f'{p.relative_to(root)}: space.{field} must be an array')
            for field in ['actors', 'props', 'paths', 'eyelines', 'camera_setups', 'cut_order']:
                if not isinstance(obj.get(field, []), list):
                    errors.append(f'{p.relative_to(root)}: {field} must be an array')

    # Durable multi-step pipeline progress validation.
    progress_path = root / '00_project/pipeline_progress.json'
    if progress_path.exists():
        try:
            progress_obj = load_json(progress_path)
            validate_pipeline_progress(progress_obj)
        except (Exception, SystemExit) as exc:
            errors.append(f'00_project/pipeline_progress.json: {exc}')
            progress_obj = {}
        if progress_obj.get('status') in {'active', 'paused', 'blocked'}:
            if not (root / '00_project/HANDOFF.md').exists():
                errors.append('00_project/HANDOFF.md: required while pipeline progress is active, paused, or blocked')
            if not (root / '00_project/progress_events.jsonl').exists():
                errors.append('00_project/progress_events.jsonl: required while pipeline progress is active, paused, or blocked')

    # Resource-safe offline generation package.
    offline_batch_path = root / '04_generation/comfyui/offline_batch.json'
    if offline_batch_path.exists():
        try:
            errors.extend(f'offline ComfyUI batch: {e}' for e in validate_offline_batch(root, load_offline_batch(root), live=None))
        except Exception as exc:
            errors.append(f'04_generation/comfyui/offline_batch.json: {exc}')
    resource_policy_path = root / '00_project/resource_policy.json'
    if resource_policy_path.exists():
        try:
            rp = load_json(resource_policy_path)
            if rp.get('schema_version') != 1:
                errors.append('00_project/resource_policy.json: schema_version must be 1')
            llm = rp.get('local_llm')
            if not isinstance(llm, dict):
                errors.append('00_project/resource_policy.json: local_llm must be an object')
            elif llm.get('adapter') not in {'unconfigured', 'command', 'external'}:
                errors.append('00_project/resource_policy.json: local_llm.adapter must be unconfigured, command, or external')
            else:
                location = llm.get('runtime_location', 'unknown')
                if location not in {'unknown', 'local', 'external'}:
                    errors.append('00_project/resource_policy.json: local_llm.runtime_location must be unknown, local, or external')
                if llm.get('adapter') == 'external':
                    evidence = llm.get('location_evidence', [])
                    if location != 'external' or not isinstance(evidence, list) or not any(isinstance(x, str) and x.strip() for x in evidence):
                        errors.append('00_project/resource_policy.json: external adapter requires explicit external runtime_location and location_evidence')
                    endpoint = str(llm.get('endpoint') or llm.get('health_url') or '')
                    if endpoint:
                        try:
                            from llm_runtime import classify_endpoint
                            if classify_endpoint(endpoint).get('location') == 'local':
                                errors.append('00_project/resource_policy.json: external adapter conflicts with a local LLM endpoint')
                        except Exception as exc:
                            errors.append(f'00_project/resource_policy.json: could not classify local_llm endpoint: {exc}')
            comfy_cfg = rp.get('comfyui')
            if not isinstance(comfy_cfg, dict):
                errors.append('00_project/resource_policy.json: comfyui must be an object')
            for dotted, value in walk_strings(rp):
                if any(key in dotted.lower() for key in ['api_key', 'password', 'secret', 'bearer', 'token']):
                    errors.append(f'00_project/resource_policy.json: credential-like field at {dotted}')
        except Exception as exc:
            errors.append(f'00_project/resource_policy.json: {exc}')
    resource_status_path = root / '00_project/resource_handoff.json'
    if resource_status_path.exists():
        try:
            rs = load_json(resource_status_path)
            if rs.get('schema_version') != 1:
                errors.append('00_project/resource_handoff.json: schema_version must be 1')
            if rs.get('phase') not in {'idle','armed','waiting-for-agent-end','unloading-llm','running-comfyui','unloading-comfyui','reloading-llm','complete','failed','cancelled'}:
                errors.append(f"00_project/resource_handoff.json: invalid phase {rs.get('phase')!r}")
        except Exception as exc:
            errors.append(f'00_project/resource_handoff.json: {exc}')

    # Portable generation package validation.
    comfy = root / '04_generation/comfyui_handoff.json'
    if comfy.exists():
        try:
            obj = load_json(comfy)
        except Exception as exc:
            errors.append(f'04_generation/comfyui_handoff.json: invalid JSON: {exc}')
            obj = {}
        for field in ['schema_version', 'producer', 'requested_models', 'required_inputs', 'expected_outputs', 'unresolved_requirements']:
            if field not in obj:
                errors.append(f'04_generation/comfyui_handoff.json: missing {field}')
        for dotted, value in walk_strings(obj):
            looks_like_path = '/' in value or '\\' in value
            if looks_like_path and not portable_path(value):
                errors.append(f'04_generation/comfyui_handoff.json: non-portable string at {dotted}: {value!r}')

    # ComfyUI live-run record validation.
    comfy_root = root / '04_generation/comfyui'
    snapshot = comfy_root / 'server_snapshot.json'
    if snapshot.exists():
        try:
            obj = load_json(snapshot)
        except Exception as exc:
            errors.append(f'04_generation/comfyui/server_snapshot.json: invalid JSON: {exc}')
            obj = {}
        if 'captured_at' not in obj:
            errors.append('04_generation/comfyui/server_snapshot.json: missing captured_at')
        for dotted, value in walk_strings(obj):
            low = dotted.lower()
            if any(key in low for key in ['api_key', 'auth_token', 'access_token', 'refresh_token']):
                errors.append(f'04_generation/comfyui/server_snapshot.json: credential-like field at {dotted}')

    run_index = comfy_root / 'run_index.jsonl'
    if run_index.exists():
        for n, obj in validate_jsonl(run_index, errors):
            if not isinstance(obj, dict):
                errors.append(f'run_index.jsonl:{n}: record must be an object')
                continue
            if not obj.get('event') or not obj.get('prompt_id') or not obj.get('timestamp'):
                errors.append(f'run_index.jsonl:{n}: missing event, prompt_id, or timestamp')
            item_id = obj.get('item_id')
            if item_id and (not isinstance(item_id, str) or not ID_RX.match(item_id)):
                errors.append(f'run_index.jsonl:{n}: invalid item_id {item_id!r}')
            for dotted, value in walk_strings(obj):
                low = dotted.lower()
                if any(key in low for key in ['api_key', 'auth_token', 'access_token', 'refresh_token']):
                    errors.append(f'run_index.jsonl:{n}: credential-like field at {dotted}')

    runs_root = comfy_root / 'runs'
    if runs_root.exists():
        for p in runs_root.glob('*.json'):
            try:
                obj = load_json(p)
            except Exception as exc:
                errors.append(f'{p.relative_to(root)}: invalid JSON: {exc}')
                continue
            if obj.get('schema_version') != 1:
                errors.append(f'{p.relative_to(root)}: unsupported schema_version')
            if not obj.get('prompt_id'):
                errors.append(f'{p.relative_to(root)}: missing prompt_id')
            workflow_path = obj.get('workflow_path')
            if isinstance(workflow_path, str) and workflow_path and not portable_path(workflow_path):
                errors.append(f'{p.relative_to(root)}: non-portable workflow_path {workflow_path!r}')
            for dotted, value in walk_strings(obj):
                low = dotted.lower()
                if any(key in low for key in ['api_key', 'auth_token', 'access_token', 'refresh_token']):
                    errors.append(f'{p.relative_to(root)}: credential-like field at {dotted}')
                if dotted.endswith('.path') and isinstance(value, str) and value and not portable_path(value):
                    errors.append(f'{p.relative_to(root)}: non-portable output path at {dotted}: {value!r}')

    # Portable editorial package validation.
    editorial = root / '05_post/editorial_manifest.json'
    if editorial.exists():
        try:
            obj = load_json(editorial)
        except Exception as exc:
            errors.append(f'05_post/editorial_manifest.json: invalid JSON: {exc}')
            obj = {}
        for field in ['schema_version', 'project_title', 'timeline', 'audio_stems', 'missing_media', 'placeholders']:
            if field not in obj:
                errors.append(f'05_post/editorial_manifest.json: missing {field}')
        for field in ['timeline', 'audio_stems', 'missing_media', 'placeholders']:
            if field in obj and not isinstance(obj[field], list):
                errors.append(f'05_post/editorial_manifest.json: {field} must be an array')
        for dotted, value in walk_strings(obj):
            if ('/' in value or '\\' in value) and not portable_path(value):
                errors.append(f'05_post/editorial_manifest.json: non-portable string at {dotted}: {value!r}')

    for e in errors:
        print('ERROR', e)
    if errors:
        return 1
    print(f'OK: project structure valid, {len(seen_shots)} shot briefs, {len(ref_ids)} references checked')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
