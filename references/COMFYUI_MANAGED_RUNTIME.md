# Story-Film Managed Official Comfy Runtime

Story-Film Skills treats ComfyUI itself and the user's model collection as user-owned prerequisites for local AI generation. The official control applications are Story-Film-managed external runtimes.

## What Story-Film installs

On the first `story_comfy` operation, `scripts/comfy_official_runtime.py` creates a private Python virtual environment in the user's cache directory and installs only:

- `comfy-cli>=1.14.0`
- `comfy-mcp`
- `comfy-api-proxy`

These packages are installed from their normal Python distributions and keep their upstream licenses. Their source is not copied into the Apache-2.0 Story-Film repository.

Story-Film's bootstrap does not run the CLI command that creates a ComfyUI workspace. It does not download ComfyUI, models, or custom nodes.

`STORY_FILM_COMFY_RUNTIME_DIR` can override the managed-runtime directory. Story-Film never writes a personal machine path into the repository.

## Pi control surface

The Pi package loads `extensions/story-film-comfy/index.ts`. That extension registers the LLM-callable `story_comfy` tool directly with Pi. A separately configured generic MCP extension is not required.

The tool starts the managed `comfy-mcp` process over stdio and points it at the ComfyUI URL declared by the current Story-Film project's `00_project/resource_policy.json`. `comfy-mcp` uses the managed `comfy-cli` executable through `COMFY_BIN`.

Normal sequence:

1. `story_comfy` with `action=server-info`
2. `action=search-tools` when the exact MCP verb is not already known
3. `action=call` for live node, model, template, workflow, job, output, lifecycle, or asset operations
4. preserve Story-Film project state and workflow validation gates around those runtime operations

Third-party node installs, broad ComfyUI changes, model downloads, version switching, and paid partner execution remain approval-gated. Automatic control-runtime bootstrap is not one of those mutations because it installs only Story-Film's own external control dependencies.

## API v2 proxy

The same managed environment contains `comfy-api-proxy`. Story-Film starts it only when an API-v2 operation needs it. The managed start path binds it to loopback and points it at the project's existing ComfyUI URL.

The `story_comfy` actions `proxy-status`, `proxy-start`, `proxy-stop`, and `v2-request` provide the Pi-facing control path. Story-Film does not enable proxy model-directory placement during automatic startup.

## Fallbacks

The managed official stack is the preferred interactive Pi control surface. Story-Film's bundled native HTTP controller remains available for deterministic validation, offline batches, recovery, and environments where Python package installation is impossible. A missing generic Pi MCP server is not a reason to switch to ad hoc `curl`, `urllib`, or guessed workflow code.
