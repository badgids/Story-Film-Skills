# Pi Todo and Pipeline Progress

[Documentation home](../README.md) | [Up: Feature-scale production](feature-scale.md) | [Recovery](../operations/recovery.md)

## Table of contents

- [What the Todo shows](#what-the-todo-shows)
- [Source of truth](#source-of-truth)
- [Compact and expanded views](#compact-and-expanded-views)
- [Keep the two Todo panels small](#keep-the-two-todo-panels-small)
- [Why a Todo can look stale](#why-a-todo-can-look-stale)
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


## Compact and expanded views

The Story-Film Todo starts in compact mode. Compact mode shows three pipeline rows. It follows the current row automatically. You can still scroll it.

Expanded mode shows ten pipeline rows. Both compact and expanded modes show the full keyboard control legend; expanded mode also shows the detailed next-action line.

Toggle the Story-Film panel with:

```text
/story-todo toggle
```

You can also use:

```text
/story-todo expand
/story-todo collapse
Ctrl+Alt+End
```

`Ctrl+Alt+End` is the keyboard toggle. The extension also listens to Pi's raw terminal-input hook and routes the chord through Pi's own key parser when normal extension shortcut dispatch is unavailable; it does not require the user to run a shell command.

## Keep the two Todo panels small

Some Pi distributions have their own generic Todo panel. Story-Film does not own that host panel. The public extension API does not give Story-Film a portable way to set the host panel's row count or expanded state.

When a Story-Film pipeline is active, the agent must not copy all Story-Film stages into the generic Todo. If it uses the generic Todo, keep at most three Story-Film items there:

1. current Story-Film target
2. immediate next Story-Film target
3. requested final endpoint

This keeps the host Todo small while the Story-Film Todo provides the detailed pipeline view. On compatible Pi Todo tools, the extension blocks a new generic Story-Film list when it contains more than three items.

## Why a Todo can look stale

The Story-Film panel reads `pipeline_progress.json`. It does not guess progress from files on disk. This is intentional. A file can exist and still be incomplete or invalid.

If the agent starts the world bible while the ledger still says `story-brief`, the problem is not the screen refresh. The agent worked ahead without checkpointing the earlier targets.

Story-Film now adds two runtime protections:

1. Before each agent turn, the extension states the authoritative current Story-Film target.
2. When possible, the extension blocks reads of specialist skills that are only in future pending targets.

The model must finish the current target, validate it, and run the checkpoint command before starting the next target.

Do not repair stale progress by marking files complete only because they exist. Validate them first.

## Pi commands

```text
/story-todo status
/story-todo toggle
/story-todo expand
/story-todo collapse
/story-todo up
/story-todo down
/story-todo page-up
/story-todo page-down
/story-todo current
/story-todo help
/story-todo keys
/story-resource
```

Keyboard controls:

```text
Ctrl+Alt+End              Toggle compact or expanded view
Ctrl+Alt+Up/Down          Scroll one row
Ctrl+Alt+PageUp/PageDown  Scroll one page
Ctrl+Alt+Home             Focus/follow the current Story-Film item
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
