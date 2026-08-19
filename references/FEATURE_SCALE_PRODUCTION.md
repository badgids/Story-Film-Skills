# Feature-Scale Production Contract

[Documentation home](../docs/README.md) | [Feature-scale user guide](../docs/production/feature-scale.md)

A feature film is too large to treat as one agent context.

Use `SEQ-###` as the normal production boundary. Keep global canon and locked identities above the sequence layer. Keep scene, line, shot, take, media, generation, and editorial detail inside the smallest sequence shard that can do the work.

## Required control loop

1. Build `00_project/sequence_manifest.json` after the screenplay scene manifest is stable enough to plan production.
2. Build one context shard for each sequence.
3. Work on one sequence or one explicit global gate at a time.
4. Run sequence coverage and continuity before generation.
5. Build a memory-aware generation schedule before a large local batch.
6. Create a recovery checkpoint at approved boundaries and before a risky machine transition.
7. Preserve completed generation jobs after a partial failure.
8. Reconcile each sequence into the main edit.
9. Run the final completeness audit before calling the project a completed film.

## Global gates

A global gate may read more than one sequence when the task truly needs global evidence. Examples include long-range continuity, final editorial order, whole-film audio, delivery QC, and final completeness.

Do not use a global gate as an excuse to load every detailed artifact into one LLM context. Use indexes, summaries, and sequence shards first.
