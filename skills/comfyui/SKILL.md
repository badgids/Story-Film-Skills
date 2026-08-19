---
name: comfyui
description: Understand and operate ComfyUI for story-film production using live runtime discovery, workflow validation, generation execution, queue and history control, input and output handling, official comfy-cli integration, optional MCP and API v2 surfaces, and safe troubleshooting without assuming any other skill pack is installed.
author: Alan Guice (Badgids)
license: Apache-2.0
compatibility: Python 3 for bundled native API scripts. comfy-cli, comfy-mcp, and comfy-api-proxy are optional.
---

# ComfyUI

This is the ComfyUI router for Story-Film Skills.

## Start

1. Read `../../references/COMFYUI_OPERATIONS.md`.
2. Read `../../references/COMFYUI_SECURITY.md`.
3. Identify the requested control surface and scope.
4. Read only the specialist skill needed next.

## Route

- inspect server, nodes, models, features, or resources: `comfyui-discover`
- inspect, validate, edit, or prepare workflow JSON: `comfyui-workflow`
- submit, wait, queue, cancel, free memory, or collect a run: `comfyui-run`
- upload inputs or download generated outputs: `comfyui-assets`
- install, locate, launch, stop, run, or manage through official comfy-cli: `comfyui-cli`
- use an already exposed comfy-mcp tool surface: `comfyui-mcp`
- use comfy-api-proxy or another Comfy API v2 endpoint: `comfyui-api-v2`
- diagnose missing nodes, models, invalid prompts, execution failures, or VRAM problems: `comfyui-troubleshoot`
- compile and run a deterministic multi-job generation batch that cannot call an LLM: `comfyui-offline-batch`
- hand GPU/RAM ownership from a local LLM to ComfyUI and back without model calls during generation: `resource-safe-generation`

## Rules

- Discover live capabilities before naming executable nodes, model files, or templates.
- ComfyUI-Pi-Agent is not a prerequisite for any capability in this skill.
- Do not require comfy-cli, comfy-mcp, or comfy-api-proxy for ordinary native API operation.
- Do not install software, custom nodes, or models unless the user asked for or approved that mutation.
- Do not switch local work to paid cloud or partner execution without user intent.
- Keep credentials out of workflows and project files.
- For long generations, submit asynchronously and keep the prompt ID.
