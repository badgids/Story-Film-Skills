---
name: shot-design
description: Design motivated shots from a screenplay scene and director book, giving every shot a purpose, framing, camera behavior, action, continuity state, duration, and sound plan.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Shot Design

## Workflow

1. Read core contract, dramaturgy rules, film grammar, prompt packet schema, screenplay scene, line manifest, breakdown, director book, continuity, production capabilities when present, performance blocking when present, and approved reference manifest.
2. Assign stable `SHOT-###` IDs within the project sequence.
3. Design the minimum coverage needed for the intended cut.
4. Write one model-neutral JSON object per shot to `04_generation/shot_briefs.jsonl`.
5. Each shot must include `line_ids` for the source production units it covers when a line manifest exists, plus purpose, dramatic job, beat, scene ID, duration, subjects, location, continuity, framing, composition, camera, movement reason, eye trace, action, environmental pressure, micro-action, anchor, lighting, dialogue, ambience, music, SFX, references, cut intent, and constraints.
6. Add optional `frame_regions` only when multi-subject screen placement needs explicit control or the downstream route supports regional conditioning. Use semantic zones unless normalized bounds were deliberately planned.
7. Check screen direction, eyelines, eye trace, and geography across adjacent shots.
8. If the requested camera/action combination is unavailable or conditional in `production_capabilities.json`, redesign, split, or mark the blocker rather than pretending it is executable.
9. Delete shots that do not change a relationship or emotion, advance action or information, increase pressure, or satisfy an explicit practical coverage need.

## Done

Every shot earns its place in the edit and can be generated independently from its saved brief.
