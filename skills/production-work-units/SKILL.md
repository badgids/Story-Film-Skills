---
name: production-work-units
description: Break a Story-Film specification or large production plan into bounded complete work units with explicit blockers, acceptance criteria, and validation gates.
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Production Work Units

Read `../../references/PRODUCTION_WORK_UNITS.md`.

1. Start from the approved creative-production spec or current project plan.
2. Prefer complete creative/production slices, not one horizontal unit per document type or department.
3. Give every unit a `UNIT-###` ID and explicit blocker edges.
4. Make each unit independently reviewable or verifiable.
5. Include concrete acceptance criteria and the validator/QC/human gate that proves them.
6. Write both `00_project/work_units.json` and `00_project/work_units.md`.
7. Use `scripts/work_units.py validate` and `frontier` before execution.
8. Do not silently start blocked units.

Use the Pi pipeline Todo for execution progress. Work units describe production dependency; the Todo describes the currently running process.
