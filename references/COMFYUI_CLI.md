# comfy-cli Integration

`comfy-cli` is the official command-line engine underneath Story-Film's managed Comfy control runtime. Story-Film installs it into a separate managed Python environment together with comfy-mcp and comfy-api-proxy; the user does not need to install comfy-cli separately.

Story-Film's bootstrap does not invoke ComfyUI installation. It targets the ComfyUI that the user already installed and configured.

## Stable steering rule

The CLI evolves. Use stable workflow logic in skills and query the installed CLI for current argument details. Prefer JSON output for agent automation.

The official agent pattern uses global flags such as:

```text
comfy --where local --json <command> ...
```

When exact syntax is uncertain, run `comfy --help` or `comfy <command> --help` rather than guessing.

## Locating a workspace

Useful official concepts:

- `--workspace=<path>` targets a specific workspace.
- `--recent` targets the recently used workspace.
- `--here` targets the current directory's ComfyUI.
- `comfy set-default` sets the default workspace.
- `comfy which` reports the resolved target workspace.

The workspace resolution mechanism replaces hardcoded personal paths.

## Server location

`COMFY_LOCAL_URL` can point local-targeting commands at an already-running ComfyUI on a non-default address. Per-command host/port flags take precedence when supported.

Do not assume `127.0.0.1:8188` if the CLI or user has explicitly configured another target.

## Lifecycle

Official operations include:

```text
comfy launch
comfy launch --background
comfy stop
comfy env
comfy system-stats
comfy free
```

Use background launch for agent workflows that need to regain control of the shell. After launch, probe the server before submitting work.

## Workflow execution

`comfy run --workflow <file>` can run a workflow against local ComfyUI, and current comfy-cli can auto-convert UI-format workflow JSON for its run path.

For long runs, prefer asynchronous submission followed by job status/wait commands and output download rather than pinning the agent to one blocking command.

Current CLI concepts include:

```text
comfy run
comfy jobs
comfy upload
comfy download
```

Use the returned prompt ID as the handle. Do not parse human prose when `--json` output is available.

## Nodes, models, templates, and dependencies

comfy-cli can manage and inspect custom nodes and models, and its newer agent surface includes live node, template, workflow validation, and dependency capabilities.

Rules:

- discover before installing
- validate a workflow before changing dependencies
- require user approval before installing or updating third-party custom-node code
- restart ComfyUI after node installation
- revalidate after restart
- do not download a large model merely because a workflow mentions it without user intent

## Updates

Updating ComfyUI, the CLI, or all custom nodes changes the execution environment.

- Do not update as a generic troubleshooting reflex.
- Preserve or report dirty working-tree state.
- Version switching can stash changes and reinstall dependencies.
- Updating all custom nodes can run third-party installation code and requires explicit user intent.

## Local versus cloud

comfy-cli can route work to Comfy Cloud with `--where cloud`. That is not an automatic fallback for local resource limits. Cloud generation may consume credits and requires authentication.

If both local and cloud are possible, preserve the user's chosen execution location. Ask before switching a project from local to paid cloud execution.


## Current source-oriented workflow pattern

Recent official comfy-cli agent guidance distinguishes read-only discovery from state-changing execution and recommends a hierarchy:

1. curated template when one matches
2. reusable fragment plus blueprint for work expected to grow or repeat
3. raw API JSON only for a small throwaway graph

Useful discovery and source-management concepts include:

```text
comfy --json discover
comfy --json templates ls --type <image|video|audio>
comfy templates fetch <name> --out <file>
comfy --json nodes ls ...
comfy --json nodes show <NodeClass>
comfy nodes path <SOURCE_TYPE> <DEST_TYPE>
comfy --json workflow slots <workflow.json>
comfy --json workflow notes <workflow.json>
comfy workflow decompose <workflow.json> --name <fragment-name>
comfy workflow compose <blueprint.yaml>
```

Do not assume these verbs exist on an older installed CLI. If an operation fails as unsupported, report the capability gap and fall back to native ComfyUI inspection where possible.

The key engineering rule is source versus artifact: for a reusable workflow, edit fragments/blueprints and recompose rather than repeatedly modifying a compiled graph by numeric node ID.

## Live model discovery

Prefer the installed CLI's live catalog to model names copied into skill text:

```text
comfy --json models list-folders --where local
comfy --json models list-folder checkpoints --where local
comfy --json models search --text <words> --type <folder-or-type> --where local
comfy --json models show <exact-name> --where local
```

Local search walks the model folders reported by the running ComfyUI. Treat those results as current evidence for the target server.

The bundled bridge exposes the same read-only operations:

```text
python scripts/comfyui_cli_bridge.py models-list-folders
python scripts/comfyui_cli_bridge.py models-search --text <words>
python scripts/comfyui_cli_bridge.py models-show <name>
```

## Custom-node dependency repair

Custom nodes are executable third-party code. Discovery is read-only; installation and mutation require explicit user approval.

Useful official operations include:

```text
comfy node deps [pack ...]
comfy node deps-in-workflow --workflow <file> --output <deps.json>
comfy node install <registry-id ...>
comfy node reinstall <registry-id ...>
comfy node uninstall <registry-id ...>
comfy node update <registry-id ...>
comfy node fix <registry-id ...>
comfy node install-deps --workflow <file>
```

Operational sequence for a missing node:

1. Confirm the missing class from workflow validation or server `node_errors`.
2. Identify the responsible package from current CLI or registry data. Do not guess a GitHub URL from the class name.
3. Show the exact package change to the user and obtain approval.
4. Install or repair only the named package.
5. Restart ComfyUI so the running process can load the new node classes.
6. Re-read live object info and revalidate the workflow.

The bridge refuses broad `all` targets for package mutations and refuses to perform them unless `--confirm` is present. The confirmation flag is an execution interlock, not permission to infer user consent.

## Model downloads

A missing model is different from a missing node. First query the live model catalog and the loader node's current choices. Download only after the user has chosen to change the local environment.

The bridge supports an explicitly approved official CLI download:

```text
python scripts/comfyui_cli_bridge.py model-download \
  --url <public-model-url> \
  --relative-path <model-folder> \
  --background \
  --confirm
```

The bridge rejects credential-bearing URLs. Configure Hugging Face, CivitAI, Comfy, or other credentials through the provider or official CLI mechanism rather than embedding secrets in a command, workflow, project record, or URL.

Large downloads should normally use the official CLI's background mode, then the CLI's download status controls. Do not claim a model is available until the download has completed and the target ComfyUI can see it.

## Error envelope discipline

When an official CLI command fails in JSON mode, inspect its structured `error.code`, `hint`, and `details` before inventing a fix. Common principles:

- a UI-format workflow conversion error is not a missing-node error
- a server `node_errors` map is stronger evidence than an LLM guess about the graph
- a dropped local WebSocket does not prove the server-side job stopped
- cloud authentication failure before submit differs from a partner node token failure during a job
- an unsupported CLI capability should degrade to native ComfyUI inspection when possible, not trigger a blind environment update
