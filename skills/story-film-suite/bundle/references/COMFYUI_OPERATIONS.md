# ComfyUI Operations Contract

Story-Film Skills can inspect and operate ComfyUI directly. ComfyUI-Pi-Agent, comfy-mcp, comfy-cli, and comfy-api-proxy are optional interfaces, not runtime requirements.

## Core rule

Discover the live installation before choosing nodes, models, templates, or workflow inputs. Never assume a class name, model filename, custom-node pack, widget index, filesystem path, or template is present because it existed in documentation or on another machine.

## Preferred control surfaces

Use the smallest surface that fits the task.

1. Native ComfyUI HTTP API for inspection, API-format workflow validation, input upload, queueing, polling, cancellation, output download, and memory release.
2. `comfy-cli` when it is installed and its workspace, lifecycle, UI-workflow conversion, template, node, model, cloud, or structured command features materially help.
3. `comfy-mcp` when the current agent harness already exposes its tools. It is an optional adapter over comfy-cli, not a requirement.
4. Comfy API v2 through `comfy-api-proxy` or Comfy Cloud only when the user selected that surface or the current workflow requires the v2 contract.

Do not install any of these merely to avoid using the native API. Do not switch from local execution to paid or hosted execution without user intent.

## Runtime discovery order

For a local or explicitly supplied ComfyUI URL:

1. Probe `GET /system_stats`.
2. Read `GET /features` when available.
3. Read `GET /prompt` for queue depth.
4. When a workflow is involved, inspect `GET /object_info` or the exact classes with `GET /object_info/{node_class}`.
5. Inspect model categories with `GET /models` and exact category contents with `GET /models/{folder}` only when model availability matters.
6. Save a project-local snapshot when reproducibility matters. A snapshot is evidence from one moment, not permanent truth.

## Workflow execution order

1. Identify whether the workflow file is API format or UI format.
2. For API format, validate its node classes and required inputs against the live server before submission when practical.
3. For UI format, do not pretend it can be posted directly to `/prompt`. Use comfy-cli's supported conversion/run path when available, or ask for/export an API-format copy before using the native submit script.
4. Upload required input media before execution and update only the intended workflow input values.
5. Submit asynchronously when the generation may take meaningful time.
6. Keep the returned `prompt_id` as the durable run handle.
7. Poll `/history/{prompt_id}` as the authoritative completion record. `/ws` is useful for live progress but is not required for correctness.
8. Fetch output records from history and download them through `/view`.
9. Record generated media in project state using project-relative paths.

## Live discovery over stale instructions

Model, node, and template catalogs change. Skills should teach the method, then query the current server or official CLI at runtime. Literal model or node names belong in a project only when they came from the user, the live server, an approved workflow, or a model-specific adapter that is explicitly targeting that family.

## Custom nodes

Custom nodes execute Python code in the ComfyUI process. Missing custom nodes are a dependency problem, not permission to install arbitrary repositories.

- Identify the missing class first.
- Prefer an official registry or known package mapping when using comfy-cli.
- Explain the missing dependency to the user before installation.
- Require user approval before installing or updating third-party custom-node code.
- Restart ComfyUI after installing nodes before re-validating the workflow.
- Never invent a custom-node repository URL from a class name.

## Models

A model filename required by a workflow must be checked against the live model category or the relevant loader node schema.

- Do not fabricate model paths.
- Do not assume a downloaded model is visible to a remote ComfyUI.
- Large downloads should be explicit operations with a known destination category and user intent.
- Prefer safetensors when choosing between equivalent untrusted weight formats.
- Never place arbitrary files in `custom_nodes`, configuration directories, or executable locations through a model workflow.

## Memory and long jobs

Before a heavy generation, `system_stats` can be used to inspect free VRAM and system memory. If ComfyUI itself is holding unnecessary models, `POST /free` can request model unload and cache release. This cannot free VRAM held by another process and does not replace cancelling a running job.

## Project records

ComfyUI operation records belong under `04_generation/comfyui/`:

```text
04_generation/comfyui/
  server_snapshot.json
  run_index.jsonl
  workflows/
  templates/
  fragments/
  blueprints/
  inputs/
  runs/
  outputs/
```

A run record should store the workflow path, server URL without credentials, prompt ID, stable story-film item ID when known, submission time, final state, output records, and errors. `run_index.jsonl` is append-only so retries and rejected generations remain traceable instead of being overwritten. Never store API keys or bearer tokens.
