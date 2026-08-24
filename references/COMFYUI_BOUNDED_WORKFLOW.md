# Bounded ComfyUI Workflow Pipeline

Story-Film separates workflow authorship from workflow orchestration.

The LLM may inspect preserved workflow sources and live installed-node schemas, then adapt or author exactly one canonical API-format ComfyUI workflow. It does not fan that graph out across shots and it does not manage the offline generation batch.

Use the Pi-native `story_comfy_workflow` tool:

1. `prepare` searches only Story-Film's `comfyui_workflows/` library (built-ins plus `custom/<task>/<model>/`). It never scans project workflow folders, ComfyUI userdata, external paths, or template catalogs. It refreshes the live model inventory, captures the live node schemas, preserves matching extension sources, and writes a build contract.
2. The LLM may use only live installed class types and live model choices while constructing one canonical graph. It may use `story_comfy` `node-search`, `node-info`, and `node-path` while doing that design work.
3. The canonical graph uses `__STORY_FILM_PROMPT__` in its positive-prompt string input. It may use `__STORY_FILM_NEGATIVE_PROMPT__` and `__STORY_FILM_FILENAME_PREFIX__` when the installed graph exposes those inputs.
4. `finalize` live-validates the canonical graph before touching runnable workflows. Unknown classes, missing required inputs, invalid live model choices, invalid output indexes, and incompatible links fail the operation.
5. After validation, deterministic code resolves the current generation records. An existing `offline_batch.json` is preferred when recovering an interrupted production so Story-Film preserves source IDs, job IDs, dependencies, output directories, timeouts, and retry policy.
6. Per-shot prompt text comes from existing approved Story-Film prompt artifacts under `04_generation/prompts/<adapter>/<source-id>.md` when available. Only when no prepared prompt exists may deterministic brief fields be used as a fallback.
7. The script expands the canonical graph into per-shot runnable workflows, quarantines overwritten workflows, validates the complete rebuilt offline batch against the live ComfyUI server, writes the batch, and arms the existing model-free resource handoff.
8. When finalization returns `waiting-for-agent-end`, the LLM stops backend work. The existing Story-Film agent-end hook releases the armed handoff so generation can continue after the local LLM unloads.

## Custom-node boundary

Building a workflow means composing JSON from nodes already installed in the running ComfyUI instance. The bounded pipeline never creates, installs, updates, or writes code for custom nodes. Custom-node development is a separate user-requested task.

## Failure behavior

A validation failure leaves runnable workflows untouched. If valid replacements are ready, existing runnable workflows are copied into a timestamped recovery quarantine before replacement. If resource-handoff arming fails, Story-Film reports that deterministic blocker and does not ask the LLM to work around it with shell commands.
