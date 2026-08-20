---
name: generation-model-setup
description: Poll the active ComfyUI server and let the user choose the adapter/model family plus exact checkpoints, diffusion models, VAEs, text encoders, LoRAs, audio models, upscalers, and other installed resources for each Story-Film generation process.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Generation Model Setup

Use this skill before model-specific ComfyUI generation or when the user wants to change production models.

## Required behavior

1. Read `../../references/MODEL_SELECTION.md`.
2. Discover the active ComfyUI server with the native ComfyUI discovery capability.
3. Run `../../scripts/model_inventory.py scan <project-root> --url <server-url>`. This is the authoritative Story-Film model discovery command.
4. Treat the ComfyUI `/models` and `/models/{folder}` registry as authoritative for installed model filenames. ComfyUI resolves model roots registered through `extra_model_paths.yaml` and supported startup configuration before these endpoints answer. Do not assume models must live under the ComfyUI application directory.
5. Use `/object_info` only for installed node schemas and model-like dropdown choices. Current ComfyUI node definitions use `input.required` and `input.optional`, not a top-level `inputs` object. Do not use an ad hoc `/object_info` parser as a replacement for the model registry.
6. Determine which production processes are required.
7. For each required process, run `../../scripts/model_inventory.py menu <project-root> --process <process-id>`.
8. Show the resulting choices to the user.
9. Wait for the user's selection unless the user explicitly delegated that process.
10. Record the adapter/model family with `model_preferences.py set-adapter`.
11. Record exact resources with `model_preferences.py set-resource` and `add-lora`.
12. Run `model_preferences.py validate` before creating model-specific workflows.

## User-choice rule

Do not choose a resource because it appears first, has a familiar file name, is already referenced by an example workflow, or appears to fit the task.

MiniMax H3 is the default video adapter only when the user does not choose a video adapter. It does not imply any concrete checkpoint, VAE, text encoder, or LoRA choice.

For other production processes, no adapter is forced by default. Ask the user or use an explicitly delegated choice.

## Keep the list usable

If a ComfyUI folder contains many files, show one process at a time. Group choices by model folder. Preserve exact server-returned file names.

Do not rewrite, shorten, normalize, or guess file names.

Do not run `find /`, `find $HOME`, recursive filesystem searches, or guessed ComfyUI model-directory scans to decide which models are installed. Do not read or parse `extra_model_paths.yaml` unless the user explicitly asks to inspect that configuration. The running ComfyUI server has already resolved those paths.

If the authoritative inventory returns zero model filenames but the user expects models to exist, stop with a discovery blocker. Re-run the inventory, report the server URL and `/models` result, and ask the user to verify the running ComfyUI instance/configuration if needed. Do not claim that no models are installed, do not download replacements, and do not create mock or simulated generated media.

## Done

Done when every production process that needs model-specific generation has a recorded adapter/model-family decision and all required concrete resources are either selected or explicitly marked not required by the chosen workflow.
