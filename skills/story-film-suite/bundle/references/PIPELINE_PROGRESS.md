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

The current leaf is also a hard work boundary. An agent must not open a future Story-Film specialist or create that later specialist's artifact while the current leaf is still pending/current/blocked. Complete, validate, checkpoint, then move. The Pi extension adds a runtime guard for future specialist reads when the requested skill is represented later in the active pipeline.

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

Compact mode is the default and shows three Story-Film pipeline rows. Expanded mode shows ten rows. Use `/story-todo toggle`, `/story-todo expand`, `/story-todo collapse`, or `Ctrl+Alt+End`. Both modes can scroll. The widget always shows a compact key hint so the end user can discover the controls.

It follows the current item unless the user manually scrolls. `Ctrl+Alt+Home` or `/story-todo current` returns to follow mode.

The extension also exposes compact Pi status lines for the active pipeline and next action. It appends a small runtime reminder to each agent turn so the model sees the authoritative current target. It can block a read of a specialist skill that only appears in a future pending pipeline target. This prevents accidental work-ahead without pretending that file existence proves completion.

Pi or another harness may also provide its own generic Todo panel. That panel is owned by the host, not by the Story-Film extension. When the agent uses it during a Story-Film run, it must mirror at most three Story-Film items: current, immediate next, and endpoint. `pipeline_progress.json` remains authoritative if the two displays disagree. On compatible Pi Todo tools, the extension also blocks initialization of a generic Story-Film mirror with more than three items.

The UI owns no pipeline state and can be removed without damaging project resumability.

## Resource-handoff status

`00_project/resource_handoff.json` is a separate deterministic runtime-status channel for exclusive local-LLM/ComfyUI handoffs. The Pi extension may render it beside the Todo and emit phase-change notifications without calling an LLM. It never replaces `pipeline_progress.json` as the pipeline cursor, and the resource runner must not checkpoint creative work on its own.
