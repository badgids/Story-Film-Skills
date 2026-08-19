# Resource-Safe Local Generation

[Documentation home](../README.md) | [Up: ComfyUI generation](comfyui.md) | [Next: RAM and VRAM budgets](memory-budget.md)

## Table of contents

- [Problem](#problem)
- [Safe handoff](#safe-handoff)
- [What must be finished first](#what-must-be-finished-first)
- [What works without the LLM](#what-works-without-the-llm)
- [Failure behavior](#failure-behavior)
- [Return to the LLM](#return-to-the-llm)

## Problem

A local language model can use much RAM and VRAM. A large ComfyUI model can also use much RAM and VRAM.

The computer can fail with an out-of-memory error if both models stay loaded.

## Safe handoff

Story-Film Skills can use this order:

1. Keep the LLM loaded while creative work is still needed.
2. Finish all prompts and workflow values.
3. Upload all declared ComfyUI inputs.
4. Patch the exact server filenames into the workflows.
5. Validate every final workflow against the live server.
6. Arm the batch.
7. End the current agent turn.
8. Unload the local LLM with the configured adapter.
9. Run the prepared ComfyUI jobs with deterministic code only.
10. Ask ComfyUI to unload models and free memory.
11. Reload the local LLM.
12. Read `00_project/RESOURCE_RESUME.md` and continue.

## What must be finished first

An armed batch cannot contain unresolved creative placeholders such as `TODO`, `TBD`, or `NEEDS-LLM`.

The local LLM lifecycle must also be configured. Story-Film Skills does not guess how your LLM server unloads a model.

## What works without the LLM

While the LLM is unloaded, deterministic code can:

- submit a prepared workflow;
- poll the ComfyUI queue;
- collect outputs;
- update `JOB-###` status;
- update the Pi Todo and resource status;
- retry a prepared job when the retry policy permits an identical retry;
- stop safely when semantic repair is needed.

These actions do not call the LLM and do not use its context window.

## Failure behavior

The no-LLM runner cannot rewrite a prompt or make an artistic choice.

If semantic repair is needed, it stops the batch. It then attempts ComfyUI cleanup and restores the local LLM. The failed job is recorded for repair.

## Return to the LLM

Read:

```text
00_project/resource_handoff.json
00_project/RESOURCE_RESUME.md
```

These files explain what completed, what failed, and what action comes next.

## Related pages

- [ComfyUI generation](comfyui.md)
- [RAM and VRAM budgets](memory-budget.md)
- [Partial batch recovery](batch-recovery.md)
- [Recover after a reboot](../operations/recovery.md)
