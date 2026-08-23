# ComfyUI Portable Package Contract

Story-Film Skills does not require ComfyUI or a ComfyUI agent to be installed for planning.

This contract defines a portable project-relative package that can later be consumed by ComfyUI, another agent, a workflow compiler, or a human operator.

## Output

Write `04_generation/comfyui_handoff.json`.

Minimum shape:

```json
{
  "schema_version": 1,
  "producer": "Story-Film Skills",
  "project_title": "Example",
  "source_state": "00_project/state.json",
  "canon": "00_project/canon.json",
  "workflow_preferences": "00_project/workflow_preferences.json",
  "workflow_catalog": "00_project/comfyui_workflow_catalog.json",
  "reference_manifest": "03_preproduction/references/reference_manifest.json",
  "shot_briefs": "04_generation/shot_briefs.jsonl",
  "image_briefs": "04_generation/image_briefs.jsonl",
  "voice_cues": "04_generation/voice_cues.jsonl",
  "music_cues": "04_generation/music_cues.jsonl",
  "sfx_cues": "04_generation/sfx_cues.jsonl",
  "prompt_roots": {},
  "requested_workflows": {},
  "required_inputs": [],
  "expected_outputs": [],
  "stale_ids": [],
  "sequence_scope": [],
  "unresolved_requirements": [],
  "notes": []
}
```

All paths are project-relative.

## What the package owns

The package may specify:

- stable shot or cue ID;
- the selected workflow task/category;
- the durable selected workflow identity or materialized project-relative workflow path;
- prompt file;
- reference IDs and roles;
- source images, audio, or video by project-relative path;
- target width, height, aspect ratio, duration, frame rate, or sample format when required by the production plan;
- exact dialogue or visible text;
- expected output ID and destination category;
- continuity preserve rules;
- unresolved requirements.

The selected workflow itself owns its concrete checkpoint/model, VAE, text encoders, LoRAs, audio models, upscalers, nodes, samplers, schedulers, and other graph settings.

## What the package does not invent

Do not guess:

- a replacement workflow when the user selected another one;
- ComfyUI node class names that are not in a selected workflow or live schema;
- widget indices;
- personal machine paths;
- API endpoints;
- custom-node serialization;
- another project's private workflow schema.

A downstream tool can materialize the selected workflow, stage the current project inputs, and validate it against its live ComfyUI server.

## Completion rule

The handoff is complete when another tool can identify every requested generation task, its selected workflow or unresolved workflow requirement, its inputs, prompt, continuity requirements, and expected output without reading the originating conversation.
