---
name: shooting-script
description: Compile screenplay lines, performance blocking, shot briefs, scene state, and dialogue timing into a portable machine-readable shooting script with positions, moves, actions, camera coverage, exact dialogue, and timing sources.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Shooting Script

## Workflow

1. Read core contract, `HIERARCHICAL_PRODUCTION_PLANNING.md`, `SHOOTING_SCRIPT.md`, screenplay, line manifest, blocking, shot briefs, continuity, and production capabilities.
2. Work one approved scene or sequence at a time.
3. Write `03_preproduction/shooting_script.json`. Preserve exact dialogue and stable IDs.
4. For every unit, record current positions, moves, actions, covering shot IDs, constraints, and timing source.
5. Keep movement separate from non-locomotion actions.
6. If measured voice duration exists, use it instead of an estimate where it controls shot/action/subtitle timing.
7. Never rewrite dialogue or choose a new story beat to fit a technical limit. Route the conflict upstream or split the production unit.
8. Run `production-coverage` after compiling the requested scope.

## Done

The approved scope can be executed or translated into generation tasks without reconstructing performer state, dialogue, camera coverage, or timing from chat.
