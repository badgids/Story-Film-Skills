#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Shared style-policy exemptions for Story-Film Skills."""
from __future__ import annotations

import json
from pathlib import Path


PROJECT_WORKFLOW_DIRS = {'default_workflows', 'workflows', 'templates'}


def _lower_parts(path: Path) -> tuple[str, ...]:
    return tuple(part.lower() for part in path.parts)


def _known_workflow_path(path: Path) -> bool:
    if path.suffix.lower() != '.json':
        return False

    parts = _lower_parts(path)
    if 'comfyui_workflows' in parts:
        return True

    for i in range(len(parts) - 2):
        if parts[i] != '04_generation' or parts[i + 1] != 'comfyui':
            continue
        if parts[i + 2] in PROJECT_WORKFLOW_DIRS:
            return True
    return False


def is_comfyui_workflow_json(path: Path, text: str) -> bool:
    """Return True only for JSON that should be treated as ComfyUI workflow data.

    Known Story-Film workflow directories are authoritative. For workflows kept
    elsewhere, recognize the two common ComfyUI representations: UI graph JSON
    with nodes/links and API prompt JSON keyed by node id with class_type/inputs.
    """
    if _known_workflow_path(path):
        return True
    if path.suffix.lower() != '.json':
        return False

    try:
        obj = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return False
    if not isinstance(obj, dict):
        return False

    if isinstance(obj.get('nodes'), list) and isinstance(obj.get('links', []), list):
        return True

    if obj and all(
        isinstance(node, dict)
        and isinstance(node.get('class_type'), str)
        and isinstance(node.get('inputs', {}), dict)
        for node in obj.values()
    ):
        return True
    return False
