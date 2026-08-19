---
name: resource-safe-generation
description: Coordinate local-first generation on machines where Pi's local LLM and ComfyUI models cannot safely occupy GPU or system memory at the same time, using a fully precompiled ComfyUI batch and a model-free runtime handoff.
author: Alan Guice (Badgids)
license: Apache-2.0
compatibility: Python 3. Optional local LLM lifecycle commands supplied by the user. Native ComfyUI HTTP API.
---

# Resource-Safe Generation

Read `../../references/RESOURCE_SAFE_GENERATION.md` and `../../references/COMFYUI_OFFLINE_BATCH.md`.

Use when the local LLM and ComfyUI generation models compete for VRAM/RAM.

Core rule: **the LLM must finish every creative decision and every ComfyUI instruction before it is unloaded.** The offline runner may execute, observe, retry transiently, collect outputs, and report state, but it may not invent prompts, choose new creative directions, repair semantics, or ask the unloaded model for help.

1. Finish prompts, references, workflow mapping, seeds/parameters, output identities, and acceptance metadata.
2. Build and validate `04_generation/comfyui/offline_batch.json` with `comfyui-offline-batch`.
3. Configure `00_project/resource_policy.json` with a verified local LLM unload/reload adapter when exclusive mode is required.
4. Arm `scripts/resource_handoff.py`. It starts a model-free runner and waits for the Pi agent turn to finish.
5. The Pi extension writes the release signal on `agent_end`; without the extension, the user can run the explicit release command.
6. The runner unloads the local LLM, executes the full ComfyUI batch deterministically, continuously updates project status/events, then calls ComfyUI `/free` with model unload and memory release.
7. The runner reloads the local LLM and writes `RESOURCE_RESUME.md` containing results/blockers for the next model turn.
8. If semantic repair is required, stop the batch, unload ComfyUI models, reload the LLM, and return the failed job plus evidence. Never improvise a new prompt while the LLM is absent.

The Pi progress extension renders resource phase and job progress from files on disk. These UI updates do not require an LLM call.
