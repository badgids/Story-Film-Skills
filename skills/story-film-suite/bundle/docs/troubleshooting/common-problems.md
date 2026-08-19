# Common Problems

[Documentation home](../README.md) | [Up: Documentation home](../README.md) | [Quick start](../getting-started/quick-start.md)

## Table of contents

- [The Todo does not appear](#the-todo-does-not-appear)
- [ComfyUI cannot run a workflow](#comfyui-cannot-run-a-workflow)
- [The computer runs out of memory](#the-computer-runs-out-of-memory)
- [A rich document fails validation](#a-rich-document-fails-validation)
- [A feature film cannot pass completion](#a-feature-film-cannot-pass-completion)
- [Work resumed at the wrong place](#work-resumed-at-the-wrong-place)

## The Todo does not appear

Confirm that the Pi extension was installed. The durable progress files still work without the widget.

Run:

```bash
python scripts/pipeline_progress.py status PROJECT
```

## ComfyUI cannot run a workflow

Validate the final API workflow against the live server. Check required nodes, models, and uploaded inputs.

Do not mark the job complete when submission fails.

## The computer runs out of memory

Use resource-safe generation. Configure conservative RAM and VRAM limits. Do not load the local LLM and a heavy ComfyUI model together if the machine cannot hold both.

## A rich document fails validation

Check for a same-basename Markdown file.

Example:

```text
budget.xlsx
budget.md
```

The Markdown file must contain meaningful content.

## A feature film cannot pass completion

Read:

```text
06_release/completeness_audit.md
00_project/health_report.md
```

Repair the named blocker. Do not bypass the final gate.

## Work resumed at the wrong place

Use the recovery checkpoint and pipeline progress files. Do not infer the cursor from old chat text.

## Related pages

- [Recovery](../operations/recovery.md)
- [Production health](../production/health.md)
- [Testing](../development/testing.md)
