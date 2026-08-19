# Generation Budgeting and Memory Scheduling

[Resource-safe generation](RESOURCE_SAFE_GENERATION.md) | [Feature-scale contract](FEATURE_SCALE_PRODUCTION.md) | [Documentation home](../docs/README.md)

Large local generation jobs can compete for RAM and VRAM. Define the machine limits in `04_generation/generation_resources.json` before a large batch.

The scheduler reads the prepared ComfyUI batch and creates `04_generation/generation_schedule.json` and `.md`.

It does three things:

1. It rejects a declared resource profile that exceeds the usable machine limit.
2. It respects `blocked_by` job dependencies.
3. It prefers ready jobs that use the same resident model group so the system can reduce model swaps.

Run:

```bash
python scripts/generation_scheduler.py PROJECT --strict
```

The time values are estimates. They are a planning budget, not a promise.
