# Hierarchical Production Planning

Story-Film Skills refines film intent through explicit layers. Each layer adds production detail without silently rewriting the layer above it.

## Planning chain

```text
story or source
  -> screenplay
  -> scene manifest
  -> line manifest
  -> director book and breakdown
  -> production capabilities
  -> performance blocking
  -> shot briefs and previz
  -> shooting script
  -> generation briefs
  -> candidate takes
  -> media QC and take selection
  -> edit
```

## Refinement rule

A downstream layer may:

- split an upstream unit into smaller units
- add staging, camera, sound, timing, or generation detail
- record reversible assumptions
- record a concise decision reason

A downstream layer may not:

- change canon
- alter exact dialogue without updating the screenplay and line manifest
- invent unavailable production capabilities and present them as available
- delete an upstream story event because it is difficult to generate

## Traceability fields

When the artifact schema supports them, use:

- `source_ids`: upstream IDs refined by this record
- `decision_reason`: concise reason for the chosen split, staging, or setup
- `assumptions`: reversible unknowns introduced at this layer
- `constraints`: verified production restrictions

Do not save private chain-of-thought. Save only decision-relevant rationale that a future agent needs to audit or continue the work.

## Coverage principle

Long-form production fails when a planning layer silently drops material. Scene and line coverage must therefore be checkable from files. Use `production-coverage` before declaring a screenplay scope generation-ready.
