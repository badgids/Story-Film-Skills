---
name: production-executor
description: Execute one ready Story-Film production work unit from its approved specification through validation, approval, and durable progress checkpointing.
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Production Executor

Use for a `UNIT-###` that is on the ready frontier.

1. Read the work unit, its source IDs, acceptance criteria, blockers, and authoritative project artifacts.
2. Refuse to execute it if a blocker is incomplete.
3. Activate the smallest relevant Story-Film playbook and Pi Todo scope.
4. Produce the complete requested slice, not just the easiest layer.
5. Validate at natural seams while working and run the unit's final acceptance gates at the end.
6. If validation fails, keep the unit and Todo target active/blocked. Repair before advancing.
7. Mark the unit complete only after acceptance criteria pass or the declared human approval is recorded.
8. Run `project-impact` when approved upstream content changed.
9. Update `HANDOFF.md` so a fresh session can continue without chat reconstruction.
