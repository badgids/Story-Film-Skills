# Playbook: Operate ComfyUI

Use when the user wants to inspect, validate, execute, monitor, cancel, or troubleshoot a ComfyUI workflow or server.

## Steps

1. Read `comfyui`.
2. Read `comfyui-discover` and probe the intended live server before naming installed nodes, models, templates, or available memory.
3. If a workflow file is involved, read `comfyui-workflow`. Preserve the original and detect whether it is UI format or API format.
4. Validate executable API-format workflows against live `/object_info` before submitting. If a UI-format workflow must run, prefer the official CLI through `comfyui-cli` when available or require an API export. Do not submit UI-format JSON directly to `/prompt`.
5. Stage required input media with `comfyui-assets`. Use the upload response name/subfolder/type in the executable workflow.
6. Read `comfyui-run`. Submit asynchronously, retain the returned prompt ID, and poll history or the selected job surface until terminal state.
7. Collect output metadata and requested files with `comfyui-assets`. Capture text outputs separately from media outputs.
8. If execution fails, read `comfyui-troubleshoot`. Report the exact node validation or execution error before proposing a mutation.
9. Record live execution state under `04_generation/comfyui/` when operating inside a story-film project.

## Done

The requested ComfyUI operation is completed or a concrete live blocker is reported with the exact next reversible action. No node, model, template, prompt ID, or output path is invented.
