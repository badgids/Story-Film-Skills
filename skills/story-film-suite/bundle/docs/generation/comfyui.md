# ComfyUI Generation

[Documentation home](../README.md) | [Up: Story to film](../workflows/story-to-film.md) | [Next: Resource-safe generation](resource-safe.md)

## Table of contents

- [Purpose](#purpose)
- [Before generation](#before-generation)
- [Prepare a workflow](#prepare-a-workflow)
- [Run work](#run-work)
- [Check outputs](#check-outputs)
- [When memory is limited](#when-memory-is-limited)

## Purpose

ComfyUI performs configured image, audio, and video generation. Story-Film Skills prepares the creative instructions and the workflow data.

Story-Film Skills does not treat a queued job as a finished asset. An output must return to the media registry and pass the required checks.

## Before generation

Do these actions before you spend GPU time:

1. Freeze the creative decisions that affect the job.
2. Give the item a stable ID such as `SHOT-###`, `VOICE-###`, `MUS-###`, or `SFX-###`.
3. Select a compatible ComfyUI workflow.
4. Confirm that required model files and custom nodes exist.
5. Confirm that reference images and other inputs exist.
6. Validate the API-format workflow.
7. Set an output destination.

Do not make ComfyUI guess missing story facts.

## Prepare a workflow

Use the workflow tools to inspect and validate a workflow:

```bash
python scripts/comfyui_workflow.py detect workflow.json
python scripts/comfyui_workflow.py inspect workflow.json
python scripts/comfyui_control.py validate --workflow workflow.json
```

A live validation checks the workflow against the running ComfyUI server.

## Run work

For small work, Story-Film Skills can submit and wait for a job directly.

For a large prepared set, use the offline batch format. The batch uses `BATCH-###` and `JOB-###` IDs.

The batch can include dependency edges. A job starts only when its blockers are complete.

## Check outputs

After generation:

1. Record the output file.
2. Link it to the source item.
3. Run media QC when required.
4. Mark the file as a candidate, primary, alternate, rejected, or superseded.
5. Do not use newest-file-wins behavior.

## When memory is limited

If the local LLM and the ComfyUI model cannot fit in memory at the same time, use [Resource-safe local generation](resource-safe.md).

## Related pages

- [Resource-safe local generation](resource-safe.md)
- [RAM and VRAM budgets](memory-budget.md)
- [Partial batch recovery](batch-recovery.md)
- [Production health](../production/health.md)
