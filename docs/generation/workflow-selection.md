# Choose ComfyUI Workflows

[Documentation home](../README.md) | [Up: ComfyUI generation](comfyui.md) | [Next: Resource-safe generation](resource-safe.md)

## Table of contents

- [Purpose](#purpose)
- [Playbook preflight](#playbook-preflight)
- [Built-in workflow directory](#built-in-workflow-directory)
- [How to choose](#how-to-choose)
- [What Story-Film searches](#what-story-film-searches)
- [Materialize the selected workflow](#materialize-the-selected-workflow)
- [The workflow owns its model choices](#the-workflow-owns-its-model-choices)
- [Create or add a custom workflow](#creating-a-new-workflow)
- [Supplied workflow portability](#supplied-workflow-portability)
- [Current selections](#current-selections)
- [Related pages](#related-pages)

## Purpose

Story-Film Skills uses complete ComfyUI workflows as the generation choice.

You do not need to answer a long series of questions about adapters, checkpoints, VAEs, text encoders, LoRAs, audio models, or upscalers. Those concrete choices are already stored in the workflow you select.

Story-Film shows the workflows that are available for the current task as a normal numbered list. The list is not limited to four choices.

## Playbook preflight

When the selected playbook will use ComfyUI, Story-Film chooses all required workflow categories before story or canon work begins.
The empty project container may be initialized first so the selections have durable files.
Creative production does not begin until the workflow preflight is complete.

Later generation stages reuse the saved selections.
They do not stop to ask for the same workflow choices again unless you explicitly request a change.

Preflight state is stored in:

```text
00_project/workflow_preflight.json
```

Story-Film can inspect it with:

```bash
python scripts/workflow_preflight.py status .
```

## Built-in workflow directory

The built-in library is in the Story-Film Skills installation:

```text
comfyui_workflows/
```

It is organized by task first and model/workflow family second.

Examples from the v0.0.32 built-in library:

```text
comfyui_workflows/
  image/
    Krea2/
    Qwen-Image-2512/
  image-edit/
    Krea2/
    Qwen-Image-Edit/
  video/
    MiniMax-H3/
  tts/
    Qwen3-TTS/
  music/
    MiniMax-Music-3/
  sfx/
    Stable-Audio-3/
  character-sheet/
    Krea2/
    MiniMax-H3/
  orbit-sheet/
    Qwen-Image-Edit/
  location-orbit/
    MiniMax-H3/
  prop-sheet/
    MiniMax-H3/
  storyboard/
    Krea2/
  upscale/
    NVIDIA-RTX/
  frame-interpolation/
    FILM/
  llm/
    Qwen3/
    Qwen3.5/
    Qwen3-VL/
```

The extension ships at least 29 workflow JSON files in this baseline.
Twenty-six are ordinary production/reference workflows and three are retained research sources. Custom workflows placed under `comfyui_workflows/custom/` are not capped and are not included in that release-minimum count.
The 14 new Krea2 and Qwen files come from the user-supplied workflow archive.
Story-Film installs the workflow JSON files, not the source ZIP.

## How to choose

For a video workflow, Story-Film can run:

```bash
python scripts/workflow_catalog.py catalog . --category video --url http://127.0.0.1:8188
```

The output is an ordinary numbered list:

```text
Workflow choices for video:

1. [package-custom] MiniMax-H3 - my_custom_h3.json
2. [built-in] MiniMax-H3 - video_minimax_h3_i2v.json
3. [built-in] MiniMax-H3 - video_minimax_h3_r2v.json
4. [built-in] MiniMax-H3 - video_minimax_h3_r2v_exact_audio_hybrid.json
5. [built-in] MiniMax-H3 - video_minimax_h3_t2v.json

Reply with the number you want to use.
```

There can be more than four choices. Story-Film must not use a four-option TUI question to hide or divide this list.

After you choose a number:

```bash
python scripts/workflow_catalog.py choose . 4
```

Your selection is stored in:

```text
00_project/workflow_preferences.json
```

## What Story-Film searches

The catalog can combine all of these sources.

### Story-Film built-ins

```text
comfyui_workflows/<task>/<model>/
```

### Your package-level custom defaults

If you intentionally maintain custom files inside your Story-Film Skills installation, put them here:

```text
comfyui_workflows/custom/<task>/<model>/
```

Example shape:

```text
comfyui_workflows/custom/video/My-H3-Setup/my_h3_workflow.json
```

These appear as `package-custom`.

### Adding your own workflows

Story-Film does not scan project folders, ComfyUI userdata, template catalogs, or arbitrary external directories for workflow selection. To add a workflow, copy its JSON file into the extension library:

```text
comfyui_workflows/custom/<task>/<model>/
```

For example:

```text
comfyui_workflows/custom/video/My-H3-Setup/my_h3_workflow.json
```

Refresh the numbered catalog after copying the file. It will appear as `package-custom`. This keeps discovery deterministic and portable: every selectable Story-Film workflow is physically inside the extension.

## Materialize the selected workflow

Bundled and package-custom workflows are preserved as extension sources.

Before Story-Film edits one for the current production, it creates a project-owned copy:

```bash
python scripts/workflow_catalog.py materialize . video --url http://127.0.0.1:8188
```

The selected copy is stored under:

```text
04_generation/comfyui/templates/selected/<task>/
```

Story-Film can then stage current project inputs, patch approved prompts or output identities, validate the graph, and promote a runnable API workflow through the normal ComfyUI workflow path.

## The workflow owns its model choices

If a workflow says to load a specific checkpoint, diffusion model, VAE, text encoder, LoRA, audio model, or upscaler, those values are part of that workflow choice.

Story-Film does not ask you to select those same resources again in a separate TUI.

If the selected workflow references something your active ComfyUI server cannot load, Story-Film reports the blocker. It does not silently swap in another model.

You can:

- edit the workflow in ComfyUI and copy/export the new JSON into `comfyui_workflows/custom/<task>/<model>/`;
- install or restore the missing dependency yourself;
- choose another workflow number.

## Creating a new workflow

Story-Film still creates new ComfyUI workflows when the user explicitly asks it to create, build, author, or design one. That is a workflow-authoring operation, not another discovery source and not an automatic fallback row in every workflow menu.

For an explicit authoring request:

1. inspect the running ComfyUI server's live node and model schemas;
2. construct one bounded candidate from classes and inputs that actually exist;
3. keep the candidate outside `04_generation/comfyui/workflows/` until it passes validation;
4. validate required inputs, links, model/resource choices, and retrievable outputs;
5. promote a project-specific runnable graph only through the normal validated promotion path;
6. for a reusable Story-Film workflow, save or copy the validated JSON into `comfyui_workflows/custom/<task>/<model>/`;
7. refresh the extension workflow catalog so the new workflow becomes a normal `package-custom` numbered choice.

Do not invent node classes from memory. Missing custom nodes or models are blockers unless the user separately approves the required environment change.

A newly authored or exported workflow becomes selectable only after its JSON file is placed under `comfyui_workflows/custom/<task>/<model>/` and the catalog is refreshed. Live ComfyUI schemas are authoring/validation inputs; they are not a separate workflow-discovery source.

## Supplied workflow portability

The bundled workflows are preserved as supplied.

A ComfyUI export can contain author-local input-picker history or local paths from the computer on which it was saved. Those paths are not Story-Film machine configuration and are not treated as portable project inputs.

Story-Film works from a copy and replaces or stages project inputs as required before running the graph.

## Current selections

Show the selected workflows:

```bash
python scripts/workflow_catalog.py show .
```

Clear one selection:

```bash
python scripts/workflow_catalog.py clear . video
```

Then rebuild the numbered catalog and choose again.

## Related pages

- [ComfyUI generation](comfyui.md)
- [Optional ComfyUI custom nodes](comfyui-optional-nodes.md)
- [Resource-safe local generation](resource-safe.md)
- [RAM and VRAM generation budgets](memory-budget.md)
