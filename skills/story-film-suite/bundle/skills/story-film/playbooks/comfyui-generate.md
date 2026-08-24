# Playbook: Generate Through ComfyUI

> Workflow preflight gate: before building or changing generation briefs, record every ComfyUI task category required by this requested scope and complete workflow selection for every missing category. Reuse those selections throughout this playbook.

Use when a Story-Film project is ready to turn one or more approved image, video, voice, music, sound, reference-sheet, storyboard, orbit, or upscaling briefs into generated media through ComfyUI.

## Steps

1. Read `WORKFLOW_SELECTION.md` and verify `workflow_preflight.py status` is complete for this generation scope. If this playbook was invoked directly without router preflight, complete that preflight now before building or changing generation briefs.
2. Read `generation-pack` and `comfyui-handoff`. Build or refresh the smallest requested handoff scope using the already selected workflows.
3. Read each durable selection from `00_project/workflow_preferences.json`. Do not print a new workflow catalog or ask for another workflow choice unless the user explicitly requested a change.
4. Treat each selected workflow as authority for its concrete checkpoint/model, VAE, encoders, LoRAs, audio models, upscalers, nodes, sampler/scheduler settings, and other graph configuration.
5. Materialize the selected extension source into `04_generation/comfyui/templates/selected/<task>/`. Preserve the original source. Do not edit a bundled or package-custom workflow in place.
6. Read `comfyui` and `comfyui-discover`. Probe the live target. Inspect the selected workflow and validate the node classes, required inputs, and workflow resource names against the running server. The ComfyUI server registry and node schemas are runtime truth for whether the selected graph can execute.
7. If the selected workflow has a model/resource or custom-node blocker, report it exactly. Do not silently choose another workflow or replace the workflow's model stack. The user can update/export the source into `comfyui_workflows/custom/<task>/<model>/`, restore the missing dependency, or choose another numbered extension workflow.
8. If the user explicitly asks Story-Film to create a new workflow, read `comfyui-workflow` and use the bounded live-schema workflow-authoring path. This is explicit authoring, not a catalog fallback: inspect real live schemas, build one candidate outside the runnable directory, validate it, and do not invent node classes or silently install dependencies. For a reusable workflow, save or copy the validated JSON into `comfyui_workflows/custom/<task>/<model>/`, refresh the catalog, and record the resulting real workflow when it will be used.
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
