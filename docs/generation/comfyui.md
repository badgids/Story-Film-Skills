# ComfyUI Generation

[Documentation home](../README.md) | [Up: Story to film](../workflows/story-to-film.md) | [Next: Resource-safe generation](resource-safe.md)

## Table of contents

- [Purpose](#purpose)
- [Choose generation models and resources](#choose-generation-models-and-resources)
- [Before generation](#before-generation)
- [Prepare a workflow](#prepare-a-workflow)
- [Sanitized blueprints and optional nodes](#sanitized-blueprints-and-optional-nodes)
- [Run work](#run-work)
- [Check outputs](#check-outputs)
- [When memory is limited](#when-memory-is-limited)

## Purpose

ComfyUI performs configured image, audio, and video generation. Story-Film Skills prepares the creative instructions and the workflow data.

Story-Film Skills does not treat a queued job as a finished asset. An output must return to the media registry and pass the required checks.

## Choose generation models and resources

The user owns the model choices for image generation, image editing, video, TTS, music, SFX/Foley, upscaling, and frame interpolation.

Before model-specific generation, Story-Film Skills polls the running ComfyUI server and shows the installed model folders and model-like choices. The user can select exact checkpoints, diffusion models, VAEs, text encoders, LoRAs, audio encoders, upscalers, and other server-reported resources.

If the user does not choose a video adapter, Story-Film Skills uses **MiniMax H3** (`minimax-h3`). This default does not choose its concrete ComfyUI model files.

See [Choose generation models and ComfyUI resources](model-selection.md).

## Before generation

Do these actions before you spend GPU time:

1. Freeze the creative decisions that affect the job.
2. Give the item a stable ID such as `SHOT-###`, `VOICE-###`, `MUS-###`, or `SFX-###`.
3. Scan the active ComfyUI model inventory and record the user-selected model stack. Use the ComfyUI server registry, which includes external model directories configured through `extra_model_paths.yaml`. Do not search the filesystem for model files.
4. Select a compatible ComfyUI workflow.
5. Confirm that required model files and custom nodes exist. Report missing optional nodes; do not silently install them.
6. Confirm that reference images and other inputs exist and that their authority scopes are compatible with the job.
7. Validate the workflow-family contract and API-format workflow against live `/object_info`.
8. Audit prompt/reference bindings so labels, `REF-###`/`MEDIA-###`, staged files, hashes, and graph inputs agree.
9. Run dialogue timing preflight and approved-audio checks when visible dialogue is involved.
10. Set an output destination.

Do not make ComfyUI guess missing story facts.

## Prepare a workflow

Use the workflow tools to inspect and validate a workflow:

```bash
python scripts/comfyui_workflow.py detect workflow.json
python scripts/comfyui_workflow.py inspect workflow.json
python scripts/comfyui_control.py validate --workflow workflow.json
```

A live validation checks the workflow against the running ComfyUI server.

## Sanitized blueprints and optional nodes

Story-Film includes sanitized UI-format workflow blueprints under `references/comfyui_workflows/`. They are preserved topology sources, not executable defaults. They do not select model files for the user.

Read [Sanitized ComfyUI workflows](sanitized-workflows.md) and [Optional ComfyUI custom nodes](comfyui-optional-nodes.md) before adapting one. The dependency manifest is `references/comfyui_workflow_dependencies.json`.

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

- [Choose generation models and ComfyUI resources](model-selection.md)
- [Sanitized ComfyUI workflows](sanitized-workflows.md)
- [Optional ComfyUI custom nodes](comfyui-optional-nodes.md)
- [Resource-safe local generation](resource-safe.md)
- [RAM and VRAM budgets](memory-budget.md)
- [Partial batch recovery](batch-recovery.md)
- [Production health](../production/health.md)
