# Project Folder Layout

[Documentation home](../README.md) | [Up: Reference](../README.md#8-reference) | [Next: Stable IDs](stable-ids.md)

## Table of contents

- [Main folders](#main-folders)
- [Feature-scale control files](#feature-scale-control-files)
- [Why the layout matters](#why-the-layout-matters)

## Main folders

A Story-Film project normally uses these top-level areas:

```text
00_project/        project state, dependencies, progress, recovery
01_story/          story research and narrative development
02_screenplay/     screenplay and scene/line structure
03_preproduction/  blocking, continuity, storyboards, references
04_generation/     prepared and generated image/audio/video work
05_post/           editorial, audio, video, masters, editor projects
06_release/        delivery, campaign, documents, final audits
```

## Feature-scale control files

Important v0.0.11 files include:

```text
00_project/sequence_manifest.json
00_project/sequence_manifest.md
00_project/shards/
00_project/health_report.json
00_project/health_report.md
00_project/recovery/
03_preproduction/continuity/anchors.jsonl
03_preproduction/continuity/long_range_report.md
04_generation/generation_schedule.md
05_post/editorial/reconciliation.md
06_release/completeness_audit.md
```

## Why the layout matters

Agents use project-relative paths. This makes the project portable between computers.

Do not put personal absolute machine paths into reusable project contracts.

## Related pages

- [Stable IDs](stable-ids.md)
- [Sequences and shards](../production/sequences-and-shards.md)
- [Core project schema](../../references/PROJECT_SCHEMA.md)
