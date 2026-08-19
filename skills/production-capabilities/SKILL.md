---
name: production-capabilities
description: Build and maintain a project-specific registry of executable locations, blocking anchors, performer actions, camera behaviors, audio features, generation limits, and unknown production capabilities before detailed blocking or shooting plans.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Production Capabilities

## Workflow

1. Read core contract, `PRODUCTION_CAPABILITIES.md`, approved production approach, and any live discovery or tested workflow evidence.
2. Write or update `03_preproduction/production_capabilities.json`.
3. Record each relevant capability as available, unavailable, conditional, or unknown.
4. Separate installed technical components from verified creative capability.
5. For fixed sets or 3D spaces, record real location anchors and allowed actions/camera behaviors. For generative production, record model/workflow limits and risks without inventing exact geometry.
6. Mark assumptions and unknowns explicitly.
7. If the selected production route changes, run `project-impact` before reusing dependent blocking or shot decisions.

## Done

The next planning stage can tell what it may safely use, what needs a workaround, and what remains unknown without guessing from model names.
