# ComfyUI Generation

[Documentation home](../README.md) | [Up: Story to film](../workflows/story-to-film.md) | [Next: Resource-safe generation](resource-safe.md)

## Table of contents

- [Purpose](#purpose)
- [Choose a workflow](#choose-a-workflow)
- [Workflow sources](#workflow-sources)
- [Before generation](#before-generation)
- [Prepare and validate the selected workflow](#prepare-and-validate-the-selected-workflow)
- [Optional nodes](#optional-nodes)
- [Run work](#run-work)
- [Check outputs](#check-outputs)
- [When memory is limited](#when-memory-is-limited)

## Purpose

ComfyUI performs configured image, audio, and video generation. Story-Film Skills prepares the creative instructions, selects a complete user-approved workflow, stages project inputs, and validates a project-owned copy.

A queued job is not a finished asset. An output must return to the media registry and pass the required checks.

## Choose a workflow

Story-Film uses workflow-first generation.

For each required task, Story-Film builds a numbered catalog and asks you to choose a workflow by number.

Typical tasks include:

- image generation
- image editing
- video
- TTS
- music
- SFX/Foley
- character sheets
- orbit or multiple-angle sheets
- location orbits
- storyboards
- upscaling
- frame interpolation

The workflow contains the concrete checkpoint/model, VAE, encoders, LoRAs, nodes, samplers, and other settings. Story-Film does not follow workflow selection with a second TUI interview for those model files.

Read [Choose ComfyUI workflows](workflow-selection.md).

## Workflow sources

Story-Film offers workflows only from its extension library:

- built-ins from `comfyui_workflows/<task>/<model>/`;
- custom workflows copied into `comfyui_workflows/custom/<task>/<model>/`.

It does not scan project workflow folders, ComfyUI userdata/saved workflows, arbitrary external directories, or ComfyUI template catalogs. If you want Story-Film to use another workflow, copy the exported JSON into the appropriate `comfyui_workflows/custom/<task>/<model>/` directory and refresh the catalog.

The ordinary numbered list can contain more than four entries.

## Before generation

Before spending GPU time:

1. freeze the creative decisions that affect the job;
2. give the item a stable ID such as `SHOT-###`, `VOICE-###`, `MUS-###`, or `SFX-###`;
3. select the complete workflow for the task;
4. materialize a project-owned copy of the selected extension workflow;
5. confirm that required model files and custom nodes used by that workflow exist;
6. confirm that reference images and other inputs exist and their authority scopes fit the job;
7. validate the workflow-family contract when one exists and validate the executable graph against live `/object_info`;
8. audit prompt/reference bindings so labels, `REF-###`/`MEDIA-###`, staged files, hashes, and graph inputs agree;
9. run dialogue timing preflight and approved-audio checks when visible dialogue is involved;
10. set an output destination.

Do not make ComfyUI guess missing story facts.

## Prepare and validate the selected workflow

Build the catalog:

```bash
python scripts/workflow_catalog.py catalog . --category video --url http://127.0.0.1:8188
```

Record the user's numbered choice:

```bash
python scripts/workflow_catalog.py choose . 2
```

Materialize the selected source:

```bash
python scripts/workflow_catalog.py materialize . video --url http://127.0.0.1:8188
```

Inspect or validate the resulting workflow through the normal tools:

```bash
python scripts/comfyui_workflow.py inspect workflow.json
python scripts/comfyui_control.py validate --workflow workflow.json
```

For UI-format workflows, use the supported conversion/preservation route before native API submission.

If a workflow references a missing model or node, report the blocker. Do not silently replace its model stack.

## Optional nodes

Bundled or user-selected workflows can depend on optional custom-node packages.

Read [Optional ComfyUI custom nodes](comfyui-optional-nodes.md). Story-Film reports missing nodes but does not install custom-node code automatically.

## Run work

For small work, Story-Film can submit and wait for a job directly.

For a large prepared set, use the offline batch format. The batch uses `BATCH-###` and `JOB-###` IDs.

The batch can include dependency edges. A job starts only when its blockers are complete.

## Check outputs

After generation:

1. record the output file;
2. link it to the source item;
3. run media QC when required;
4. mark the file as a candidate, primary, alternate, rejected, or superseded;
5. do not use newest-file-wins behavior.

## When memory is limited

If the local LLM and the ComfyUI model cannot fit in memory at the same time, use [Resource-safe local generation](resource-safe.md). The selected workflows and all required input mappings must be finalized before the LLM is unloaded.

## Related pages

- [Choose ComfyUI workflows](workflow-selection.md)
- [Optional ComfyUI custom nodes](comfyui-optional-nodes.md)
- [Resource-safe local generation](resource-safe.md)
- [RAM and VRAM budgets](memory-budget.md)
- [Partial batch recovery](batch-recovery.md)
- [Production health](../production/health.md)
