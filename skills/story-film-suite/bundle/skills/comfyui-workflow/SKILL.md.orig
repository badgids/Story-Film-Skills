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
- `../../references/COMFYUI_BOUNDED_WORKFLOW.md`

## Procedure

### Bounded production workflow path

For ordinary Story-Film production recovery or workflow creation, use the Pi-native `story_comfy_workflow` tool before the lower-level procedure below.

1. Call `story_comfy_workflow` with `action=prepare`, a concrete workflow/model query, and the media type.
2. The deterministic script owns source discovery/fetching, live node/model snapshots, and the build contract.
3. If no directly finalizable source exists, the LLM may adapt a preserved source or author exactly one canonical API graph using only the live schemas. The LLM builds the graph; it does not fan out shots or build the batch.
4. Put `__STORY_FILM_PROMPT__` in the positive-prompt input. Optional deterministic markers are `__STORY_FILM_NEGATIVE_PROMPT__` and `__STORY_FILM_FILENAME_PREFIX__`.
5. Pass the single canonical graph to `story_comfy_workflow` with `action=finalize`. Deterministic code owns live validation, approved-prompt reuse, per-shot fan-out, quarantine, offline-batch rebuild, and resource-handoff arming.
6. If finalization reports a graph error, repair only the canonical graph and retry. Do not create/install custom nodes as a fallback.
7. When finalization returns `waiting-for-agent-end`, stop backend work and end the agent turn cleanly.

See `../../references/COMFYUI_BOUNDED_WORKFLOW.md`.

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
