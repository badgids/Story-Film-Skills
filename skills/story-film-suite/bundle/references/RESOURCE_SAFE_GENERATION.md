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

## Local LLM lifecycle adapter

Do not assume how the user's local model server is managed. The default policy is `unconfigured` and exclusive generation must refuse to start until the user chooses one of:

- `command`: explicit argv arrays for unload and reload, plus either a health URL or health command
- `external`: the Pi model is remote or otherwise proven not to consume the local generation resources

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
