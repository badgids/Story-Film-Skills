# Sanitized ComfyUI Workflows

[Documentation home](../README.md) | [Up: Generation](../README.md#4-image-audio-and-video-generation)

## Table of contents

- [Purpose](#purpose)
- [Included blueprints](#included-blueprints)
- [Promotion rules](#promotion-rules)
- [Related pages](#related-pages)

## Purpose

`references/comfyui_workflows/` contains sanitized UI-format workflow blueprints adapted from production workflows. They preserve useful graph topology while removing project-specific prompts, preview paths, personal machine paths, concrete model/checkpoint filenames, and output names where possible.

They are not executable defaults and do not override `00_project/model_preferences.json`.

## Included blueprints

- MiniMax H3 T2V, I2V, Ref2VA, and Ref2VA exact-audio hybrid;
- character, location, and prop reference sheets;
- FILM frame interpolation;
- NVIDIA RTX video upscale reference;
- FlyBird Qwen3-TTS reference;
- Stable Audio SFX reference;
- MiniMax Music API reference.

See `references/comfyui_workflow_dependencies.json` for optional node packages and `references/comfyui_workflow_contracts.json` for capability contracts.

## Promotion rules

Before a blueprint becomes runnable, the bounded workflow pipeline must inspect live `/object_info`, resolve selected resources, replace sanitized placeholders, validate the graph, audit reference bindings, and promote a preserved copy. Missing custom nodes are reported; Story-Film does not install them automatically.

## Related pages

- [Optional ComfyUI custom nodes](comfyui-optional-nodes.md)
- [Reference authority](../production/reference-authority.md)
- [Reference sheets](../production/reference-sheets.md)
