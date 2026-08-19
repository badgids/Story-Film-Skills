# RAM and VRAM Generation Budgets

[Documentation home](../README.md) | [Up: Resource-safe generation](resource-safe.md) | [Next: Partial batch recovery](batch-recovery.md)

## Table of contents

- [Purpose](#purpose)
- [Resource profiles](#resource-profiles)
- [Machine limits](#machine-limits)
- [Scheduling](#scheduling)
- [Important limit](#important-limit)

## Purpose

A generation plan must fit the computer before it runs.

`generation-budget` creates a deterministic schedule from prepared `JOB-###` records and resource profiles.

## Resource profiles

A profile can describe:

- expected VRAM;
- expected system RAM;
- expected duration;
- whether the GPU must be exclusive;
- a resident model group.

The default project file is:

```text
04_generation/generation_resources.json
```

The default machine capacity is intentionally unconfigured. Enter real limits for the current computer.

## Machine limits

Keep a reserve. Do not schedule to the last available byte.

If a profile exceeds the configured usable limit, scheduling fails before generation starts.

## Scheduling

The scheduler respects job dependencies first.

When more than one ready job is possible, it can prefer jobs in the same resident model group. This reduces model swaps.

Run:

```bash
python scripts/generation_scheduler.py PROJECT build
```

Outputs:

```text
04_generation/generation_schedule.json
04_generation/generation_schedule.md
```

## Important limit

A budget is an estimate. The actual runtime can use more memory than the estimate.

Use conservative values and update profiles from observed runs.

## Related pages

- [Resource-safe generation](resource-safe.md)
- [Partial batch recovery](batch-recovery.md)
- [Feature-scale production](../production/feature-scale.md)
