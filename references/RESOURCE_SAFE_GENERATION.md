# Resource-Safe Local Generation

## Goal

Allow Pi to use a locally hosted LLM and ComfyUI on the same resource-constrained machine even when both models cannot fit in memory concurrently.

## State files

- `00_project/resource_policy.json`: user/runtime lifecycle configuration
- `00_project/llm_model_snapshot.json`: exact local model set captured before native unload
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

Story-Film has native deterministic model-memory lifecycle support. The preferred adapters are:

- `auto`: probe the configured local endpoint and use llama.cpp router mode or Ollama
- `llama-server`: use the llama.cpp router model API directly
- `ollama`: use the Ollama model-residency API directly
- `command`: legacy compatibility for installations that require explicit service-manager argv arrays
- `external`: only when Pi's model is proven to run outside this machine

The agent must not author curl, jq, shell, or one-off Python lifecycle scripts. Native adapters call `scripts/llm_model_lifecycle.py`, which uses Python's HTTP client directly and verifies state after every transition.

Before unload, Story-Film snapshots the exact resident model set. During restore it first unloads untracked temporary models that appeared while ComfyUI was running, then restores the original snapshot. This matters when a ComfyUI graph itself uses an Ollama helper model.

### llama.cpp llama-server router

Story-Film uses these router endpoints:

```text
GET  /models
POST /models/unload   {"model": "<id>"}
POST /models/load     {"model": "<id>"}
```

The helper polls `/models` and verifies the model status instead of treating the POST response as proof that memory has already changed.

### Ollama

Story-Film lists resident models with `GET /api/ps`. It uses `POST /api/generate` with an empty prompt and `keep_alive: 0` to unload a model immediately. Restore uses an empty generation request with the configured `restore_keep_alive` value, then verifies `/api/ps`.

The project policy records the active local endpoint and adapter. Example native shape:

```json
{
  "adapter": "auto",
  "endpoint": "http://127.0.0.1:8080",
  "restore_keep_alive": "5m"
}
```

`command` remains supported for nonstandard local runtimes, but it is a configuration fallback, not a script-generation task for the LLM.

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
