---
name: editor-project-export
description: Export canonical film editorial state as editable Kdenlive and/or Shotcut projects using a shared multitrack MLT-based manifest, target-specific serializers, project-relative media, effects/transitions, subtitles, and structural validation.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Editor Project Export

## Workflow

1. Read `../../references/EDITOR_PROJECT_EXPORT.md` and `../../references/MLT_TOOLKIT.md`.
2. If only the executable timeline exists, derive `05_post/editorial/editor_project.json` from it.
3. If the user needs layered editing, build the advanced editor manifest with explicit bin clips, V/A tracks, placements, filters, transitions, subtitles, and notes.
4. Read `kdenlive-export`, `shotcut-export`, or both according to the requested target.
5. Query MLT services before relying on optional effects or transitions.
6. Run `scripts/editor_project_export.py` with source existence validation when media is available.
7. Parse and target-validate every generated XML project.
8. Never report that a GUI editor opened the project unless that editor was actually available and the integration check was performed.

## Done

Every requested editor project file exists and passes target-specific structural validation, with project-relative media references and no invented private schema.
