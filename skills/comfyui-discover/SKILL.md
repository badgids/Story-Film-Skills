---
name: comfyui-discover
description: Inspect a live ComfyUI server for version, hardware, feature flags, queue depth, installed node schemas, model categories, and model filenames before selecting or validating a workflow.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# ComfyUI Discover

## Read

- `../../references/COMFYUI_OPERATIONS.md`
- `../../references/COMFYUI_NATIVE_API.md`

## Procedure

1. In Pi, begin with `story_comfy action=server-info`. Do this before any shell, filesystem, or guessed-path attempt to locate ComfyUI.
2. Use the user-supplied server URL when present. Otherwise use the configured environment URL or loopback default.
3. Probe the server before doing generation work.
4. Read system stats and features.
5. Query exact node classes or filtered node catalog only when the task needs them. In Pi use `story_comfy action=node-search` or `action=node-info`.
6. Before building a workflow, run the bundled workflow catalog. In Pi use `story_comfy action=workflow-catalog`. It combines Story-Film's included workflows, project/user-added workflows, and the user's saved ComfyUI workflows. It does not query ComfyUI core/custom template catalogs.
7. Query model categories and filenames only when model availability matters. In Pi use `story_comfy action=model-inventory` and `action=model-search`. The server registries include model roots registered through `extra_model_paths.yaml`.
8. Use `/object_info` through Story-Film's managed/native control layer for node schemas. Its node input schema is under `input.required` and `input.optional`. Do not treat an empty result from an incorrectly parsed `inputs` field as evidence that models are missing.
9. Save a project snapshot to `04_generation/comfyui/server_snapshot.json` when reproducibility or later diagnosis benefits.

Bundled commands:

```text
python scripts/comfyui_control.py probe
python scripts/comfyui_control.py nodes --query <term>
python scripts/comfyui_control.py models
python scripts/comfyui_control.py --project PROJECT workflow-catalog --query <term>
python scripts/comfyui_control.py models --folder <category>
```

## Do not

- use Bash, `find`, `ls`, `which`, `locate`, directory globbing, home-directory scans, or guessed personal paths to locate ComfyUI or model files; use `story_comfy` and the live server registry instead
- infer that ComfyUI is absent from a failed `cd`, a missing guessed directory, or a failed filesystem search
- infer that models are absent from an empty guessed `checkpoints`, `vae`, `loras`, `unet`, or `diffusion_models` directory
- invoke managed comfy-cli discovery commands directly through Bash when `story_comfy` can perform the operation
- write one-off model inventory scripts or raw `/models` curl loops when `model_inventory.py` is available; use the bundled inventory tool for Story-Film model selection
- search `/workflow_templates` or ComfyUI core/custom template catalogs; if the user wants a template, they must save or copy it into their ComfyUI workflow area first
- write one-off `/userdata`, `/object_info`, or `/prompt` parsers/loops when the bundled controller already owns workflow discovery and execution
- infer that models are absent because they are outside the ComfyUI application directory
- create mock media or download substitute models when discovery is incomplete
- assume a custom node exists from an online workflow
- treat a stale saved snapshot as current capability data
- guess model filenames from model family names

## Done

The next step has live evidence for the server, required node classes, and relevant models instead of assumptions.
