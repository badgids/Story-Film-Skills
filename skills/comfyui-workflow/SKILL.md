---
name: comfyui-workflow
description: Select, preserve, inspect, validate, patch, convert, and promote complete ComfyUI workflows from Story-Film's workflow library, project defaults, saved ComfyUI workflows, templates, external sources, or live-schema generation.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# ComfyUI Workflow

## Read

- `../../references/WORKFLOW_SELECTION.md`
- `../../references/COMFYUI_WORKFLOWS.md`
- `../../references/COMFYUI_NATIVE_API.md`
- `../../references/COMFYUI_SECURITY.md`
- `../../references/COMFYUI_BOUNDED_WORKFLOW.md`
- `../../references/COMFYUI_WORKFLOW_CONTRACTS.md`
- `../../references/REFERENCE_AUTHORITY.md`
- `../../references/DIALOGUE_AUDIO_AUTHORITY.md`

## Workflow-first rule

A complete selected workflow is the generation configuration.

Do not ask the user to rebuild its model stack through separate adapter/checkpoint/VAE/text-encoder/LoRA questions. Do not let legacy `model_preferences.json` override the selected workflow.

Before constructing a new graph:

1. read `generation-workflow-setup`;
2. build the relevant numbered workflow catalog with `scripts/workflow_catalog.py`;
3. let the user choose by number;
4. record the selection;
5. materialize a project-owned copy.

Bundled workflow sources are under `../../comfyui_workflows/<task>/<model>/`. They are actual editable workflows, not sanitized blueprints.

## Bounded production workflow path

For ordinary Story-Film production recovery or workflow creation, use the Pi-native `story_comfy_workflow` tool when available after a workflow has been selected/materialized.

1. Start from the exact selected project-owned source.
2. Preserve that source. Never edit the bundled, saved-ComfyUI, template, or external original in place.
3. Identify UI versus API format.
4. Inspect the graph and required node classes.
5. When a live server is available, validate every required class and input against `/object_info`.
6. Verify the concrete model/resource names already stored in the workflow against the active server and node dropdowns where applicable.
7. Stage current project inputs and references.
8. Patch only named production values that the selected graph actually exposes: approved prompts, project input identities, output prefixes/IDs, requested dimensions, seeds, durations, or other explicit production parameters.
9. Run workflow-family contract validation when a contract applies.
10. For reference-driven graphs, write/audit `04_generation/comfyui/reference_bindings.jsonl` so prompt ordinals, graph inputs, `REF-###`/`MEDIA-###`, staged paths, and hashes agree.
11. Confirm the requested result reaches a live output node or documented retrievable output path.
12. Promote only a live-validated runnable API graph into `04_generation/comfyui/workflows/`.

If finalization reports a graph error, repair only the selected project-owned copy and retry. Do not replace it wholesale with a guessed model-family graph.

## Source discovery

The numbered workflow catalog can contain:

- Story-Film built-ins;
- package custom defaults;
- project defaults;
- existing project workflows/templates;
- the user's saved ComfyUI workflows;
- ComfyUI core templates;
- installed custom-node templates;
- user-registered external workflow files/directories;
- a `generate-new` choice.

There is no four-choice limit.

## Generate-new fallback

Only when the user selects the catalog's `generate-new` entry may Story-Film author a new candidate.

Use only live-discovered schemas. Do not construct class names from memory. Write the candidate outside the runnable workflow directory, validate it, then promote it. Missing custom nodes are blockers; do not install them automatically.

After the generated workflow is saved into the project, refresh the workflow catalog so it becomes a normal selectable project workflow.

## Model and prompt behavior

The selected workflow owns its concrete checkpoint, diffusion model, VAE, text encoders, LoRAs, audio models, upscalers, and node-specific model fields.

Prompt adapters remain allowed for prompt grammar. Infer the applicable prompt adapter from the selected workflow/model family when needed; do not ask for a second generation model selection.

If a selected workflow names unavailable resources, report the blocker. Do not silently swap to another model or workflow.

## Bundled offline commands

```text
python scripts/comfyui_workflow.py inspect WORKFLOW.json
python scripts/comfyui_workflow.py classes WORKFLOW.json
python scripts/comfyui_workflow.py patch WORKFLOW.json --node 12 --input text --value 'new prompt' --out patched.json
```

Workflow selection and materialization:

```text
python scripts/workflow_catalog.py catalog PROJECT --category video --url http://127.0.0.1:8188
python scripts/workflow_catalog.py choose PROJECT 3
python scripts/workflow_catalog.py materialize PROJECT video --url http://127.0.0.1:8188
```

Live validation:

```text
python scripts/comfyui_control.py validate --workflow WORKFLOW.json
```

## Story-Film mapping

When mapping `comfyui_handoff.json`, process one shot or cue at a time. Map only named inputs that the selected live workflow actually exposes. Canon and approved prompts remain authoritative.

## Done

The workflow choice is durable, the source is preserved, the project-owned copy is known, required node classes and resource names are explicit, requested edits are minimal, and the runnable API graph passes the available preflight checks.
