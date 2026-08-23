---
name: generation-workflow-setup
description: Discover complete ComfyUI workflows from Story-Film's bundled library, project defaults, saved ComfyUI user workflows, external workflow sources, or live-schema generation, then let the user select each required task from an ordinary numbered list.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Generation Workflow Setup

Use this skill before ComfyUI generation or whenever the user wants to change the workflow used for a generation task.

## Read

Read `../../references/WORKFLOW_SELECTION.md`.

## Playbook preflight and reuse

When the selected playbook will use ComfyUI, workflow selection happens before story/canon creation. Run `../../scripts/workflow_preflight.py set` for the playbook/profile or explicit task categories, then resolve every missing category before creative production begins.

If a required category already has a durable selection and the user did not ask to change it, reuse that exact selection. Materialize or validate it as needed, but do not show the numbered list again. Do not ask again later.

Only missing categories or an explicit user-requested workflow change open an interactive numbered catalog. A later missing model/node/input is a blocker, not permission to reopen workflow selection.

## Required behavior

1. Check `00_project/workflow_preferences.json` first. If the task already has a durable selection and no change was requested, reuse it without another user question.
2. Determine the generation task category that the current preflight or production step needs.
3. Discover the active ComfyUI server when the user's saved ComfyUI workflows are relevant. Do not search ComfyUI core/custom template catalogs.
4. For a missing category, run `../../scripts/workflow_catalog.py catalog <project-root> --category <task> --url <server-url>`.
5. Add `--query <text>` when the task needs a narrower subset.
6. Show the command's complete ordinary numbered list to the user.
7. Do **not** use `ask_user_question` or another TUI picker for workflow selection.
8. Do **not** truncate the list. Story-Film imposes no maximum workflow count. Show every discovered workflow, including user-added workflows, regardless of how many choices exist.
   There is no four-choice limit for workflow selection. There is no higher Story-Film workflow-count limit.
9. Ask the user to reply with the number of the workflow to use.
10. After the user replies, record that exact choice with `workflow_catalog.py choose`.
11. Materialize the selected source with `workflow_catalog.py materialize` unless the selected source is the `generate-new` choice.
12. If `generate-new` was selected, use `comfyui-workflow` to build one candidate from live schemas, validate it, save it as a project workflow, refresh the catalog, and record the resulting real workflow.
13. Inspect and live-validate the selected workflow before execution.
14. If the workflow names unavailable models or missing nodes, report the exact blocker. Do not silently replace the workflow, model, VAE, encoder, LoRA, or other resource.
15. Continue to the next required task category only after the current workflow choice is recorded.

## Source types

The catalog can include:

- bundled workflows under `../../comfyui_workflows/<task>/<model>/`;
- package custom defaults under `../../comfyui_workflows/custom/<task>/<model>/`;
- project defaults under `04_generation/comfyui/default_workflows/<task>/<model>/`;
- existing project workflows;
- workflows saved by the user inside ComfyUI;
- explicit external files or directories registered by the user;
- a final `generate-new` choice.

Do not prefer a source merely because it appears first. The user chooses from the numbered list.

## Workflow owns the model stack

Do not run a second adapter/checkpoint/VAE/text-encoder/LoRA questionnaire after workflow selection.

The selected workflow owns the concrete model/resource values stored in its graph. Prompt adapters may still translate model-neutral production intent when the selected workflow requires model-specific prompt grammar.

`model_preferences.json` is legacy compatibility data. It does not override a selected workflow.

## Live model registry validation

When checking whether resource names stored in the selected workflow are available, use the running ComfyUI server registry. Use `/models` and `/models/{folder}` through the bundled discovery helpers. These registry results include external model roots configured by `extra_model_paths.yaml`.

Use `scripts/model_inventory.py scan` only for low-level diagnostics and compatibility reporting. Do not run `find /` or another filesystem sweep to rediscover model files. Do not replace it with direct `curl`, `wget`, or one-off Python parsers. The running ComfyUI registry is runtime truth for model availability.

## Custom workflow locations

Package-level custom defaults:

```text
comfyui_workflows/custom/<task>/<model>/
```

Project-local defaults:

```text
04_generation/comfyui/default_workflows/<task>/<model>/
```

Register another file or directory:

```bash
python scripts/workflow_catalog.py source-add <project-root> <workflow-or-directory>
```

Saved ComfyUI user workflows appear in the live catalog. ComfyUI core/custom templates do not. If the user wants a template, they must save or copy it into their own ComfyUI workflow area first.

## Done

Done when each generation task required by the current production scope has a durable selection in `00_project/workflow_preferences.json`, any active workflow preflight is complete, and the selected workflow has either passed its required validation or has a concrete unresolved blocker.
