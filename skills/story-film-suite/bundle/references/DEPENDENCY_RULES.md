# Dependency and Invalidation Rules

A long project must be repairable without rebuilding everything.

## Principle

Artifacts form a directed dependency graph. When an upstream artifact changes, mark only reachable downstream artifacts stale.

Examples:

- changing a logline can affect the whole story and screenplay
- changing one screenplay scene should invalidate that scene's breakdown, shots, boards, prompts, and edit entries, not unrelated scenes
- changing a character identity master can invalidate every prompt that uses that reference while leaving unrelated locations intact
- changing one dialogue line invalidates its voice cue and affected video prompt, not the score for another sequence
- changing an approved picture source invalidates only the editor placements, masters, trailers, and social deliverables that actually use that source
- changing a runtime capability snapshot does not by itself invalidate creative intent, but it can invalidate a tool operation or editor export that depended on a now-missing codec, filter, delegate, or MLT service

## Dependency record

`00_project/dependencies.json` stores artifact keys, paths, scope, and `depends_on` edges.

Use scope when possible:

- `global`
- `CH-###`
- `SCN-###`
- `LINE-###`
- `SHOT-###`
- `CHAR-###`
- `LOC-###`
- `REF-###`
- `TAKE-###`
- `MEDIA-###`
- `AUD-###`
- `EVT-###`
- `MASTER-###`
- `TRL-###`
- `CAMP-###`
- `SOC-###`
- `COPY-###`
- `DELIV-###`
- `TOOL-###`
- `CLIP-###`
- `EDIT-###`

## Invalidation

Before rebuilding:

1. identify the changed artifact or stable ID
2. traverse downstream dependencies
3. mark affected outputs stale
4. preserve unaffected approved outputs
5. rebuild the smallest valid set
6. rerun continuity checks at the boundary between rebuilt and preserved material

## Hash snapshots

`00_project/artifact_hashes.json` may store SHA-256 snapshots for registered paths. A changed hash is evidence that the file changed, not proof that every downstream artifact is wrong. Use the dependency graph to calculate impact.

## Checkpoints

After a sequence, chapter, or other bounded batch is approved, snapshot hashes and state. A future agent can resume from the last approved boundary without reconstructing chat history.

## Completion

A revision is complete only when all affected downstream artifacts are either:

- rebuilt and validated
- explicitly deferred as stale
- intentionally retired
