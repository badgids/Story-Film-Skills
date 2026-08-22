#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ID_RX = re.compile(r"^(?:CHAR|PROP|REF|SCN|LINE|SHOT)-\d{3,}$")
MOUTH_VISIBILITY = {"required", "preferred", "not-required"}
CUT_POLICY = {"hold-through-line", "cut-allowed", "not-applicable"}
TIMING_SOURCE = {"estimated", "measured-speech", "measured-media", "locked"}
MEASURED_TIMING = {"measured-speech", "measured-media", "locked"}


def load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        if isinstance(value, dict):
            rows.append(value)
    return rows


def _valid_positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def _line_map(root: Path) -> dict[str, dict[str, Any]]:
    return {
        row["line_id"]: row
        for row in load_jsonl(root / "02_screenplay/line_manifest.jsonl")
        if isinstance(row.get("line_id"), str)
    }


def _validate_sync_record(
    sync: Any,
    prefix: str,
    lines: dict[str, dict[str, Any]],
    errors: list[str],
    subjects: set[str] | None = None,
    expected_line_id: str | None = None,
) -> None:
    if not isinstance(sync, dict):
        errors.append(f"{prefix} must be an object")
        return
    line_id = sync.get("line_id")
    speaker_id = sync.get("speaker_id")
    if not isinstance(line_id, str) or not line_id.startswith("LINE-") or not ID_RX.match(line_id):
        errors.append(f"{prefix}.line_id is invalid")
        source = None
    else:
        source = lines.get(line_id)
        if lines and source is None:
            errors.append(f"{prefix}.line_id {line_id} does not resolve")
        elif source is not None and source.get("kind") != "dialogue":
            errors.append(f"{prefix}.line_id {line_id} is not dialogue")
    if expected_line_id and isinstance(line_id, str) and line_id != expected_line_id:
        errors.append(f"{prefix}.line_id {line_id} does not match unit {expected_line_id}")
    if not isinstance(speaker_id, str) or not speaker_id.startswith("CHAR-") or not ID_RX.match(speaker_id):
        errors.append(f"{prefix}.speaker_id is invalid")
    elif source is not None and source.get("character_id") and speaker_id != source.get("character_id"):
        errors.append(f"{prefix}.speaker_id {speaker_id} does not match {line_id}")
    required = sync.get("required", False)
    if not isinstance(required, bool):
        errors.append(f"{prefix}.required must be boolean")
        required = False
    mouth = sync.get("mouth_visibility", "not-required")
    if mouth not in MOUTH_VISIBILITY:
        errors.append(f"{prefix}.mouth_visibility {mouth!r} is invalid")
    cut_policy = sync.get("cut_policy", "not-applicable")
    if cut_policy not in CUT_POLICY:
        errors.append(f"{prefix}.cut_policy {cut_policy!r} is invalid")
    timing_source = sync.get("timing_source", "estimated")
    if timing_source not in TIMING_SOURCE:
        errors.append(f"{prefix}.timing_source {timing_source!r} is invalid")
    duration = sync.get("speech_duration_s")
    if duration is not None and not _valid_positive_number(duration):
        errors.append(f"{prefix}.speech_duration_s must be a positive number")
    if timing_source in MEASURED_TIMING and not _valid_positive_number(duration):
        errors.append(f"{prefix}.timing_source {timing_source} requires speech_duration_s")
    constraints = sync.get("occlusion_constraints")
    if constraints is not None and not (
        isinstance(constraints, list) and all(isinstance(item, str) for item in constraints)
    ):
        errors.append(f"{prefix}.occlusion_constraints must be an array of strings")
    if required and subjects is not None and isinstance(speaker_id, str) and speaker_id not in subjects:
        errors.append(f"{prefix}: required visible speaker {speaker_id} is not a shot subject")


def _validate_end_frame(
    value: Any,
    prefix: str,
    canon: dict[str, Any],
    ref_ids: set[str],
    errors: list[str],
) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object")
        return
    if "required" in value and not isinstance(value["required"], bool):
        errors.append(f"{prefix}.required must be boolean")
    characters = canon.get("characters", {}) if isinstance(canon.get("characters"), dict) else {}
    props = canon.get("props", {}) if isinstance(canon.get("props"), dict) else {}
    subjects = value.get("subjects", [])
    if not isinstance(subjects, list):
        errors.append(f"{prefix}.subjects must be an array")
    else:
        for index, row in enumerate(subjects, 1):
            item_prefix = f"{prefix}.subjects[{index}]"
            if not isinstance(row, dict):
                errors.append(f"{item_prefix} must be an object")
                continue
            sid = row.get("subject_id")
            if not isinstance(sid, str) or not sid.startswith("CHAR-") or not ID_RX.match(sid):
                errors.append(f"{item_prefix}.subject_id is invalid")
            elif sid not in characters:
                errors.append(f"{item_prefix}.subject_id {sid} does not resolve")
    prop_rows = value.get("props", [])
    if not isinstance(prop_rows, list):
        errors.append(f"{prefix}.props must be an array")
    else:
        for index, row in enumerate(prop_rows, 1):
            item_prefix = f"{prefix}.props[{index}]"
            if not isinstance(row, dict):
                errors.append(f"{item_prefix} must be an object")
                continue
            pid = row.get("prop_id")
            if not isinstance(pid, str) or not pid.startswith("PROP-") or not ID_RX.match(pid):
                errors.append(f"{item_prefix}.prop_id is invalid")
            elif pid not in props:
                errors.append(f"{item_prefix}.prop_id {pid} does not resolve")
    rid = value.get("reference_id")
    if rid is not None:
        if not isinstance(rid, str) or not rid.startswith("REF-") or not ID_RX.match(rid):
            errors.append(f"{prefix}.reference_id is invalid")
        elif rid not in ref_ids:
            errors.append(f"{prefix}.reference_id {rid} does not resolve")


def validate_project(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    lines = _line_map(root)
    canon = load_json(root / "00_project/canon.json", {})
    refs = load_json(root / "03_preproduction/references/reference_manifest.json", {})
    ref_ids = {
        row.get("ref_id")
        for row in refs.get("references", []) if isinstance(refs, dict) and isinstance(refs.get("references"), list)
        if isinstance(row, dict) and isinstance(row.get("ref_id"), str)
    } if isinstance(refs, dict) else set()

    for row_index, shot in enumerate(load_jsonl(root / "04_generation/shot_briefs.jsonl"), 1):
        subjects = {x for x in shot.get("subjects", []) if isinstance(x, str)} if isinstance(shot.get("subjects", []), list) else set()
        sync_rows = shot.get("lip_sync")
        if sync_rows is not None:
            if not isinstance(sync_rows, list):
                errors.append(f"shot_briefs.jsonl:{row_index}: lip_sync must be an array")
            else:
                for index, sync in enumerate(sync_rows, 1):
                    _validate_sync_record(sync, f"shot_briefs.jsonl:{row_index}.lip_sync[{index}]", lines, errors, subjects)
        if "end_frame" in shot:
            _validate_end_frame(shot["end_frame"], f"shot_briefs.jsonl:{row_index}.end_frame", canon if isinstance(canon, dict) else {}, ref_ids, errors)
        capture = shot.get("capture_behavior")
        if capture is not None and not isinstance(capture, str):
            errors.append(f"shot_briefs.jsonl:{row_index}: capture_behavior must be a string")

    shooting = load_json(root / "03_preproduction/shooting_script.json", {})
    if isinstance(shooting, dict):
        for scene_index, scene in enumerate(shooting.get("scenes", []) if isinstance(shooting.get("scenes"), list) else [], 1):
            if not isinstance(scene, dict):
                continue
            for unit_index, unit in enumerate(scene.get("units", []) if isinstance(scene.get("units"), list) else [], 1):
                if not isinstance(unit, dict):
                    continue
                sync_rows = unit.get("lip_sync")
                if sync_rows is None:
                    continue
                prefix = f"shooting_script.scenes[{scene_index}].units[{unit_index}].lip_sync"
                if not isinstance(sync_rows, list):
                    errors.append(f"{prefix} must be an array")
                    continue
                for index, sync in enumerate(sync_rows, 1):
                    _validate_sync_record(sync, f"{prefix}[{index}]", lines, errors, expected_line_id=unit.get("line_id"))
    return errors


def _required_sync(rows: Any) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict) and row.get("required") is True]


def _same_sync(a: dict[str, Any], b: dict[str, Any]) -> bool:
    return a.get("line_id") == b.get("line_id") and a.get("speaker_id") == b.get("speaker_id")


def _dedupe(values: list[Any]) -> list[Any]:
    seen: set[str] = set()
    out: list[Any] = []
    for value in values:
        key = json.dumps(value, sort_keys=True, ensure_ascii=False) if isinstance(value, dict) else str(value)
        if key not in seen:
            seen.add(key)
            out.append(value)
    return out


def build_coverage(root: Path, scene_ids: set[str] | None = None) -> dict[str, Any]:
    root = root.resolve()
    lines = _line_map(root)
    shots = {
        row.get("shot_id"): row
        for row in load_jsonl(root / "04_generation/shot_briefs.jsonl")
        if isinstance(row.get("shot_id"), str) and (not scene_ids or row.get("scene_id") in scene_ids)
    }
    units: dict[str, list[dict[str, Any]]] = {}
    shooting = load_json(root / "03_preproduction/shooting_script.json", {})
    if isinstance(shooting, dict):
        for scene in shooting.get("scenes", []) if isinstance(shooting.get("scenes"), list) else []:
            if not isinstance(scene, dict) or (scene_ids and scene.get("scene_id") not in scene_ids):
                continue
            for unit in scene.get("units", []) if isinstance(scene.get("units"), list) else []:
                if isinstance(unit, dict) and isinstance(unit.get("line_id"), str):
                    units.setdefault(unit["line_id"], []).append(unit)

    missing: list[dict[str, Any]] = []
    speaker_conflicts: list[dict[str, Any]] = []
    timing_conflicts: list[dict[str, Any]] = []
    line_conflicts: list[dict[str, Any]] = []

    def check_basic(sync: dict[str, Any], source: str) -> None:
        lid = sync.get("line_id")
        line = lines.get(lid) if isinstance(lid, str) else None
        if line is None or line.get("kind") != "dialogue":
            line_conflicts.append({"source": source, "line_id": lid, "reason": "missing-or-non-dialogue"})
            return
        if sync.get("speaker_id") != line.get("character_id"):
            speaker_conflicts.append({
                "source": source,
                "line_id": lid,
                "expected": line.get("character_id"),
                "actual": sync.get("speaker_id"),
            })

    for shot_id, shot in shots.items():
        for sync in _required_sync(shot.get("lip_sync")):
            check_basic(sync, shot_id)
            lid = sync.get("line_id")
            matching_units = [
                unit for unit in units.get(lid, [])
                if any(_same_sync(sync, other) for other in _required_sync(unit.get("lip_sync")))
            ]
            if not matching_units:
                missing.append({"line_id": lid, "shot_id": shot_id, "missing": "shooting-script lip_sync"})
            speech = sync.get("speech_duration_s")
            duration = shot.get("duration_seconds")
            if sync.get("cut_policy") == "hold-through-line" and _valid_positive_number(speech) and _valid_positive_number(duration) and speech > duration:
                timing_conflicts.append({"line_id": lid, "shot_id": shot_id, "speech_duration_s": speech, "shot_duration_s": duration})

    for lid, line_units in units.items():
        for unit in line_units:
            for sync in _required_sync(unit.get("lip_sync")):
                check_basic(sync, f"shooting:{lid}")
                candidate_ids = [x for x in unit.get("shot_ids", []) if isinstance(x, str)] if isinstance(unit.get("shot_ids", []), list) else []
                matching_shots = [
                    sid for sid in candidate_ids
                    if sid in shots and any(_same_sync(sync, other) for other in _required_sync(shots[sid].get("lip_sync")))
                ]
                if not matching_shots:
                    missing.append({"line_id": lid, "shot_ids": candidate_ids, "missing": "covering-shot lip_sync"})
                speech = sync.get("speech_duration_s")
                if _valid_positive_number(speech):
                    for sid in matching_shots:
                        for shot_sync in _required_sync(shots[sid].get("lip_sync")):
                            if not _same_sync(sync, shot_sync):
                                continue
                            other = shot_sync.get("speech_duration_s")
                            if _valid_positive_number(other) and abs(float(speech) - float(other)) > 0.05:
                                timing_conflicts.append({
                                    "line_id": lid,
                                    "shot_id": sid,
                                    "shooting_duration_s": speech,
                                    "shot_duration_s": other,
                                })

    result = {
        "missing_lip_sync_coverage": _dedupe(missing),
        "lip_sync_speaker_conflicts": _dedupe(speaker_conflicts),
        "lip_sync_timing_conflicts": _dedupe(timing_conflicts),
        "lip_sync_line_conflicts": _dedupe(line_conflicts),
    }
    result["lip_sync_ready"] = not any(result[key] for key in (
        "missing_lip_sync_coverage",
        "lip_sync_speaker_conflicts",
        "lip_sync_timing_conflicts",
        "lip_sync_line_conflicts",
    ))
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate Story-Film visible-dialogue synchronization contracts.")
    ap.add_argument("project")
    args = ap.parse_args()
    errors = validate_project(Path(args.project).expanduser())
    if errors:
        for error in errors:
            print("ERROR", error)
        return 1
    print("OK dialogue sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
