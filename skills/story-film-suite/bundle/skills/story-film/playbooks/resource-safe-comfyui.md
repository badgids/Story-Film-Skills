# Playbook: Resource-Safe Local ComfyUI Generation


> Workflow preflight gate: complete all required ComfyUI workflow selections before step 1. This playbook must never unload the LLM while a workflow choice or other semantic generation decision is unresolved.

Use when Pi's local LLM and ComfyUI generation models share a machine and may not fit in RAM/VRAM at the same time.

## Steps

1. Read `resource-safe-generation`, `comfyui-offline-batch`, `generation-pack`, `comfyui-handoff`, and `generation-workflow-setup`. Finish every prompt, reference, **workflow selection**, seed, dimension, duration, input mapping, source ID, expected output kind, and generation dependency while the LLM is still loaded.
2. Materialize each selected workflow into the project. Read `comfyui-discover` and `comfyui-workflow`. Probe the live server and validate every final API-format workflow against installed nodes, models, and required inputs. Do not alter a workflow's model stack just to make validation pass.
3. Create `04_generation/comfyui/offline_batch.json`. Read `generation-budget`, declare the real machine limits in `04_generation/generation_resources.json`, and build a memory-aware schedule before arming a large batch. Include every required upload and exact workflow patch so no model reasoning is needed after handoff.
4. Run `scripts/comfyui_batch.py validate <project> --live`. Resolve every blocker now. An unresolved workflow choice, TODO, missing workflow, missing node/model, circular dependency, or missing input makes the batch unsafe to arm.
5. Configure `00_project/resource_policy.json`. For a local Pi model, prefer the native `auto`, `llama-server`, or `ollama` adapter and record Pi's active local endpoint. Read `llm-model-lifecycle`. Do not generate lifecycle scripts. Use legacy `command` only for an unsupported local runtime. If Pi's model is truly external, declare `external`.
6. Run `scripts/resource_handoff.py arm <project>`. The detached runner enters the waiting-for-agent-end phase and does not unload the model during the active response.
7. Finish the current Pi response. The Story-Film Pi extension writes the release signal from its deterministic `agent_end` hook. If the extension is unavailable, use `scripts/resource_handoff.py release <project>` only after the current model turn is finished.
8. While the LLM is absent, let the model-free runner upload inputs, patch prepared values, execute one ComfyUI job at a time, poll history, download outputs, write status/events, and update the Pi runtime display. User input is intercepted by the extension and answered with deterministic progress instead of invoking the unavailable model.
9. After the batch finishes or fails, the runner drains the queue where possible and requests ComfyUI `/free` with model unload and memory release, then reloads the configured local LLM and waits for its health gate.
10. Read `00_project/RESOURCE_RESUME.md` on the next LLM turn. If the batch stopped after partial success, read `batch-recovery` and create a minimal recovery batch. Continue normal QC/selection for successful outputs, or repair only the failed prepared job if semantic changes are required.

## Done

The full requested ComfyUI scope completed without any LLM call during the generation phase, or the runner restored local-model availability and returned a concrete blocker for the next model turn.
