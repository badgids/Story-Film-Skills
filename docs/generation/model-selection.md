# Generation Model Selection Is Retired

[Documentation home](../README.md) | [Choose ComfyUI workflows](workflow-selection.md)

## Table of contents

- [Workflow-first selection](#workflow-first-selection)
- [Compatibility tools](#compatibility-tools)
- [Related pages](#related-pages)

## Workflow-first selection

Story-Film Skills no longer asks the user to assemble ComfyUI model stacks through a sequence of Pi TUI questions.

Starting with v0.0.31, generation is **workflow-first**.

Choose a complete workflow for each required task. The workflow already contains its checkpoint or diffusion model, VAE, text encoder, LoRAs, audio models, upscalers, node choices, and generation settings.

Use:

```bash
python scripts/workflow_catalog.py catalog . --category video --url http://127.0.0.1:8188
```

Story-Film prints the full relevant numbered list, even when it contains more than four options. Reply with the number you want.

Read [Choose ComfyUI workflows](workflow-selection.md) for built-in workflow directories, project defaults, saved ComfyUI workflows, templates, external workflow directories, materialization, and generated-workflow fallback.

## Compatibility tools

`model_preferences.json`, `model_inventory.py`, and `model_preferences.py` remain available for compatibility and low-level debugging, but they are not the generation-selection authority for workflow-first projects.

## Related pages

- [Choose ComfyUI workflows](workflow-selection.md)
- [ComfyUI generation](comfyui.md)
- [Resource-safe local generation](resource-safe.md)
