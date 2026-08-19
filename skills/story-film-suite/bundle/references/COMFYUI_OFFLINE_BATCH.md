# ComfyUI Offline Batch Contract

Default path: `04_generation/comfyui/offline_batch.json`.

Stable IDs:

- `BATCH-###`: one complete handoff batch
- `JOB-###`: one deterministic generation job
- `UP-###`: one deterministic input upload identity

Minimum shape:

```json
{
  "schema_version": 1,
  "batch_id": "BATCH-001",
  "status": "prepared",
  "sequential": true,
  "uploads": [],
  "jobs": [
    {
      "job_id": "JOB-001",
      "source_ids": ["SHOT-001"],
      "workflow": "04_generation/comfyui/workflows/SHOT-001.api.json",
      "patches": [],
      "blocked_by": [],
      "output_dir": "04_generation/comfyui/outputs/SHOT-001",
      "timeout_s": 1800,
      "max_transient_retries": 1,
      "expected_output_kinds": ["video"]
    }
  ]
}
```

Upload record:

```json
{
  "upload_id": "UP-001",
  "path": "03_preproduction/references/character/REF-001.png",
  "subfolder": "story-film/BATCH-001",
  "overwrite": false
}
```

Patch record:

```json
{
  "node": "17",
  "input": "image",
  "upload_id": "UP-001"
}
```

A patch may instead contain a literal `value` when the exact workflow input is fully decided before handoff.

## Offline completeness gate

The batch is not ready if it contains:

- UI-format workflows
- unresolved template variables or TODO placeholders
- missing project inputs
- missing dependency IDs
- circular dependencies
- workflow/node/model blockers discovered by live preflight
- a request for the runner to choose a creative alternative
- a paid route whose consent is unresolved

## Model-free runner

The runner performs deterministic upload, patch, submit, poll, download, record, retry, and memory-release operations only. Every result remains traceable to the original `JOB-###`, workflow, prompt ID, and source IDs.
