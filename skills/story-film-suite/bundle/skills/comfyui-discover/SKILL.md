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

1. Use the user-supplied server URL when present. Otherwise use the configured environment URL or loopback default.
2. Probe the server before doing generation work.
3. Read system stats and features.
4. Query exact node classes or filtered node catalog only when the task needs them.
5. Query model categories and filenames only when model availability matters. Use `/models` and `/models/{folder}` through the bundled client or `model_inventory.py`; these server registries include model roots registered through `extra_model_paths.yaml`.
6. Use `/object_info` for node schemas. Its node input schema is under `input.required` and `input.optional`. Do not treat an empty result from an incorrectly parsed `inputs` field as evidence that models are missing.
7. Save a project snapshot to `04_generation/comfyui/server_snapshot.json` when reproducibility or later diagnosis benefits.

Bundled commands:

```text
python scripts/comfyui_control.py probe
python scripts/comfyui_control.py nodes --query <term>
python scripts/comfyui_control.py models
python scripts/comfyui_control.py models --folder <category>
```

## Do not

- scan the filesystem for guessed personal ComfyUI paths or model files; use the server model registry instead
- write one-off model inventory scripts or raw `/models` curl loops when `model_inventory.py` is available; use the bundled inventory tool for Story-Film model selection
- infer that models are absent because they are outside the ComfyUI application directory
- create mock media or download substitute models when discovery is incomplete
- assume a custom node exists from an online workflow
- treat a stale saved snapshot as current capability data
- guess model filenames from model family names

## Done

The next step has live evidence for the server, required node classes, and relevant models instead of assumptions.
