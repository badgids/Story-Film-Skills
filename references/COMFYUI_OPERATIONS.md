# ComfyUI Operations Contract

Story-Film Skills operates the user's existing ComfyUI through a Story-Film-managed official control stack. Story-Film installs comfy-cli, comfy-mcp, and comfy-api-proxy into a separate external Python environment on first use; their upstream licenses remain separate from Story-Film's Apache-2.0 code.

The user is expected to install ComfyUI itself and the models they want to use. Managed bootstrap never installs ComfyUI, models, or custom nodes.

## Core rule

Discover the live installation before choosing nodes, models, templates, or workflow inputs. Never assume a class name, model filename, custom-node pack, widget index, filesystem path, or template is present because it existed in documentation or on another machine.

## Preferred control surfaces

1. In Pi, use the native `story_comfy` tool. It speaks MCP stdio directly to Story-Film's managed official comfy-mcp process and exposes the live official tool catalog.
2. Keep Story-Film's workflow catalog, project-copy preservation, live validation/promotion, deterministic batch, and resource-handoff rules around executable production work.
3. Use managed comfy-cli underneath comfy-mcp for workspace, lifecycle, workflow, job, model, node, template, and asset operations.
4. Start the managed comfy-api-proxy on loopback when a workflow/application intentionally needs the Comfy API v2 contract.
5. Use Story-Film's bundled native HTTP controller as a deterministic fallback or offline implementation detail when the managed official surface cannot perform an operation.

Do not ask the user to install the control stack or configure a generic Pi MCP server. Do not replace these surfaces with ad hoc curl, urllib, requests, or raw prompt loops. Do not switch from local execution to paid or hosted execution without user intent.

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
