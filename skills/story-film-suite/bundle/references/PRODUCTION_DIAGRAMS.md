# Production Diagram Rules

Use a diagram only when spatial, temporal, relational, or dependency structure is clearer visually than in prose.

Story-Film Skills creates its own diagram specification. No external diagram skill is required.

## Useful film diagrams

- character relationship map
- story or sequence timeline
- scene geography map
- blocking map
- eyeline and axis map
- shot flow or coverage map
- production dependency graph
- reference inheritance map
- post-production cue flow

## Required outputs

For each diagram, write:

1. a semantic JSON file containing nodes, relationships, focal items, uncertainty, and the question being answered
2. a Markdown companion containing either a compact Mermaid representation or a labeled textual spatial map

Use SVG only when the current agent can create it reliably and the user needs a rendered diagram.

## One question per diagram

A diagram answers one main production question. Split diagrams that mix unrelated concerns.

## Complexity budget

- Prefer 4 to 9 meaningful nodes.
- Above 9 nodes, consider overview plus detail.
- Remove relationships already obvious from layout.
- Highlight only the elements that matter to the current decision.
- Delete any node or connector that does not change the reader's understanding.

## Film-specific requirements

### Scene geography

Show only elements that affect blocking, eyelines, screen direction, entrances, exits, threat, objective, camera placement, or continuity.

### Blocking

Use stable character IDs. Show start position, important movement, and end position. Do not imply exact distances unless the project knows them.

### Shot flow

Link `SHOT-###` IDs in editorial order. Annotate cut intent, eye-trace handoff, or audio bridge only when relevant.

### Relationship map

Label dramatic relationships such as protects, suspects, owes, controls, resents, or seeks approval from.

### Dependency graph

Use artifact keys and stable IDs. Its job is impact analysis, not decoration.

## Spatial honesty

Mermaid and auto-layout diagrams are not floor plans. For scene geography or blocking, use a labeled coordinate or zone map when auto-layout could imply false geometry.
