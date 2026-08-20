# Playbook: Generate Through ComfyUI


> Before model-specific prompts or ComfyUI workflows, run `generation-model-setup`. Poll the live ComfyUI model inventory and record the user-selected adapter plus exact model resources for each production process. MiniMax H3 is only the default video adapter. Do not guess concrete model files, VAEs, text encoders, LoRAs, audio models, or upscalers.

Use when a story-film project is ready to turn one or more approved image, video, voice, music, or sound briefs into generated media through ComfyUI.

## Steps

1. Read `generation-pack` and `comfyui-handoff`. Build or refresh the smallest requested handoff scope.
2. Read `MODEL_SELECTION.md`. For video generation, honor the user's selected model. If no video model was selected, use `minimax-h3`. A missing selected model is a blocker; never silently switch to LTX or another model.
3. Read `comfyui` and `comfyui-discover`. Probe the live target and discover current node, model, feature, and resource capabilities. Model discovery must use `scripts/model_inventory.py scan` or the bundled `/models` client. The server registry includes external model roots configured through `extra_model_paths.yaml`; never search the filesystem to rediscover them. Use `/object_info` for node schemas, not as the primary model-file inventory.
4. Run `scripts/comfyui_control.py --project PROJECT workflow-catalog` before constructing anything. Select the first suitable source in this order: validated project workflow, project template, saved ComfyUI user workflow, official core template, installed custom-node example workflow. Do not skip directly to graph synthesis.
5. Read `comfyui-workflow`. Preserve the source workflow. Repair a failed runnable copy minimally instead of replacing it wholesale. For reusable or multi-stage graphs with current comfy-cli available, keep editable templates/fragments/blueprints under `04_generation/comfyui/` and compile the run artifact. For a small one-time API graph, map approved prompts, references, dimensions, durations, seeds, and other requested values into a preserved working copy using known inputs. Only when no suitable source exists may a new candidate be built from live schemas, and it must pass the bundled controller's workflow promotion step before becoming runnable.
6. Validate against live schemas. Missing nodes or model files are blockers, not permission to install them. If the server model registry is unexpectedly empty or inconsistent, stop and diagnose the live registry. Do not conclude that the user has no models merely because they are not inside the ComfyUI application directory. Do not fabricate mock outputs to advance the production pipeline.
7. Read `comfyui-assets`. Upload or stage required project inputs and replace workflow input values with the server-returned identity.
8. Before a heavy local generation, inspect current device memory and prove where Pi's active LLM runs. If Pi reports a base URL, classify it with `scripts/llm_runtime.py`. Loopback endpoints are local. OpenAI compatibility is not evidence of a cloud model. If the endpoint location is not proven, keep it unknown and do not select the external lifecycle mode. If a local LLM shares the machine and cannot safely coexist with the required ComfyUI models, stop the ordinary interactive loop here and route the requested batch through `resource-safe-comfyui`. That playbook must precompile and live-validate every remaining generation decision before unloading the LLM. Otherwise continue normally. Approve continuity-critical hero references and recurring voice identity before launching an expensive multi-shot batch. If the graph contains a paid partner/API route, obtain user approval before spending credits and keep credentials outside the workflow.
9. Read `comfyui-run`. Submit asynchronously with the originating stable shot/cue ID and retain the returned prompt ID. Append every resubmit as a new run instead of replacing the failed prompt ID. For multiple shots or cues, submit and reconcile one controlled batch at a time rather than losing shot identity in a large opaque queue.
10. Wait or poll, then collect media and text outputs. Store downloaded copies under `04_generation/comfyui/outputs/` and associate each output with the originating stable shot/cue ID and prompt ID. Register every concrete media output through `asset-approval` so voice, music, SFX, image, and video alternatives share durable approval behavior.
11. Run the relevant continuity and prompt QC checks. Run `media-qc` on actual media where applicable, then use `take-selection` when the output represents a planned shot or storyboard panel. If a result is rejected, preserve the run and take records and change only the necessary input or workflow parameter before rerunning.
12. When alternatives exist, select the approved take before downstream editorial work treats any render as authoritative.
13. Use `project-impact` when an approved generated reference becomes an upstream production asset that changes downstream work.

An adapter such as `qwen-image-2512` is a prompt-formatting adapter, not proof of a ComfyUI `class_type`, API node, local model file, or loader graph. Executable details must come from a selected existing workflow/template or the live node/model schemas.

## Done

Every requested generated asset is traceable from story-film ID to handoff brief to workflow copy to ComfyUI prompt ID to output, and reviewed shot candidates have explicit take/selection state, or the scope has an explicit live blocker.
