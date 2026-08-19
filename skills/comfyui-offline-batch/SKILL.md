---
name: comfyui-offline-batch
description: Compile image, audio, and video generation into a complete deterministic ComfyUI batch that can execute without any LLM involvement after handoff.
author: Alan Guice (Badgids)
license: Apache-2.0
---

# ComfyUI Offline Batch

Read `../../references/COMFYUI_OFFLINE_BATCH.md` and `comfyui`.

Before handing memory from a local LLM to ComfyUI, ensure the batch contains everything the runner needs:

- final API-format workflow JSON for every job
- stable source IDs and job IDs
- all final prompt/text values
- all seeds, sizes, durations, frame/audio parameters, model selections, and workflow inputs
- exact project input files plus deterministic upload/patch mappings
- job dependency edges
- output directories and expected output kinds
- timeout/retry policy that never changes creative inputs
- already-approved paid-route consent where applicable

Run live schema/model validation before arming the resource handoff. Missing nodes/models or unresolved placeholders are blockers while the LLM is still available.

The offline runner may retry the identical job for transient transport/server failures. It must stop and return control to the LLM for any semantic change, prompt rewrite, model substitution, missing creative decision, or continuity repair.
