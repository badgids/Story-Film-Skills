#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

CHAR_RX = re.compile(r"^CHAR-\d{3,}$")
SCN_RX = re.compile(r"^SCN-\d{3,}$")

IDENTITY_LIST_FIELDS = {"physical_identifiers", "must_preserve", "must_not_be", "may_vary"}
SPEECH_LIST_FIELDS = {"habits", "pressure_changes", "must_not_do"}
MOVEMENT_LIST_FIELDS = {"habitual_actions", "pressure_changes", "must_not_do"}
STILLNESS_LIST_FIELDS = {"habits", "pressure_changes", "must_not_do"}
BASELINE_TEXT_FIELDS = {"room_shape", "leadership", "proximity", "conflict_pattern", "notes"}
RELATIONSHIP_TEXT_FIELDS = {"state", "power_balance", "notes"}


def load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _validate_list_fields(prefix: str, value: dict[str, Any], fields: set[str], errors: list[str]) -> None:
    for field in fields:
        if field in value and not _string_list(value[field]):
            errors.append(f"{prefix}.{field} must be an array of strings")


def validate_character_record(character_id: str, record: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return [f"canon.characters.{character_id} must be an object"]

    identity = record.get("identity")
    if identity is not None:
        if not isinstance(identity, dict):
            errors.append(f"canon.characters.{character_id}.identity must be an object")
        else:
            _validate_list_fields(f"canon.characters.{character_id}.identity", identity, IDENTITY_LIST_FIELDS, errors)

    signature = record.get("performance_signature")
    if signature is not None:
        if not isinstance(signature, dict):
            errors.append(f"canon.characters.{character_id}.performance_signature must be an object")
        else:
            sections = {
                "speech": SPEECH_LIST_FIELDS,
                "movement": MOVEMENT_LIST_FIELDS,
                "stillness": STILLNESS_LIST_FIELDS,
            }
            for section, list_fields in sections.items():
                value = signature.get(section)
                if value is None:
                    continue
                if not isinstance(value, dict):
                    errors.append(f"canon.characters.{character_id}.performance_signature.{section} must be an object")
                    continue
                _validate_list_fields(
                    f"canon.characters.{character_id}.performance_signature.{section}", value, list_fields, errors
                )
                for key, item in value.items():
                    if key in list_fields:
                        continue
                    if item is not None and not isinstance(item, (str, int, float, bool)):
                        errors.append(
                            f"canon.characters.{character_id}.performance_signature.{section}.{key} must be a scalar or string array"
                        )
    return errors


def relationship_pair_key(a: str, b: str) -> str:
    return "::".join(sorted((a, b)))


def validate_relationship_baselines(canon: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    characters = canon.get("characters", {}) if isinstance(canon.get("characters"), dict) else {}
    baselines = canon.get("relationship_baselines", {})
    if baselines is None:
        return errors
    if not isinstance(baselines, dict):
        return ["canon.relationship_baselines must be an object"]

    for key, record in baselines.items():
        prefix = f"canon.relationship_baselines.{key}"
        if not isinstance(record, dict):
            errors.append(f"{prefix} must be an object")
            continue
        pair = record.get("characters")
        if not isinstance(pair, list) or len(pair) != 2 or not all(isinstance(x, str) for x in pair):
            errors.append(f"{prefix}.characters must contain exactly two character IDs")
            continue
        a, b = pair
        if a == b:
            errors.append(f"{prefix}.characters must contain two distinct character IDs")
        for cid in pair:
            if not CHAR_RX.match(cid):
                errors.append(f"{prefix}: invalid character ID {cid!r}")
            elif characters and cid not in characters:
                errors.append(f"{prefix}: unresolved character ID {cid}")
        expected = relationship_pair_key(a, b)
        if key != expected:
            errors.append(f"{prefix}: key must be canonical pair {expected}")
        for field in BASELINE_TEXT_FIELDS:
            if field in record and record[field] is not None and not isinstance(record[field], str):
                errors.append(f"{prefix}.{field} must be a string")
    return errors


def validate_story_state_relationships(canon: dict[str, Any], state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    canon_chars = canon.get("characters", {}) if isinstance(canon.get("characters"), dict) else {}
    state_chars = state.get("characters", {})
    if not isinstance(state_chars, dict):
        return ["story_state.characters must be an object"]
    scene_order = state.get("scene_order", []) if isinstance(state.get("scene_order"), list) else []
    scene_ids = {x for x in scene_order if isinstance(x, str)}

    for cid, record in state_chars.items():
        if not isinstance(record, dict):
            continue
        relationships = record.get("relationships")
        if relationships is None:
            continue
        prefix = f"story_state.characters.{cid}.relationships"
        if not isinstance(relationships, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for target, value in relationships.items():
            item_prefix = f"{prefix}.{target}"
            if not CHAR_RX.match(target):
                errors.append(f"{item_prefix}: invalid character ID")
            elif canon_chars and target not in canon_chars:
                errors.append(f"{item_prefix}: unresolved character ID")
            if isinstance(value, str):
                continue  # v0.0.26 legacy form remains valid.
            if not isinstance(value, dict):
                errors.append(f"{item_prefix} must be a string or object")
                continue
            for field in RELATIONSHIP_TEXT_FIELDS:
                if field in value and value[field] is not None and not isinstance(value[field], str):
                    errors.append(f"{item_prefix}.{field} must be a string")
            changed = value.get("last_changed_in")
            if changed is not None:
                if not isinstance(changed, str) or not SCN_RX.match(changed):
                    errors.append(f"{item_prefix}.last_changed_in must be a SCN-### ID")
                elif scene_ids and changed not in scene_ids:
                    errors.append(f"{item_prefix}.last_changed_in {changed} is missing from scene_order")
    return errors


def validate_project(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    canon = load_json(root / "00_project/canon.json", {})
    if not isinstance(canon, dict):
        return ["00_project/canon.json must contain an object"]
    characters = canon.get("characters", {})
    if isinstance(characters, dict):
        for cid, record in characters.items():
            if isinstance(cid, str) and CHAR_RX.match(cid):
                errors.extend(validate_character_record(cid, record))
    errors.extend(validate_relationship_baselines(canon))

    state = load_json(root / "01_story/story_state.json", {})
    if state:
        if not isinstance(state, dict):
            errors.append("01_story/story_state.json must contain an object")
        else:
            errors.extend(validate_story_state_relationships(canon, state))
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate Story-Film character performance and relationship contracts.")
    ap.add_argument("project")
    args = ap.parse_args()
    errors = validate_project(Path(args.project).expanduser())
    if errors:
        for error in errors:
            print("ERROR", error)
        return 1
    print("OK character profiles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
