#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Durable pre-story ComfyUI workflow-selection gate for Story-Film playbooks."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import workflow_catalog

STATE_REL = Path("00_project/workflow_preflight.json")
PREFERENCES_REL = Path("00_project/workflow_preferences.json")

FILM_PRODUCTION = (
    "image",
    "image-edit",
    "video",
    "tts",
    "music",
    "sfx",
    "character-sheet",
    "orbit-sheet",
    "location-orbit",
    "prop-sheet",
    "storyboard",
    "upscale",
    "frame-interpolation",
)

PROFILES = {
    "film-production": FILM_PRODUCTION,
    "visual-production": (
        "image",
        "image-edit",
        "video",
        "character-sheet",
        "orbit-sheet",
        "location-orbit",
        "prop-sheet",
        "storyboard",
        "upscale",
        "frame-interpolation",
    ),
    "audio-production": ("tts", "music", "sfx"),
}

PLAYBOOK_PROFILES = {
    "full-pipeline": "film-production",
    "short-film": "film-production",
    "feature-film": "film-production",
    "screenplay-to-film-package": "film-production",
    "resource-safe-comfyui": "film-production",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def project_root(value: str | Path) -> Path:
    root = Path(value).expanduser().resolve()
    if not (root / "00_project").is_dir():
        raise SystemExit(f"not a Story-Film project: {root}")
    return root


def _load(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _normalize_categories(values: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        category = workflow_catalog.normalize_category(value)
        if category and category not in out:
            out.append(category)
    return out


def required_categories(playbook: str, profile: str, categories: list[str]) -> tuple[str, list[str]]:
    if categories:
        return profile or "explicit", _normalize_categories(categories)
    selected_profile = profile or PLAYBOOK_PROFILES.get(playbook, "")
    if not selected_profile:
        raise SystemExit(
            "preflight scope is ambiguous; provide --profile or one or more --category values"
        )
    if selected_profile not in PROFILES:
        raise SystemExit(f"unknown workflow preflight profile: {selected_profile}")
    return selected_profile, list(PROFILES[selected_profile])


def refresh(root: Path, state: dict[str, Any]) -> dict[str, Any]:
    required = _normalize_categories([str(x) for x in state.get("required_categories", [])])
    prefs = _load(root / PREFERENCES_REL, {"selections": {}})
    selections = prefs.get("selections", {}) if isinstance(prefs, dict) else {}
    if not isinstance(selections, dict):
        selections = {}
    selected = [category for category in required if isinstance(selections.get(category), dict)]
    missing = [category for category in required if category not in selected]
    state.update(
        {
            "schema_version": 1,
            "required_categories": required,
            "selected_categories": selected,
            "missing_categories": missing,
            "status": "complete" if not missing else "needs-selection",
            "updated_at": now(),
        }
    )
    return state


def set_preflight(
    root: Path,
    *,
    playbook: str,
    profile: str,
    categories: list[str],
) -> dict[str, Any]:
    profile, required = required_categories(playbook, profile, categories)
    state = {
        "schema_version": 1,
        "playbook": playbook,
        "profile": profile,
        "required_categories": required,
        "selected_categories": [],
        "missing_categories": [],
        "status": "needs-selection",
        "created_at": now(),
        "updated_at": now(),
    }
    state = refresh(root, state)
    _write(root / STATE_REL, state)
    return state


def status(root: Path) -> dict[str, Any]:
    state = _load(
        root / STATE_REL,
        {
            "schema_version": 1,
            "playbook": "",
            "profile": "",
            "required_categories": [],
            "selected_categories": [],
            "missing_categories": [],
            "status": "not-required",
            "updated_at": "",
        },
    )
    if state.get("status") == "not-required" and not state.get("required_categories"):
        return state
    state = refresh(root, state)
    _write(root / STATE_REL, state)
    return state


def clear(root: Path) -> dict[str, Any]:
    state = {
        "schema_version": 1,
        "playbook": "",
        "profile": "",
        "required_categories": [],
        "selected_categories": [],
        "missing_categories": [],
        "status": "not-required",
        "updated_at": now(),
    }
    _write(root / STATE_REL, state)
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description="Story-Film pre-story ComfyUI workflow-selection gate")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("set")
    p.add_argument("project")
    p.add_argument("--playbook", default="")
    p.add_argument("--profile", choices=sorted(PROFILES), default="")
    p.add_argument("--category", action="append", default=[])
    p = sub.add_parser("status")
    p.add_argument("project")
    p = sub.add_parser("clear")
    p.add_argument("project")
    args = parser.parse_args()
    root = project_root(args.project)
    if args.command == "set":
        result = set_preflight(
            root,
            playbook=args.playbook.strip(),
            profile=args.profile.strip(),
            categories=args.category,
        )
    elif args.command == "status":
        result = status(root)
    else:
        result = clear(root)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.command == "status" and result.get("status") == "needs-selection":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
