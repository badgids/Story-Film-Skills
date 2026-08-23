# Generation Model Selection Compatibility Notice

Direct per-model/per-resource generation selection was retired in Story-Film Skills v0.0.31.

Read `WORKFLOW_SELECTION.md` before ComfyUI generation.

## Current authority

The user selects a **complete ComfyUI workflow** for each required generation task.

The selected workflow is the authority for the checkpoint or diffusion model, VAE, text encoder, LoRAs, audio models, upscalers, samplers, schedulers, nodes, and other concrete resource values stored in that graph.

Story-Film presents the relevant workflows as an ordinary numbered list. It does not use a four-option TUI model picker and it does not ask the user to reconstruct a workflow one model file at a time.

## Legacy files and commands

These remain available for compatibility and debugging:

```text
00_project/model_preferences.json
00_project/comfyui_model_inventory.json
scripts/model_inventory.py
scripts/model_preferences.py
```

They are not the generation-selection authority for workflow-first projects and must not override `00_project/workflow_preferences.json`.

Do not launch the old adapter/checkpoint/VAE/text-encoder/LoRA interview.

## Prompt adapters

Prompt adapters are still allowed when a selected workflow needs model-specific prompt grammar.

The selected workflow determines which adapter is relevant. Adapter choice is not a second user selection layer.

## Missing resources

A selected workflow can still fail validation because its graph references a model or node that is unavailable in the active ComfyUI server.

That is a blocker. Do not silently substitute another model or another workflow.

The user can edit and save the workflow, restore the dependency, select another numbered workflow, or choose the generated-workflow fallback described in `WORKFLOW_SELECTION.md`.
