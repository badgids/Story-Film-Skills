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

1. Read the standalone contract, core contract, dependency rules, ComfyUI portable package contract, state, canon, continuity, references, and generation briefs.
2. Determine the smallest requested scope by sequence, scene, shot, cue, or stale asset.
3. Ensure model-neutral briefs exist for that scope.
4. Run the selected model adapters when prewritten prompts are part of the requested package.
5. Write `04_generation/comfyui_handoff.json` using project-relative paths only.
6. Include requested model families, prompt files, reference IDs and roles, required input media, expected output IDs, durations or dimensions when required, stale IDs, and unresolved requirements.
7. Never invent node class names, widget indices, local model paths, or private custom-node schemas. The portable manifest describes intent, not a guessed executable graph.
8. Run `prompt-qc` on included prompt documents.
9. If the user also requests execution, route next to `comfyui`: discover the live server, map the manifest into a preserved workflow copy, validate against live node schemas, stage inputs, submit, and collect outputs.

## Done

The standalone package contains enough generation intent for ComfyUI, another workflow compiler, another agent, or a human operator to map each task to an available workflow without reading the originating conversation. When execution was also requested, each submitted task is traceable to a live-validated workflow and returned prompt ID.
