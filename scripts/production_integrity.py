#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
from pathlib import Path

from comfy_binding_audit import validate_project as validate_bindings
from dialogue_audio_authority import validate_project as validate_audio
from dialogue_timing_preflight import validate_project as validate_timing
from reference_authority import validate_project as validate_references
from reference_sheets import validate_project as validate_sheets
from staged_grounding import validate_project as validate_grounding
from temporal_continuity import validate_project as validate_temporal

VALIDATORS = [
    ('reference authority', validate_references),
    ('temporal continuity', validate_temporal),
    ('dialogue audio authority', validate_audio),
    ('ComfyUI bindings', validate_bindings),
    ('reference sheets', validate_sheets),
    ('staged grounding', validate_grounding),
    ('dialogue timing', validate_timing),
]


def validate_project(root: Path) -> list[str]:
    errors: list[str] = []
    for label, validator in VALIDATORS:
        try:
            errors.extend(f'{label}: {error}' for error in validator(root))
        except Exception as exc:
            errors.append(f'{label}: validator failed: {exc}')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description='Run Story-Film production-integrity contracts.')
    parser.add_argument('project_dir')
    args = parser.parse_args()
    errors = validate_project(Path(args.project_dir).resolve())
    for error in errors:
        print('ERROR', error)
    print('OK production integrity' if not errors else f'FAILED {len(errors)}')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
