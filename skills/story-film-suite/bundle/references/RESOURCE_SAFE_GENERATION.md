# Resource-Safe Local Generation

## Goal

Allow Pi to use a locally hosted LLM and ComfyUI on the same resource-constrained machine even when both models cannot fit in memory concurrently.

## State files

- `00_project/resource_policy.json`: user/runtime lifecycle configuration
- `00_project/resource_handoff.json`: authoritative current handoff state
- `00_project/resource_events.jsonl`: append-only runtime events
- `00_project/resource_handoff.release`: one-shot signal that the current agent turn has ended
- `00_project/RESOURCE_RESUME.md`: human-readable result for the next LLM turn
- `04_generation/comfyui/offline_batch.json`: complete model-free generation plan

## Phases

`idle -> armed -> waiting-for-agent-end -> unloading-llm -> running-comfyui -> unloading-comfyui -> reloading-llm -> complete`

Failures enter `failed`, but the runner must still attempt to unload ComfyUI models and restore the configured local LLM before it exits.


## Runtime location must be proven

Do not infer that Pi uses a remote or cloud LLM from the API format, provider name, or missing environment variables. A local `llama-server` can expose an OpenAI-compatible HTTP API.

Use direct evidence in this order:

1. Use an endpoint reported by Pi or explicitly configured by the user.
2. Run `python scripts/llm_runtime.py --endpoint <base-url>`.
3. Treat `localhost`, `127.0.0.0/8`, `::1`, Unix-domain sockets, and an address that matches a local network interface as local.
4. Treat any other endpoint as `unknown` unless the user or a trusted runtime source proves that it is external.
5. Never use `external` only because an endpoint speaks the OpenAI API.

Example:

```bash
python scripts/llm_runtime.py --endpoint http://127.0.0.1:8080
```

That endpoint is local to the same machine. If it is the endpoint used by Pi, Story-Film must plan for its RAM/VRAM use and must not select the external no-op lifecycle mode.

`local_llm.adapter: external` is allowed only when `runtime_location` is `external` and `location_evidence` records why that conclusion is trusted. A local or unknown endpoint must not be converted to external merely to bypass lifecycle configuration.

## Local LLM lifecycle adapter

Do not assume how the user's local model server is managed. The default policy is `unconfigured` and exclusive generation must refuse to start until the user chooses one of:

- `command`: explicit argv arrays for unload and reload, plus either a health URL or health command
- `external`: the Pi model is proven to run outside this machine and `location_evidence` records that proof

Commands are executed without a shell. Do not store secrets in argv or project files.

Example shape only, with values supplied for the user's installation:

```json
{
  "adapter": "command",
  "unload_command": ["service-manager", "stop", "local-llm"],
  "reload_command": ["service-manager", "start", "local-llm"],
  "health_command": ["local-health-check"],
  "health_url": ""
}
```

## Pi behavior while the LLM is absent

The Pi extension uses timers and filesystem reads only. It may:

- update the Todo/status widget
- show current resource phase
- show ComfyUI job N of total
- display deterministic warnings/errors from the runner
- notify when the LLM has been restored

It must not submit a model turn, synthesize commentary, or append generated prose to the conversation while the local LLM is unloaded.

## ComfyUI memory release

After the queue is finished, request native `POST /free` with both `unload_models` and `free_memory` true. This requests model unload/cache release inside ComfyUI. It does not free memory owned by unrelated processes.
