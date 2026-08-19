---
name: story-film
description: Route story writing, books, screenwriting, directing, creative decision discovery, production specifications and work units, narrative state, creative review, storyboards, executable production, resource-safe AI media generation, generalized asset approval, audio mastering, timeline rendering, finished-film mastering, trailers, social campaigns, deterministic media editing, production documents, Kdenlive/Shotcut project export, and release packaging through a standalone file-based story-to-screen-and-release pipeline.
author: Alan Guice (Badgids)
license: Apache-2.0
compatibility: Pi Agent or another Agent Skills harness with file read/write tools. Python 3 is optional for validation scripts.
---

# Story Film

This is the general entry point for Story-Film Skills. The package is standalone.

## Start

1. Read `../../references/STANDALONE_CONTRACT.md`.
2. Read `../../references/CORE_CONTRACT.md`.
3. Read `../../references/DOCUMENT_COMPANIONS.md`.
4. Read `../../references/MODEL_SELECTION.md`.
5. Read `CATALOG.md`.
6. Match the request to exactly one playbook in `playbooks/`.
7. Read that playbook in full.
8. If no project exists, initialize one with `../../scripts/init_story_project.py` or create the same structure manually.
9. For any playbook with more than one ordered step, read `../pipeline-progress/SKILL.md`. If no active matching progress ledger exists, initialize it with `../../scripts/pipeline_progress.py init`. If one already exists, resume its current target instead of reconstructing progress from chat history.
10. Execute the playbook in order. Before each specialist step, read the named sibling `SKILL.md`.
11. After each actionable progress leaf, validate its artifact before checkpointing it complete. A blocking validation failure must remain on the same leaf and become `blocked`; it must not advance.
12. Update `00_project/state.json` after each completed artifact.
13. If an approved upstream artifact changes, run `project-impact` before rebuilding downstream work.
14. Run continuity, narrative-state, production-coverage when applicable, dramaturgy, prompt, standalone, and style checks at the gates required by the playbook.

## Routing rule

Do not invent a new workflow while a listed playbook fits. If more than one fits, choose the one whose final deliverable most closely matches the user request.

## Small-model rule

Work one artifact at a time. Save it. Validate it. Checkpoint the corresponding pipeline leaf. Then continue. For long work, process one chapter, scene, sequence, or stale dependency slice at a time. After restart or compaction, read `00_project/pipeline_progress.json` and `00_project/HANDOFF.md` before opening unrelated context.

## Standalone rule

Never stop required creative or preproduction work because another skill pack is missing. Create the native portable artifact defined by this suite. ComfyUI is optional for planning and packaging. When the user asks to operate or generate through an available ComfyUI server, route through the native `comfyui` capability rather than assuming another agent extension is installed.

## Creative planning routing

If the user wants to pressure-test an idea, resolve creative ambiguity, turn existing discussion into a durable production specification, split a large production into executable work units, or chart a project whose route is not yet clear, route through `playbooks/creative-planning-and-execution.md`. Facts that can be discovered from files or tools are agent work; creative decisions remain the user's unless explicitly delegated.


## Generation model and resource selection

Before creating model-specific prompts or ComfyUI workflows, read `../generation-model-setup/SKILL.md`. Poll the active ComfyUI model inventory and show the user the available choices for every production process that applies. Record the adapter/model family and exact concrete resources in `00_project/model_preferences.json`. Do not infer VAEs, text encoders, LoRAs, checkpoints, audio models, upscalers, or other installed resources from adapter names or installed file order. MiniMax H3 remains the default video adapter only when the user did not choose a video adapter.

## Resource-safe local generation routing

If the local LLM and ComfyUI cannot safely coexist in RAM or VRAM, route generation through `playbooks/resource-safe-comfyui.md`. All prompts, workflows, uploads, parameters, dependencies, output destinations, and validation decisions must be finalized before the local LLM is unloaded. While the LLM is unavailable, only the deterministic batch runner and Pi progress extension may advance or report generation state.

## Rich-document companion rule

Every PDF, DOCX, DOTX, XLSX, XLSM, XLTX, PPTX, PPTM, ODT, ODS, or ODP created by this suite must have a meaningful Markdown file with the same basename beside it. A pointer-only Markdown file does not satisfy the rule.

## Deterministic media editing routing

If the request is about FFmpeg, FFprobe, MLT/melt, ImageMagick, Kdenlive project export, Shotcut project export, or deterministic media manipulation, route through `playbooks/media-editing-and-project-export.md`. Discover the installed runtime before using optional codecs, filters, delegates, devices, MLT services, or hardware features.

## ComfyUI execution routing

If the requested final deliverable is an actual ComfyUI inspection, workflow run, generated asset, queue action, or ComfyUI repair, choose the matching ComfyUI playbook. Live ComfyUI facts must be discovered at runtime.

## User control

If the user names a specific artifact or model, route directly to the corresponding specialist inside the chosen playbook when the supplied upstream inputs are sufficient.
