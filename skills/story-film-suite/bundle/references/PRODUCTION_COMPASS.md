# Production Compass

Use a Production Compass when the destination is too large or uncertain to plan completely in one context.

Artifacts:

- `00_project/decision_map.json`
- `00_project/decision_map.md`

The map is an index of decisions, not a duplicate store of all detail.

## Core fields

- destination
- standing notes and constraints
- decisions so far, each linked by `DEC-###`
- open decision nodes
- not-yet-specifiable areas
- out-of-scope areas
- ready frontier

## Fog rule

Create an open decision when its question can be stated precisely now. Keep it in `not_yet_specified` when the decision cannot yet be phrased without guessing what an earlier decision will reveal.

## One decision focus

A normal working session resolves one decision node, updates the map, then stops or hands off. Independent factual research may be parallelized when the runtime permits it.

The map is finished when the destination is clear enough to synthesize a production spec and no unresolved in-scope decision remains.
