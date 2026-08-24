# Command Reference

[Documentation home](../README.md) | [Up: Reference](../README.md#8-reference) | [Next: Glossary](glossary.md)

## Table of contents

- [Pi package installation](#pi-package-installation)
- [Project](#project)
- [Progress](#progress)
- [Feature scale](#feature-scale)
- [Generation](#generation)
- [Postproduction and release](#postproduction-and-release)
- [Tests](#tests)

## Project

```bash
python scripts/init_story_project.py PROJECT
python scripts/validate_story_project.py PROJECT
```

## Progress

```bash
python scripts/pipeline_progress.py init PROJECT --playbook feature-film
python scripts/pipeline_progress.py status PROJECT
python scripts/pipeline_progress.py checkpoint PROJECT --status completed
python scripts/pipeline_progress.py pause PROJECT
python scripts/pipeline_progress.py resume PROJECT
```

## Feature scale

```bash
python scripts/sequence_manager.py PROJECT init
python scripts/context_shards.py PROJECT build --all
python scripts/production_health.py PROJECT report
python scripts/long_range_continuity.py PROJECT check
python scripts/generation_scheduler.py PROJECT build
python scripts/recovery_checkpoint.py PROJECT checkpoint
python scripts/recovery_checkpoint.py PROJECT resume
python scripts/batch_recovery.py PROJECT build
python scripts/editorial_reconcile.py PROJECT check
python scripts/completeness_audit.py PROJECT check
```

Use `--help` on each script for all arguments.

## Generation

Workflow-first selection:

```bash
python scripts/workflow_catalog.py catalog PROJECT --category video
python scripts/workflow_catalog.py choose PROJECT 3
python scripts/workflow_catalog.py show PROJECT
python scripts/workflow_catalog.py materialize PROJECT video
```

ComfyUI inspection and execution helpers:

```bash
python scripts/comfyui_control.py --project PROJECT probe
python scripts/comfyui_workflow.py inspect WORKFLOW.json
python scripts/comfy_workflow_contracts.py WORKFLOW.json --contract minimax-h3-r2v
python scripts/comfy_binding_audit.py PROJECT
python scripts/reference_authority.py PROJECT
python scripts/temporal_continuity.py validate PROJECT
python scripts/dialogue_audio_authority.py PROJECT
python scripts/dialogue_timing_preflight.py PROJECT
python scripts/reference_sheets.py PROJECT
python scripts/staged_grounding.py PROJECT
python scripts/media_lifecycle.py PROJECT --help
python scripts/resource_handoff.py --help
python scripts/comfyui_batch.py --help
```

Legacy model inventory/preferences utilities remain available for compatibility and diagnostics, but workflow selection is the generation authority.

## Postproduction and release

```bash
python scripts/media_toolkit.py discover --project PROJECT --deep
python scripts/editor_project_export.py PROJECT --target both
python scripts/release_package.py --help
```

## Tests

```bash
python scripts/regression_suite.py
python scripts/local_smoke.py --help
```

## Pi package installation

Install the public repository for the user:

```bash
pi install https://github.com/badgids/Story-Film-Skills.git
```

Install only for the current project:

```bash
pi install -l https://github.com/badgids/Story-Film-Skills.git
```

Load only for the current Pi process:

```bash
pi -e https://github.com/badgids/Story-Film-Skills.git
```

If GitHub SSH authentication is already configured, the equivalent SSH source is `git:git@github.com:badgids/Story-Film-Skills.git`.

Install a local checkout only for the current project:

```bash
pi install -l /absolute/path/to/Story-Film-Skills
```

See [Pi install and project isolation](../getting-started/pi-install.md).

## Related pages

- [Choose ComfyUI workflows](../generation/workflow-selection.md)
- [Testing](../development/testing.md)
- [Quick start](../getting-started/quick-start.md)
