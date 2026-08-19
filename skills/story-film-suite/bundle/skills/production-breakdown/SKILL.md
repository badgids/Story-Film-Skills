---
name: production-breakdown
description: "Break screenplay scenes into production needs: cast, extras, locations, props, wardrobe, makeup, vehicles, practical effects, VFX, sound, music, special continuity, and generation dependencies."
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Production Breakdown

## Workflow

1. Read core contract, screenplay, scene manifest, canon, continuity bible, and reference manifest when present.
2. Create one file per scene under `03_preproduction/scene_breakdowns/SCN-###.md`.
3. Record scene purpose and all elements needed to stage or generate it.
4. Separate visible requirements from implied off-screen requirements.
5. Record continuity state at scene start and end.
6. Record any generation dependency such as approved reference ID, missing character or location sheet, first frame, last frame, voice identity, music cue, VFX plate, or previz requirement.

## Done

A director or generation agent can identify every required element for the scene without rereading the entire screenplay.
