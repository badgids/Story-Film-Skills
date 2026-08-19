# Durable Pipeline Progress and Pi Todo

## Purpose

Long story, film, trailer, campaign, and release workflows need progress state that survives chat compaction, process restarts, model changes, and handoff to a small local model.

Story-Film Skills therefore stores pipeline execution state in project files and optionally renders it through a Pi extension.

## Files

```text
00_project/
  pipeline_progress.json
  progress_events.jsonl
  HANDOFF.md
```

`pipeline_progress.json` is authoritative for execution position.

`progress_events.jsonl` is an append-only transition history.

`HANDOFF.md` is a compact human-readable recovery pointer. It is written last during a checkpoint so it never intentionally points ahead of canonical progress state.

## Schema

```json
{
  "schema_version": 1,
  "owner": "badgids-story-film-skills",
  "pipeline_id": "short-film",
  "label": "Short Film",
  "source_playbook": "skills/story-film/playbooks/short-film.md",
  "status": "active",
  "cursor": {
    "stage_id": "PST-001",
    "target_id": "PST-001"
  },
  "next_action": "Create the story brief",
  "blocker": "",
  "last_completed": "",
  "stages": [],
  "updated_at": ""
}
```

Pipeline statuses:

- `inactive`
- `active`
- `paused`
- `blocked`
- `complete`

Node statuses:

- `pending`
- `current`
- `completed`
- `blocked`
- `skipped`

## Hierarchy

The compiler reads numbered playbook steps.

- root playbook numbered items become stages
- directly referenced nested playbooks may become steps
- one further nested playbook level may become substeps

The hierarchy is intentionally capped at stage -> step -> substep. Deeper orchestration should be represented as a new bounded playbook instead of creating an unreadable progress tree.

The model does not estimate counts. Counts come from the selected playbook files.

## Non-advancing validation

A step is completed only after its required artifact validation succeeds.

A validation error changes the active leaf to `blocked`; it does not select the next leaf. Repair stays scoped to the same current target until it passes.

## Recovery

After restart or context compaction:

1. read `00_project/pipeline_progress.json`
2. read `00_project/HANDOFF.md`
3. inspect only the current target and its required upstream artifacts
4. verify any output that exists but was not checkpointed
5. continue the current target
6. checkpoint after validation

File existence alone never proves completion.

If `HANDOFF.md` and `pipeline_progress.json` disagree, stop progression and trust the JSON ledger until the mismatch is reconciled.

## Interaction with dependency invalidation

Progress state says what execution step is current. It does not decide which creative artifacts are stale.

If a retry changes an approved upstream artifact:

1. use `project-impact`
2. update dependency/stale state
3. keep unrelated completed progress and artifacts intact
4. reset only the progress scope that actually needs execution again

## Pi viewport

The optional Pi extension reads this file and renders a scrollable viewport above the editor.

It follows the current item unless the user manually scrolls. `Ctrl+Alt+Shift+Home` or `/story-todo current` returns to follow mode.

The extension also exposes compact Pi status lines for the active pipeline and next action.

The UI owns no pipeline state and can be removed without damaging project resumability.

## Resource-handoff status

`00_project/resource_handoff.json` is a separate deterministic runtime-status channel for exclusive local-LLM/ComfyUI handoffs. The Pi extension may render it beside the Todo and emit phase-change notifications without calling an LLM. It never replaces `pipeline_progress.json` as the pipeline cursor, and the resource runner must not checkpoint creative work on its own.
