---
name: comfyui-workflow
description: Detect ComfyUI UI versus API workflow JSON, inspect graph requirements, validate API workflows against live node schemas, patch named API inputs safely, preserve originals, and map story-film generation briefs onto executable live workflows without guessing node classes.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# ComfyUI Workflow

## Read

- `../../references/COMFYUI_WORKFLOWS.md`
- `../../references/COMFYUI_NATIVE_API.md`
- `../../references/COMFYUI_SECURITY.md`

## Procedure

1. Identify the workflow format.
2. If API format, inspect its required class types and links.
3. When a live server is available, validate every class against `/object_info` and verify required inputs.
4. Decide whether this is a throwaway graph or reusable source. For reusable/growing work and an available current comfy-cli, prefer template -> slots/decompose -> fragment/blueprint -> compose. For a small one-time API graph, patch the exact named input in a preserved copy.
5. For a UI-format workflow, use comfy-cli's supported run/conversion path when available or obtain an API export before native submission.
6. For a new graph, discover live nodes or an approved current template first. Do not construct class names from memory.
7. Confirm the requested result reaches a live output node or documented retrievable output path.
8. Save runnable project workflows under `04_generation/comfyui/workflows/`.

Bundled offline commands:

```text
python scripts/comfyui_workflow.py inspect WORKFLOW.json
python scripts/comfyui_workflow.py classes WORKFLOW.json
python scripts/comfyui_workflow.py patch WORKFLOW.json --node 12 --input text --value 'new prompt' --out patched.json
```

Live validation:

```text
python scripts/comfyui_control.py validate --workflow WORKFLOW.json
```

## Story-film mapping

When mapping `comfyui_handoff.json`, process one shot or cue at a time. Map only named inputs that the selected live workflow actually exposes. Canon and approved prompts remain authoritative.

## Done

The workflow format is known, required node classes are explicit, requested edits are minimal, and the runnable API graph passes the available preflight checks.
