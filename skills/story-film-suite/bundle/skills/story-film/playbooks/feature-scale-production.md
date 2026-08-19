# Feature-Scale Production

Use this playbook for a long film that can exceed one agent context or one generation session.

1. Read `sequence-production`. Build or validate `00_project/sequence_manifest.json`. Put each active screenplay scene in exactly one `SEQ-###`.
2. Read `context-shards`. Build sequence shards. Use the current sequence shard as the normal context entry point.
3. Read `production-health`. Write a health report before a long production session and after a major gate.
4. Read `long-range-continuity`. Create `CONT-###` anchors for facts that must survive across distant sequences. Record observations as those sequences are produced.
5. For each sequence, run the normal production planning, coverage, generation, QC, and take-selection steps. Keep the sequence status current.
6. Before a large local ComfyUI batch, read `generation-budget`. Declare real machine RAM/VRAM limits and build the generation schedule. If the local LLM and ComfyUI cannot coexist, continue through `resource-safe-comfyui`.
7. Read `reboot-recovery`. Create a checkpoint before a long generation run, before a planned reboot, and after an approved sequence boundary.
8. If a generation batch fails after some work is complete, read `batch-recovery`. Preserve completed jobs and rebuild only the failed, unfinished, or invalidated downstream frontier.
9. As sequences enter the edit, read `editorial-reconciliation`. Reconcile selected shots, sequence order, duplicates, missing placements, and per-sequence duration.
10. Run a global long-range continuity report after all production sequences are assembled.
11. Run `film-completeness` after the final master, delivery QC, and release state exist. Do not call the film complete while that audit has blockers.

Done when each sequence is traceable and independently recoverable, the global continuity/editorial gates pass, and the final completeness audit can prove the requested endpoint without loading the whole feature into one agent context.
