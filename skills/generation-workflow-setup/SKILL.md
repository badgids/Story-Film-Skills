---
name: generation-workflow-setup
description: Discover complete ComfyUI workflows only from Story-Film's extension-local comfyui_workflows library, then let the user select each required task from an ordinary numbered list.
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
3. For a missing category, run `../../scripts/workflow_catalog.py catalog <project-root> --category <task>`.
4. Add `--query <text>` when the task needs a narrower subset.
5. Show the command's complete ordinary numbered list to the user.
6. Do **not** use `ask_user_question` or another TUI picker for workflow selection.
7. Do **not** truncate the list. Story-Film imposes no maximum workflow count. Show every built-in and package-custom workflow in the extension library regardless of how many choices exist.
   There is no four-choice limit for workflow selection. There is no higher Story-Film workflow-count limit.
8. Ask the user to reply with the number of the workflow to use.
9. After the user replies, record that exact choice with `workflow_catalog.py choose`.
10. Materialize the selected extension source with `workflow_catalog.py materialize`.
11. Inspect and live-validate the selected workflow before execution.
12. If the workflow names unavailable models or missing nodes, report the exact blocker. Do not silently replace the workflow, model, VAE, encoder, LoRA, or other resource.
13. Continue to the next required task category only after the current workflow choice is recorded.

## Source types

The catalog can include only:

- bundled workflows under `../../comfyui_workflows/<task>/<model>/`;
- package custom workflows under `../../comfyui_workflows/custom/<task>/<model>/`.

Project workflow/default folders, ComfyUI userdata, arbitrary external paths, and ComfyUI template catalogs are not discovery sources.

Do not prefer a source merely because it appears first. The user chooses from the numbered list.

## Workflow owns the model stack

Do not run a second adapter/checkpoint/VAE/text-encoder/LoRA questionnaire after workflow selection.

The selected workflow owns the concrete model/resource values stored in its graph. Prompt adapters may still translate model-neutral production intent when the selected workflow requires model-specific prompt grammar.

`model_preferences.json` is legacy compatibility data. It does not override a selected workflow.

## Live model registry validation

When checking whether resource names stored in the selected workflow are available, use the running ComfyUI server registry. Use `/models` and `/models/{folder}` through the bundled discovery helpers. These registry results include external model roots configured by `extra_model_paths.yaml`.

Use `scripts/model_inventory.py scan` only for low-level diagnostics and compatibility reporting. Do not run `find /` or another filesystem sweep to rediscover model files. Do not replace it with direct `curl`, `wget`, or one-off Python parsers. The running ComfyUI registry is runtime truth for model availability.

## Custom workflow location

To add any custom, edited, exported, or newly authored workflow to Story-Film, copy its JSON file under:

```text
comfyui_workflows/custom/<task>/<model>/
```

Refresh the catalog after copying it. Story-Film never registers or scans an arbitrary external workflow path.

## Explicit workflow creation

Do not add a `generate-new` choice to every normal workflow catalog. However, if the user explicitly asks Story-Film to create, build, author, or design a new ComfyUI workflow, route to `comfyui-workflow` and use its bounded live-schema authoring path.

The new candidate must be built from real live node/model schemas, validated before promotion, and must not invent node classes or silently install dependencies. If the new workflow should become reusable/selectable by Story-Film, save or copy the validated JSON into `comfyui_workflows/custom/<task>/<model>/`, refresh the catalog, and record that real workflow as the durable selection when appropriate.

## Done

Done when each generation task required by the current production scope has a durable selection in `00_project/workflow_preferences.json`, any active workflow preflight is complete, and the selected workflow has either passed its required validation or has a concrete unresolved blocker.
