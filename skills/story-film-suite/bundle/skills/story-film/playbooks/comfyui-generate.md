# Playbook: Generate Through ComfyUI

> Before ComfyUI generation, run `generation-workflow-setup`. Select complete workflows from the ordinary numbered catalog. Do not run the retired per-resource model-selection interview.

Use when a Story-Film project is ready to turn one or more approved image, video, voice, music, sound, reference-sheet, storyboard, orbit, or upscaling briefs into generated media through ComfyUI.

## Steps

1. Read `generation-pack` and `comfyui-handoff`. Build or refresh the smallest requested handoff scope.
2. Read `WORKFLOW_SELECTION.md`. Determine every workflow task category required by this generation scope.
3. For each required task, run `generation-workflow-setup`. The catalog must include the relevant bundled workflows, project defaults, saved ComfyUI workflows, templates, external sources, and the generated-workflow fallback. Print the complete numbered list and wait for the user's numeric choice.
4. Record each selected workflow in `00_project/workflow_preferences.json`. The workflow owns the concrete checkpoint/model, VAE, encoders, LoRAs, audio models, upscalers, nodes, sampler/scheduler settings, and other graph configuration.
5. Materialize each non-project source into `04_generation/comfyui/templates/selected/<task>/`. Preserve the original source. Do not edit a bundled workflow, saved ComfyUI workflow, template, or external source in place.
6. Read `comfyui` and `comfyui-discover`. Probe the live target. Inspect the selected workflow and validate the node classes, required inputs, and workflow resource names against the running server. The ComfyUI server registry and node schemas are runtime truth for whether the selected graph can execute.
7. If the selected workflow has a model/resource or custom-node blocker, report it exactly. Do not silently choose another workflow or replace the workflow's model stack. The user can edit/save the source, restore the missing dependency, choose another numbered workflow, or explicitly select the generated-workflow fallback.
8. If the user selected the generate-new catalog option, read `comfyui-workflow`. Use the bounded live-schema generation path to create exactly one candidate. Do not guess class names from memory and do not install custom nodes. Validate and save the generated workflow as a project workflow, refresh the catalog, and record the real generated workflow as the selection.
9. Run only the prompt adapter needed by the selected workflow when model-specific prompt grammar is required. Canon, model-neutral briefs, exact dialogue, and approved creative intent remain authoritative.
10. Validate the workflow-family contract when one exists. For reference-driven graphs, run `comfyui-binding-audit` after uploads/staging and after UI-to-API conversion or patching so prompt labels, graph inputs, `REF-###`/`MEDIA-###`, staged paths, and hashes agree.
11. Read `comfyui-assets`. Upload or stage required project inputs and patch only the exact selected project-owned workflow copy. Replace author-local input picker paths with current staged project inputs where required. Do not alter the bundled source.
12. Before a heavy local generation, inspect current device memory and prove where Pi's active LLM runs. If a local LLM shares the machine and cannot safely coexist with the selected workflow's required models, route the prepared scope through `resource-safe-comfyui`. Every workflow choice and input mapping must be finalized before unloading the LLM.
13. Read `comfyui-run`. Submit asynchronously with the originating stable shot/cue ID and retain the returned prompt ID. Append every resubmit as a new run instead of replacing the failed prompt ID. For multiple shots or cues, submit and reconcile one controlled batch at a time.
14. Wait or poll, then collect media and text outputs. Store downloaded copies under `04_generation/comfyui/outputs/` and associate each output with the originating stable shot/cue ID and prompt ID. Register every concrete media output through `asset-approval`.
15. Run the relevant continuity and prompt QC checks. Run `media-qc` on actual media where applicable, then use `take-selection` when the output represents a planned shot or storyboard panel.
16. When alternatives exist, select the approved take before downstream editorial work treats any render as authoritative.
17. Use `project-impact` when an approved generated reference becomes an upstream production asset that changes downstream work.

## Done

Every requested generated asset is traceable from Story-Film ID to handoff brief to selected workflow identity to project-owned workflow copy to ComfyUI prompt ID to output, and reviewed candidates have explicit approval state, or the scope has a concrete live blocker.
