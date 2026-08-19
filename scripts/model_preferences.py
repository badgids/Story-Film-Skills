#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Manage explicit Story-Film generation-model preferences."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_VIDEO_MODEL = "minimax-h3"
ALLOWED_SOURCES = {"default", "user", "user-project", "delegated"}
NONDEFAULT_SOURCES = {"user", "user-project", "delegated"}


def path_for(root: Path) -> Path:
    return root / "00_project/model_preferences.json"


def default_preferences() -> dict:
    return {
        "schema_version": 1,
        "video": {
            "default_model": DEFAULT_VIDEO_MODEL,
            "selected_model": DEFAULT_VIDEO_MODEL,
            "selection_source": "default",
            "user_confirmed": False,
            "allow_agent_substitution": False,
            "shot_overrides": {},
        },
    }


def load(root: Path) -> dict:
    path = path_for(root)
    if not path.exists():
        return default_preferences()
    return json.loads(path.read_text(encoding="utf-8"))


def save(root: Path, obj: dict) -> Path:
    path = path_for(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    return path


def validate(obj: dict) -> list[str]:
    errors: list[str] = []
    if obj.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    video = obj.get("video")
    if not isinstance(video, dict):
        return errors + ["video must be an object"]
    if video.get("default_model") != DEFAULT_VIDEO_MODEL:
        errors.append(f"video.default_model must be {DEFAULT_VIDEO_MODEL}")
    selected = video.get("selected_model")
    if not isinstance(selected, str) or not selected.strip():
        errors.append("video.selected_model must be a non-empty string")
    source = video.get("selection_source")
    if source not in ALLOWED_SOURCES:
        errors.append("video.selection_source must be default, user, user-project, or delegated")
    if video.get("allow_agent_substitution") is not False:
        errors.append("video.allow_agent_substitution must be false")
    if selected and selected != DEFAULT_VIDEO_MODEL and source not in NONDEFAULT_SOURCES:
        errors.append("a non-default video model requires explicit user choice or delegated model selection")
    if selected and selected != DEFAULT_VIDEO_MODEL and video.get("user_confirmed") is not True:
        errors.append("a non-default video model must have user_confirmed=true")
    overrides = video.get("shot_overrides", {})
    if not isinstance(overrides, dict):
        errors.append("video.shot_overrides must be an object")
    else:
        for shot_id, row in overrides.items():
            if not str(shot_id).startswith("SHOT-"):
                errors.append(f"invalid shot override id {shot_id!r}")
                continue
            if not isinstance(row, dict) or not str(row.get("model", "")).strip():
                errors.append(f"{shot_id}: override must contain model")
                continue
            if row.get("source") not in NONDEFAULT_SOURCES:
                errors.append(f"{shot_id}: override requires user or delegated source")
    return errors


def cmd_show(root: Path) -> int:
    obj = load(root)
    print(json.dumps(obj, indent=2))
    return 0


def cmd_set_video(root: Path, model: str, source: str, note: str) -> int:
    if source not in NONDEFAULT_SOURCES:
        raise SystemExit("set-video requires --source user, user-project, or delegated")
    obj = load(root)
    video = obj.setdefault("video", {})
    video.update({
        "default_model": DEFAULT_VIDEO_MODEL,
        "selected_model": model,
        "selection_source": source,
        "user_confirmed": True,
        "allow_agent_substitution": False,
        "shot_overrides": video.get("shot_overrides", {}),
    })
    if note:
        video["note"] = note
    errors = validate(obj)
    if errors:
        raise SystemExit("; ".join(errors))
    print(save(root, obj))
    return 0


def cmd_reset_video(root: Path) -> int:
    obj = load(root)
    obj["video"] = default_preferences()["video"]
    print(save(root, obj))
    return 0


def cmd_validate(root: Path) -> int:
    errors = validate(load(root))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Manage Story-Film generation-model preferences.")
    sub = ap.add_subparsers(dest="command", required=True)
    for name in ("show", "reset-video", "validate"):
        p = sub.add_parser(name)
        p.add_argument("project_dir")
    p = sub.add_parser("set-video")
    p.add_argument("project_dir")
    p.add_argument("model")
    p.add_argument("--source", choices=sorted(NONDEFAULT_SOURCES), default="user")
    p.add_argument("--note", default="")
    args = ap.parse_args()
    root = Path(args.project_dir).expanduser().resolve()
    if args.command == "show":
        return cmd_show(root)
    if args.command == "set-video":
        return cmd_set_video(root, args.model, args.source, args.note)
    if args.command == "reset-video":
        return cmd_reset_video(root)
    return cmd_validate(root)


if __name__ == "__main__":
    raise SystemExit(main())
