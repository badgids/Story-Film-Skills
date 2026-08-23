---
name: llm-model-lifecycle
description: Deterministically snapshot, unload, verify, and restore models on a local llama.cpp llama-server router or Ollama server during resource-safe ComfyUI generation without asking the LLM to invent lifecycle scripts.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# LLM Model Lifecycle

Use this skill when Story-Film must release local LLM memory for ComfyUI and later restore the model state that existed before the handoff.

## Read

Read `../../references/RESOURCE_SAFE_GENERATION.md`.

## Required behavior

1. Use the endpoint already reported by Pi, the project resource policy, or a trusted runtime source.
2. Prove that the endpoint is local with `scripts/llm_runtime.py` or the lifecycle helper's local-only guard.
3. Use `scripts/llm_model_lifecycle.py`. Never author an ad hoc curl, jq, shell loop, or one-off Python lifecycle script.
4. Prefer the `auto` adapter when the endpoint may be either a llama.cpp router or Ollama. Explicit `llama-server` and `ollama` adapters are also supported.
5. Before unloading, snapshot the exact set of resident models to `00_project/llm_model_snapshot.json`.
6. Unload through the server's native model API and verify that the models are actually absent from memory.
7. During restore, remove untracked temporary models that appeared while ComfyUI was running, then restore the original snapshot exactly.
8. Verify the restored model set before returning control to normal Story-Film work.
9. Do not kill or restart the whole model server merely to free model memory when its native model lifecycle API is available.
10. Keep the legacy `command` resource-handoff adapter only for installations whose server does not expose a supported native model lifecycle API.

## llama.cpp router mode

Use the router model API:

```text
GET  /models
POST /models/unload   {"model": "<id>"}
POST /models/load     {"model": "<id>"}
```

Poll the model list and status after every load or unload. Do not assume that a successful HTTP response means memory has already reached the requested state.

## Ollama

Use:

```text
GET  /api/ps
POST /api/generate
```

For unload, send an empty generation request with `keep_alive` set to `0`. For restore, send an empty generation request with the configured restore keep-alive value. Verify both operations through `/api/ps`.

## Commands

Inspect the currently resident model set:

```bash
python scripts/llm_model_lifecycle.py list --runtime auto --endpoint <local-endpoint>
```

Snapshot and unload:

```bash
python scripts/llm_model_lifecycle.py snapshot-unload --runtime auto --endpoint <local-endpoint> --state 00_project/llm_model_snapshot.json
```

Restore the snapshot:

```bash
python scripts/llm_model_lifecycle.py restore --state 00_project/llm_model_snapshot.json
```

The resource-safe handoff calls these operations directly. The agent must not replace them with generated scripts.

## Done

Done when the original local model set is restored and verified, or when a deterministic lifecycle error is recorded for the next model turn.
