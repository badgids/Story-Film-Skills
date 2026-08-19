# Feature-Scale Production

[Documentation home](../README.md) | [Up: Feature film](../workflows/feature-film.md) | [Next: Sequences and shards](sequences-and-shards.md)

## Table of contents

- [Goal](#goal)
- [Nine feature-scale controls](#nine-feature-scale-controls)
- [Normal work loop](#normal-work-loop)
- [Global work loop](#global-work-loop)

## Goal

The goal is simple.

Make a long film without making the LLM hold the whole film in memory.

Make every long-running process recoverable.

Make completion measurable.

## Nine feature-scale controls

v0.0.11 adds these controls:

1. `sequence-production` manages `SEQ-###` production units.
2. `context-shards` builds small per-sequence working sets.
3. `production-health` reports known blockers and warnings.
4. `long-range-continuity` checks facts across distant sequences.
5. `generation-budget` schedules local AI work against RAM and VRAM limits.
6. `reboot-recovery` stores exact durable control checkpoints.
7. `batch-recovery` preserves completed generation work after a partial failure.
8. `editorial-reconciliation` checks selected shots and sequence order in the main timeline.
9. `film-completeness` checks the final production evidence.

## Normal work loop

1. Choose the current sequence.
2. Load its context shard.
3. Perform one production step.
4. Validate the result.
5. Checkpoint the Todo leaf.
6. Update the sequence status.
7. Create a recovery checkpoint at important boundaries.

## Global work loop

Use a global gate only when the question needs global evidence.

Read summaries and indexes first.

Open detailed sequence data only for the part that needs repair.

## Related pages

- [Sequences and shards](sequences-and-shards.md)
- [Production health](health.md)
- [Continuity](continuity.md)
- [Memory budget](../generation/memory-budget.md)
- [Recovery](../operations/recovery.md)
