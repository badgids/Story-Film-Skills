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
- `../../references/MODEL_SELECTION.md`

## Procedure

1. Run `scripts/comfyui_control.py --project PROJECT workflow-catalog` before constructing a new executable graph.
2. Select the first suitable source in this order: already validated project workflow; project template; saved ComfyUI user workflow; official core template; installed custom-node example workflow.
3. Fetch/copy the selected source without overwriting it. A failed runnable copy is repaired minimally; it is never replaced wholesale by a guessed model-family graph.
4. Identify the workflow format.
5. If API format, inspect its required class types and links.
6. When a live server is available, validate every class against `/object_info` and verify required inputs.
7. Read `00_project/model_preferences.json` and the current ComfyUI model inventory when model-specific resources are part of the graph. A selected workflow must use the user's exact active profile. If the graph names a different checkpoint, diffusion model, VAE, text encoder, LoRA, audio model, upscaler, or other selected resource, block and repair the mapping instead of letting the workflow override the user's selection.
8. Decide whether this is a throwaway graph or reusable source. For reusable/growing work and an available current comfy-cli, prefer template -> slots/decompose -> fragment/blueprint -> compose. For a small one-time API graph, patch the exact named input in a preserved copy.
9. For a UI-format workflow, use comfy-cli's supported run/conversion path when available or obtain an API export before native submission.
10. Only when no suitable existing source exists may a new API candidate be constructed from live-discovered schemas. Do not construct class names from memory. Write it outside the runnable workflows directory first, then use `workflow-promote`; invalid candidates are not promoted.
11. Confirm the requested result reaches a live output node or documented retrievable output path.
12. Save only live-validated runnable API graphs under `04_generation/comfyui/workflows/`.

Prompt adapters such as `qwen-image-2512` are not executable workflow specifications. Never translate an adapter/model-family label into a guessed `class_type`, API node, checkpoint name, or loader chain.

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

Workflow discovery and source preservation:

```text
python scripts/comfyui_control.py --project PROJECT workflow-catalog --query image
python scripts/comfyui_control.py --project PROJECT workflow-fetch --source core --name TEMPLATE --out 04_generation/comfyui/templates/TEMPLATE.json
python scripts/comfyui_control.py --project PROJECT workflow-promote --candidate CANDIDATE.json --out 04_generation/comfyui/workflows/SHOT-001.json
```

## Story-film mapping

When mapping `comfyui_handoff.json`, process one shot or cue at a time. Map only named inputs that the selected live workflow actually exposes. Canon and approved prompts remain authoritative.

## Done

The workflow format is known, required node classes are explicit, requested edits are minimal, and the runnable API graph passes the available preflight checks.
