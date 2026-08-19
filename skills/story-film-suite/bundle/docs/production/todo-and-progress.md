# Pi Todo and Pipeline Progress

[Documentation home](../README.md) | [Up: Feature-scale production](feature-scale.md) | [Recovery](../operations/recovery.md)

## Table of contents

- [What the Todo shows](#what-the-todo-shows)
- [Source of truth](#source-of-truth)
- [Pi commands](#pi-commands)
- [Command-line controls](#command-line-controls)

## What the Todo shows

The Pi extension shows stages, steps, and substeps.

It follows the current task automatically.

It can show blocked state and the next action.

It can also show deterministic ComfyUI resource-handoff status while the LLM is unloaded.

## Source of truth

The UI is not the source of truth.

This file is the source of truth:

```text
00_project/pipeline_progress.json
```

The event history is:

```text
00_project/progress_events.jsonl
```

The human handoff is:

```text
00_project/HANDOFF.md
```

## Pi commands

```text
/story-todo status
/story-todo up
/story-todo down
/story-todo page-up
/story-todo page-down
/story-todo current
/story-resource
```

## Command-line controls

```bash
python scripts/pipeline_progress.py status PROJECT
python scripts/pipeline_progress.py checkpoint PROJECT --status completed
python scripts/pipeline_progress.py checkpoint PROJECT --status blocked --blocker "Reason"
python scripts/pipeline_progress.py pause PROJECT --note "Reason"
python scripts/pipeline_progress.py resume PROJECT
```

A failed validation must not advance the Todo.

## Related pages

- [Recovery after reboot](../operations/recovery.md)
- [Resource-safe generation](../generation/resource-safe.md)
