---
name: comfyui
description: Understand and operate ComfyUI for story-film production through Story-Film's managed official comfy-mcp/comfy-cli control runtime, live workflow and model discovery, deterministic validation, generation execution, API v2, offline batching, resource handoff, and safe troubleshooting.
author: Alan Guice (Badgids)
license: Apache-2.0
compatibility: Python 3.10+ for the managed official Comfy control runtime. The user supplies ComfyUI and their chosen models; Story-Film manages comfy-cli, comfy-mcp, and comfy-api-proxy separately.
---

# ComfyUI

This is the ComfyUI router for Story-Film Skills.

## Start

1. Read `../../references/COMFYUI_MANAGED_RUNTIME.md`.
2. Read `../../references/COMFYUI_OPERATIONS.md`.
3. Read `../../references/COMFYUI_SECURITY.md`.
4. Identify the requested control surface and scope.
5. Read only the specialist skill needed next.

## Route

- primary Pi live control, official MCP discovery, templates, nodes, models, lifecycle, jobs, outputs, and assets: `comfyui-mcp`
- inspect server, nodes, models, features, resources, existing workflows, or templates: `comfyui-discover`
- inspect, validate, edit, or prepare workflow JSON: `comfyui-workflow`
- submit, wait, queue, cancel, free memory, or collect a run: `comfyui-run`
- upload inputs or download generated outputs: `comfyui-assets`
- official CLI workspace and lifecycle operations behind the managed runtime: `comfyui-cli`
- managed comfy-api-proxy or another approved Comfy API v2 endpoint: `comfyui-api-v2`
- diagnose missing nodes, models, invalid prompts, execution failures, or VRAM problems: `comfyui-troubleshoot`
- compile and run a deterministic multi-job generation batch that cannot call an LLM: `comfyui-offline-batch`
- hand GPU/RAM ownership from a local LLM to ComfyUI and back without model calls during generation: `resource-safe-generation`

## Rules

- In Pi, use the native `story_comfy` tool as the primary live ComfyUI control surface. Start with `action=server-info`.
- `story_comfy` has precedence over shell/filesystem discovery for ComfyUI installation/location, live server state, installed models, model search, templates, nodes, and workflows.
- Do not use Bash, `find`, `ls`, `which`, `locate`, direct comfy-cli discovery commands, guessed personal paths, home-directory scans, model-folder scans, raw config-file inspection, or one-off HTTP clients to discover those facts.
- Before deciding a model is missing, use `action=model-inventory`, then `action=model-search` when a filtered search is needed. Before discovering workflows/templates use `action=workflow-catalog`; use `action=node-search`/`action=node-info` for nodes.
- Use `action=search-tools` only when the exact official comfy-mcp verb is unknown. An empty or failed MCP tool-name search is not permission to fall back to Bash; the native `story_comfy` inventory/catalog/node actions remain the first fallback.
- A failed guessed path, missing guessed directory, empty checkpoints directory, or empty filesystem search is never evidence that ComfyUI or a model is absent.
- Story-Film automatically bootstraps its separate official control environment. Do not ask the user to install or configure comfy-cli, comfy-mcp, comfy-api-proxy, or a generic MCP extension.
- Managed bootstrap never installs ComfyUI, models, or custom nodes. The user supplies ComfyUI and their model collection.
- Discover live capabilities before naming executable nodes, model files, or templates.
- Before creating an executable graph, catalog existing project workflows/templates, saved ComfyUI user workflows, official core templates, and installed custom-node example workflows. Reuse and minimally patch a suitable source before considering a new graph.
- A Story-Film prompt adapter name describes prompt grammar only. It never proves that a same-named ComfyUI node, API node, checkpoint, or runtime exists.
- ComfyUI-Pi-Agent and a separately configured Pi MCP server are not prerequisites.
- Third-party custom-node installation, model downloads, ComfyUI version changes, broad updates, and paid partner execution require explicit user approval.
- Keep credentials out of workflows and project files.
- For long generations, submit asynchronously and keep the prompt ID.
- The bundled native HTTP controller remains a deterministic fallback/internal path; do not replace the managed tool with ad hoc curl, urllib, requests, or raw prompt loops.
