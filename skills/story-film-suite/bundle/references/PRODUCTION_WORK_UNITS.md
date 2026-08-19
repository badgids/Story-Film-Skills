# Production Work Units

Work units convert a large creative-production specification into bounded, verifiable pieces of work.

Artifacts:

- `00_project/work_units.json`
- `00_project/work_units.md`

Stable ID: `UNIT-###`.

## Slice rule

Prefer a narrow complete slice that produces a reviewable result across every layer it needs instead of horizontal batches that leave unusable partial work.

Examples:

- one story sequence from outline through continuity review
- one scene from screenplay line IDs through blocking and shot coverage
- one hero character reference package through approval
- one trailer cut from source selection through mastered deliverable
- one social deliverable from source lineage through final QC

Global foundation work is allowed when later slices cannot remain coherent without it, such as locking the story premise, creating a visual bible, or defining a voice identity.

## Record

Each work unit should contain:

- `unit_id`
- `title`
- `delivers`
- `blocked_by`
- `source_ids`
- `acceptance_criteria`
- `validation_commands` or named validation gates
- `status`: `ready`, `blocked`, `active`, `complete`, `failed`, `deferred`
- `notes`

Each unit should be small enough for one fresh agent context when practical. The ready frontier is every non-complete unit whose blockers are complete.
