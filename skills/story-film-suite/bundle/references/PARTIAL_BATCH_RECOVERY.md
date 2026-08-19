# Partial Batch Recovery

[ComfyUI offline batch](COMFYUI_OFFLINE_BATCH.md) | [Resource-safe generation](RESOURCE_SAFE_GENERATION.md) | [Documentation home](../docs/README.md)

A generation batch can fail after some jobs are complete. Completed upstream jobs must stay valid unless their inputs changed.

`comfyui_batch.py` writes partial result state after each completed job and writes the failed job when a batch stops.

Build a minimal retry batch with:

```bash
python scripts/batch_recovery.py PROJECT
```

The recovery batch contains:

- failed or unfinished jobs that need another run
- downstream jobs that depend on a retried job
- preserved completed jobs that do not need another run

Do not rerun an expensive completed job only because a later job failed.
