# ComfyUI Workflow Selection

Story-Film Skills selects complete ComfyUI workflows for generation. It does not require the user to build a model stack by answering separate adapter, checkpoint, VAE, text-encoder, LoRA, audio-model, or upscaler questions.

## Authority

For ComfyUI generation, the selected workflow is the authority for its concrete ComfyUI graph and the resource names stored in that graph.

A workflow can include its own:

- checkpoint or diffusion model
- VAE
- text encoder
- CLIP Vision model
- LoRAs
- ControlNet models
- audio encoders and audio models
- upscalers
- sampler and scheduler settings
- node-specific model choices
- generation parameters

Story-Film may patch project inputs, approved prompts, stable output IDs, seeds, dimensions, durations, and other explicitly mapped production values into a preserved project-owned copy. It must not silently replace the workflow's model stack with a different model stack.

`00_project/model_preferences.json` and `scripts/model_preferences.py` are legacy compatibility/debug facilities. They are not the generation-selection authority for workflow-first projects.

## Workflow categories

The workflow catalog supports these task categories:

- `image`
- `image-edit`
- `video`
- `tts`
- `music`
- `sfx`
- `character-sheet`
- `orbit-sheet`
- `location-orbit`
- `prop-sheet`
- `storyboard`
- `upscale`
- `frame-interpolation`
- `llm`
- `other`

The list is extensible. A new task should use the same workflow-first selection rules.

## Playbook preflight

If the selected playbook or requested endpoint will use ComfyUI at any point, workflow selection is a playbook-entry gate. Initialize the empty Story-Film project container if necessary, then determine every required workflow task before writing story, canon, screenplay, or other creative production artifacts.

Use `scripts/workflow_preflight.py` to record the required categories. Film-producing playbooks use the deterministic `film-production` profile unless the playbook declares a narrower scope. Direct generation playbooks can record explicit task categories.

For every missing category, run the normal numbered workflow catalog and record the user's choice. Once the preflight reports `complete`, later playbook stages must reuse those durable selections and must not ask the user to choose workflows again. Reopen selection only when the user explicitly requests a workflow change.

A later missing model, node, input, or other live validation dependency is a blocker. It is not permission to silently select a different workflow or restart the workflow interview.

Workflow discovery is unbounded by Story-Film. Enumerate every relevant built-in, package-custom, project-default, project-workflow, saved-ComfyUI, external, and user-added workflow returned by discovery. Do not cap, truncate, or silently omit choices because the catalog is large.

Durable preflight state is stored in:

```text
00_project/workflow_preflight.json
```

## Workflow sources

Story-Film can catalog workflows from all of these sources.

### 1. Bundled Story-Film workflows

The built-in library is:

```text
comfyui_workflows/<task>/<model>/*.json
```

These are complete editable ComfyUI workflow JSON files.

### 2. Package-level custom defaults

Users who intentionally maintain a customized Story-Film installation can add workflow defaults under:

```text
comfyui_workflows/custom/<task>/<model>/*.json
```

These appear in the same catalog but are labeled as package custom workflows.

### 3. Project-local default workflows

Project-specific defaults belong under:

```text
04_generation/comfyui/default_workflows/<task>/<model>/*.json
```

This is the preferred place for project-owned defaults because package updates do not replace them.

### 4. Existing project workflows

Story-Film catalogs JSON workflows already present under:

```text
04_generation/comfyui/workflows/
```

`04_generation/comfyui/templates/` remains an internal project-owned staging/materialization area. Files placed there are not added to workflow selection merely because they are templates.

### 5. The user's saved ComfyUI workflows

When the running ComfyUI server exposes its userdata workflow listing, Story-Film catalogs the user's saved workflows from ComfyUI.

### 6. ComfyUI templates are user-managed

Story-Film does not search ComfyUI core or custom-node template catalogs. If the user wants to use one of those templates, they can open it in ComfyUI and save it into their own workflow area, or register an exported workflow file/directory as an external source. It then participates in selection as a normal user-saved or external workflow.

### 7. Explicit external files or directories

The user can point Story-Film at another `.json` workflow or directory of workflows.

Registered external sources are stored in:

```text
00_project/workflow_sources.json
```

Paths are user-provided runtime configuration. Story-Film source code must never contain a hardcoded personal machine path.

### 8. A new Story-Film-generated workflow

If none of the available workflows fits, the numbered catalog can include a `generate-new` choice.

Choosing it authorizes Story-Film to create one candidate from the running ComfyUI server's live node schemas using the bounded workflow-generation path. The candidate must pass live validation before becoming runnable. Story-Film must not guess node classes from memory or silently install missing custom nodes.

## Numbered selection, not a TUI question limit

Do not use a four-option question widget to select workflows.

For each required task:

1. build the complete relevant workflow catalog;
2. print an ordinary numbered list;
3. include all relevant choices even when the list contains more than four entries;
4. tell the user to reply with the number;
5. wait for that user reply;
6. record exactly that workflow choice;
7. materialize a project-owned copy when the source is not already a project-owned file;
8. validate before generation.

Example:

```text
Video workflow choices:

1. [project default] MiniMax-H3 - my_h3_default.json
2. [built-in] MiniMax-H3 - video_minimax_h3_i2v.json
3. [built-in] MiniMax-H3 - video_minimax_h3_r2v.json
4. [built-in] MiniMax-H3 - video_minimax_h3_r2v_exact_audio_hybrid.json
5. [built-in] MiniMax-H3 - video_minimax_h3_t2v.json
6. [ComfyUI saved] workflows/my_video_workflow.json
7. [external] studio_video.json
8. [generate] Generate a new workflow from live ComfyUI schemas

Reply with the number you want to use.
```

The numeric catalog entry is ephemeral. The durable selection stores the workflow identity and source, not only the number.

## Durable workflow state

`00_project/comfyui_workflow_catalog.json` stores the most recent numbered catalog snapshot.

`00_project/workflow_preferences.json` stores selected workflows by task category.

`00_project/workflow_sources.json` stores user-registered external files or directories.

A selection record includes enough source identity to reopen or materialize the same workflow without reconstructing the choice from chat history.

## Materialization

Never edit a bundled workflow, a saved ComfyUI workflow, or an external source in place during production.

Copy or fetch the selected source into the project first:

```text
04_generation/comfyui/templates/selected/<task>/
```

The selected copy remains editable and inspectable.

When a user opens a bundled workflow in ComfyUI, changes its model choices or settings, and saves it as a ComfyUI user workflow, that saved workflow becomes a separate selectable source on the next catalog refresh.

## Validation

The selected workflow still must be compatible with the running ComfyUI server.

Before execution:

1. identify UI versus API workflow format;
2. inspect required node classes;
3. validate node classes and required inputs against live `/object_info`;
4. verify that referenced model resources are available to the selected nodes;
5. report missing custom-node packages where known;
6. stage project references and inputs;
7. audit reference bindings when required;
8. convert or promote only through the normal bounded ComfyUI workflow path;
9. confirm a retrievable output path.

If a selected workflow refers to an unavailable model or missing node, stop with a blocker. Do not silently substitute another workflow or model. The user can edit/save the workflow, install the missing dependency, or choose a different numbered workflow.

## Prompt adapters

Prompt adapters remain useful for translating model-neutral production intent into prompt grammar when a selected workflow needs model-specific prompt syntax.

The selected workflow determines which adapter is appropriate. The user is not asked to separately choose an adapter and then separately choose every model file.

## Completion

Workflow selection for a task is complete when:

- any required playbook workflow preflight is complete before creative production begins;
- a durable workflow selection exists;
- the source still resolves or has been materialized into the project;
- the workflow has been inspected;
- any required live validation has passed or a concrete blocker is recorded.

Generation cannot claim completion merely because a workflow was selected.
