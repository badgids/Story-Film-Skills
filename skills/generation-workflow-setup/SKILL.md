---
name: generation-workflow-setup
description: Discover complete ComfyUI workflows from Story-Film's bundled library, project defaults, saved ComfyUI workflows, templates, external workflow sources, or live-schema generation, then let the user select each required task from an ordinary numbered list.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Generation Workflow Setup

Use this skill before ComfyUI generation or whenever the user wants to change the workflow used for a generation task.

## Read

Read `../../references/WORKFLOW_SELECTION.md`.

## Required behavior

1. Determine the generation task category that the current production step needs.
2. Discover the active ComfyUI server when server-side saved workflows or templates are relevant.
3. Run `../../scripts/workflow_catalog.py catalog <project-root> --category <task> --url <server-url>`.
4. Add `--query <text>` when the task needs a narrower subset.
5. Show the command's complete ordinary numbered list to the user.
6. Do **not** use `ask_user_question` or another TUI picker for workflow selection.
7. Do **not** truncate the list to four entries. A workflow catalog can contain any practical number of choices.
   There is no four-choice limit for workflow selection.
8. Ask the user to reply with the number of the workflow to use.
9. After the user replies, record that exact choice with `workflow_catalog.py choose`.
10. Materialize the selected source with `workflow_catalog.py materialize` unless the selected source is the `generate-new` choice.
11. If `generate-new` was selected, use `comfyui-workflow` to build one candidate from live schemas, validate it, save it as a project workflow, refresh the catalog, and record the resulting real workflow.
12. Inspect and live-validate the selected workflow before execution.
13. If the workflow names unavailable models or missing nodes, report the exact blocker. Do not silently replace the workflow, model, VAE, encoder, LoRA, or other resource.
14. Continue to the next required task category only after the current workflow choice is recorded.

## Source types

The catalog can include:

- bundled workflows under `../../comfyui_workflows/<task>/<model>/`;
- package custom defaults under `../../comfyui_workflows/custom/<task>/<model>/`;
- project defaults under `04_generation/comfyui/default_workflows/<task>/<model>/`;
- existing project workflows and templates;
- workflows saved by the user inside ComfyUI;
- ComfyUI core templates;
- installed custom-node workflow templates;
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

Saved ComfyUI workflows and ComfyUI templates do not need to be copied into these directories to appear in the live catalog.

## Done

Done when each generation task required by the current production scope has a durable selection in `00_project/workflow_preferences.json`, and the selected workflow has either passed its required validation or has a concrete unresolved blocker.
