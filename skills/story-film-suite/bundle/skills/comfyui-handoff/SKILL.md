---
name: comfyui-handoff
description: Build a standalone, portable ComfyUI-ready generation manifest containing canon links, references, shot briefs, prompt files, audio cues, model requests, input requirements, output IDs, stale scope, and unresolved requirements without hardcoded machine details.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# ComfyUI Handoff

This skill creates a portable generation package. It does not require ComfyUI or any other skill pack to be installed.

## Workflow

1. Read the standalone contract, core contract, dependency rules, model selection, ComfyUI portable package contract, state, canon, continuity, references, and generation briefs.
2. Determine the smallest requested scope by sequence, scene, shot, cue, or stale asset.
3. Ensure model-neutral briefs exist for that scope.
4. Read `MODEL_SELECTION.md`. For every required generation process, use the recorded user-selected adapter/model family and exact resource profile. If no video adapter was selected, use `minimax-h3` only as the video adapter default. Do not infer concrete resources from that default.
5. If a required process has no user-selected adapter/resource configuration, run `generation-model-setup` before model-specific packaging.
6. Run the selected model adapters when prewritten prompts are part of the requested package.
7. Write `04_generation/comfyui_handoff.json` using project-relative paths only.
8. Include requested model families and the `model_preferences`/inventory references, prompt files, reference IDs and roles, required input media, expected output IDs, durations or dimensions when required, stale IDs, and unresolved requirements.
9. Never invent node class names, widget indices, local model paths, or private custom-node schemas. The portable manifest describes intent, not a guessed executable graph.
10. Run `prompt-qc` on included prompt documents.
11. If the user also requests execution, route next to `comfyui`: discover the live server, map the manifest into a preserved workflow copy, validate against live node schemas, stage inputs, submit, and collect outputs.

## Done

The standalone package contains enough generation intent for ComfyUI, another workflow compiler, another agent, or a human operator to map each task to an available workflow without reading the originating conversation. When execution was also requested, each submitted task is traceable to a live-validated workflow and returned prompt ID.
