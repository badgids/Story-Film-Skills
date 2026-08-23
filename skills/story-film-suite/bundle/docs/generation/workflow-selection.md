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
- [Generate a new workflow](#generate-a-new-workflow)
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

The v0.0.32 release ships at least 29 workflow JSON files.
Twenty-six are ordinary production/reference workflows and three are retained research sources. User-added workflows are not capped and are not included in that release-minimum count.
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

1. [project-default] MiniMax-H3 - my_default_h3.json
2. [built-in] MiniMax-H3 - video_minimax_h3_i2v.json
3. [built-in] MiniMax-H3 - video_minimax_h3_r2v.json
4. [built-in] MiniMax-H3 - video_minimax_h3_r2v_exact_audio_hybrid.json
5. [built-in] MiniMax-H3 - video_minimax_h3_t2v.json
6. [comfyui-user] Unspecified - workflows/my_saved_video.json
7. [external] Unspecified - studio_video.json
8. [generate-new] Live ComfyUI schemas - Generate a new video workflow

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

### Project-local custom defaults

For custom defaults that belong to one film project, use:

```text
04_generation/comfyui/default_workflows/<task>/<model>/
```

This is usually safer than modifying the installed package because a package update does not replace the project directory.

These appear as `project-default`.

### Workflows you saved in ComfyUI

When Story-Film can reach the active ComfyUI server, it asks ComfyUI for the workflows saved in the user's workflow area.

You do not need to copy those files into Story-Film first.

A common workflow is:

1. open one of Story-Film's bundled workflows in ComfyUI;
2. change the checkpoint, VAE, text encoder, LoRA, sampler, scheduler, nodes, or other settings;
3. save the result as your own ComfyUI workflow;
4. refresh the Story-Film workflow catalog;
5. select your saved workflow by number.

### ComfyUI templates

Story-Film does not search ComfyUI core or custom-node template catalogs. If you want to use one, open it in ComfyUI and save it into your own workflow area, or export/register it as an external workflow. Story-Film will then see it as an ordinary user-saved or external workflow.

### Another workflow file or directory

Register another file:

```bash
python scripts/workflow_catalog.py source-add . /path/to/workflow.json
```

Register a directory:

```bash
python scripts/workflow_catalog.py source-add . /path/to/workflows
```

If automatic task detection is not clear, record the category:

```bash
python scripts/workflow_catalog.py source-add . /path/to/workflows --category video --model My-Video-Setup
```

Show registered sources:

```bash
python scripts/workflow_catalog.py source-list .
```

The project stores these registrations in:

```text
00_project/workflow_sources.json
```

Story-Film source code never hardcodes your personal workflow path.

## Materialize the selected workflow

Bundled workflows, external workflows, and saved ComfyUI workflows are preserved as sources.

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

- edit the workflow in ComfyUI and save a new version;
- install or restore the missing dependency yourself;
- choose another workflow number;
- ask Story-Film to generate a new workflow from the live node schemas.

## Generate a new workflow

When the catalog includes the `generate-new` choice and you select it, Story-Film can create one candidate using the live ComfyUI node schemas.

The candidate must use the bounded workflow-generation path and pass live validation. Story-Film must not invent node classes from memory and must not silently install custom nodes.

After the generated workflow is saved into the project, it becomes a normal project workflow and can be selected like every other workflow.

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
