# Recover After a Reboot

[Documentation home](../README.md) | [Up: Pi Todo](../production/todo-and-progress.md) | [Next: Session handoff](session-handoff.md)

## Table of contents

- [Purpose](#purpose)
- [Create a checkpoint](#create-a-checkpoint)
- [Resume](#resume)
- [Resume modes](#resume-modes)

## Purpose

A long film project can continue for days or months. A machine restart must not force the agent to guess where work stopped.

## Create a checkpoint

At important boundaries, run:

```bash
python scripts/recovery_checkpoint.py PROJECT checkpoint
```

The checkpoint stores hashes of key control files plus the current pipeline, sequence, and resource-handoff state.

Files:

```text
00_project/recovery/checkpoint.json
00_project/recovery/checkpoint.md
00_project/recovery/journal.jsonl
```

## Resume

After restart:

```bash
python scripts/recovery_checkpoint.py PROJECT resume
```

Do not rebuild the state from chat history.

## Resume modes

`exact` means the checked control files still match the checkpoint.

`dirty` means one or more control files changed after the checkpoint. Inspect the differences before continuing.

`resource-interrupted` means the machine stopped during the exclusive ComfyUI/LLM handoff. Restore resources safely before normal work continues.

## Related pages

- [Pi Todo and progress](../production/todo-and-progress.md)
- [Resource-safe generation](../generation/resource-safe.md)
- [Session handoff](session-handoff.md)
