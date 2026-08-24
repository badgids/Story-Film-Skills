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

Workflow discovery is unbounded by Story-Film within the extension library. Enumerate every relevant built-in and package-custom workflow under `comfyui_workflows/`; do not cap, truncate, or silently omit choices because the catalog is large.

Durable preflight state is stored in:

```text
00_project/workflow_preflight.json
```

## Workflow sources

Story-Film catalogs workflows from one authoritative location: the extension's `comfyui_workflows/` directory.

### 1. Bundled Story-Film workflows

The built-in library is:

```text
comfyui_workflows/<task>/<model>/*.json
```

These are complete editable ComfyUI workflow JSON files. `research/` remains excluded from ordinary production selection.

### 2. User/custom Story-Film workflows

To add a workflow for Story-Film, copy the JSON file into:

```text
comfyui_workflows/custom/<task>/<model>/*.json
```

These appear in the same numbered catalog as `package-custom` workflows. There is no catalog-size limit.

Story-Film does **not** scan:

- ComfyUI's saved/userdata workflows;
- ComfyUI core or custom-node template catalogs;
- `04_generation/comfyui/default_workflows/`;
- `04_generation/comfyui/workflows/`;
- arbitrary user-registered files or directories.

Project `templates/` and `workflows/` directories remain production staging/output areas after selection; they are not discovery sources. If a user creates or exports a new workflow, copy it into the appropriate `comfyui_workflows/custom/<task>/<model>/` directory before refreshing the catalog.

## Explicit workflow creation

Workflow **creation remains supported**. Extension-only discovery does not mean Story-Film is limited to workflows that already exist.

When the user explicitly asks Story-Film to create, build, author, or design a new ComfyUI workflow:

1. treat that request as workflow authoring, not workflow discovery;
2. use the running ComfyUI server's live node/model schemas to determine real installed classes, inputs, outputs, and resource choices;
3. build one bounded candidate outside the runnable workflow directory;
4. validate the candidate against the live schemas and normal Story-Film workflow gates;
5. do not invent node classes from memory and do not silently install missing custom nodes;
6. promote a validated project-specific candidate only through the normal workflow-promotion path;
7. when the workflow should be reusable/selectable by Story-Film, save or copy its JSON into `comfyui_workflows/custom/<task>/<model>/` and refresh the catalog.

Story-Film does not need a permanent `generate-new` row in every numbered catalog. Explicit user intent to create a workflow is sufficient authorization to enter the bounded workflow-authoring path.

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

1. [package-custom] MiniMax-H3 - my_h3_custom.json
2. [built-in] MiniMax-H3 - video_minimax_h3_i2v.json
3. [built-in] MiniMax-H3 - video_minimax_h3_r2v.json
4. [built-in] MiniMax-H3 - video_minimax_h3_r2v_exact_audio_hybrid.json
5. [built-in] MiniMax-H3 - video_minimax_h3_t2v.json

Reply with the number you want to use.
```

The numeric catalog entry is ephemeral. The durable selection stores the workflow identity and source, not only the number.

## Durable workflow state

`00_project/comfyui_workflow_catalog.json` stores the most recent numbered catalog snapshot.

`00_project/workflow_preferences.json` stores selected workflows by task category.

A selection record includes enough extension-library source identity to reopen or materialize the same workflow without reconstructing the choice from chat history.

## Materialization

Never edit a bundled or package-custom source in place during production.

Copy or fetch the selected source into the project first:

```text
04_generation/comfyui/templates/selected/<task>/
```

The selected copy remains editable and inspectable.

When a user edits a workflow in ComfyUI, the edited/exported JSON becomes selectable only after it is copied into `comfyui_workflows/custom/<task>/<model>/` and the Story-Film catalog is refreshed.

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
