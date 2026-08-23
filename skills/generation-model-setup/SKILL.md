---
name: generation-model-setup
description: Compatibility redirect for pre-v0.0.31 projects. Story-Film generation is workflow-first; use generation-workflow-setup to select complete ComfyUI workflows instead of asking the user to assemble model/resource stacks.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Generation Model Setup

Direct interactive model/resource selection was retired in v0.0.31.

## Current behavior

1. Read `../../references/WORKFLOW_SELECTION.md`.
2. Read `../generation-workflow-setup/SKILL.md`.
3. Do not ask the user to choose adapters, checkpoints, diffusion models, VAEs, text encoders, LoRAs, audio models, upscalers, or frame-interpolation models one at a time.
4. Do not use `ask_user_question` or another four-option TUI picker for generation configuration.
5. Build the complete relevant workflow catalog and show it as an ordinary numbered list.
6. Let the user select the complete workflow by number.
7. Record the workflow in `00_project/workflow_preferences.json`.
8. Treat the concrete resource names stored in the selected workflow as part of that workflow choice.
9. Validate the selected workflow against the active ComfyUI server before execution.

## Legacy data

`00_project/model_preferences.json`, `scripts/model_inventory.py`, and `scripts/model_preferences.py` can still be used to inspect or migrate older projects and for low-level diagnostics.

They must not override a workflow selected through `generation-workflow-setup`.

## Done

This compatibility skill is done when control has moved to `generation-workflow-setup`.
