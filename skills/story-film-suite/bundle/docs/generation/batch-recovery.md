# Recover a Partial Generation Batch

[Documentation home](../README.md) | [Up: ComfyUI generation](comfyui.md) | [Next: Reboot recovery](../operations/recovery.md)

## Table of contents

- [Goal](#goal)
- [What is preserved](#what-is-preserved)
- [Build a recovery batch](#build-a-recovery-batch)
- [Dependencies](#dependencies)

## Goal

Do not regenerate successful work because one job failed.

## What is preserved

Completed `JOB-###` records stay complete.

A recovery batch contains:

- failed jobs that need retry;
- pending jobs that never ran;
- downstream jobs that depend on a retried result.

It does not include an already completed independent job.

## Build a recovery batch

Run:

```bash
python scripts/batch_recovery.py PROJECT build
```

Outputs:

```text
04_generation/comfyui/recovery_batch.json
04_generation/comfyui/recovery_batch.md
```

Review the recovery batch before you arm it.

## Dependencies

The recovery tool rewrites blocking edges to the jobs that are inside the recovery set. It keeps the original work identity.

If the failure needs a new prompt or a creative decision, restore the LLM and repair the source job first.

## Related pages

- [ComfyUI generation](comfyui.md)
- [Resource-safe generation](resource-safe.md)
- [Production health](../production/health.md)
