# ComfyUI Portable Package Contract

Story-Film Skills does not require ComfyUI or a ComfyUI agent to be installed.

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
  "reference_manifest": "03_preproduction/references/reference_manifest.json",
  "shot_briefs": "04_generation/shot_briefs.jsonl",
  "image_briefs": "04_generation/image_briefs.jsonl",
  "voice_cues": "04_generation/voice_cues.jsonl",
  "music_cues": "04_generation/music_cues.jsonl",
  "sfx_cues": "04_generation/sfx_cues.jsonl",
  "prompt_roots": {},
  "requested_models": [],
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

- stable shot or cue ID
- model family requested
- prompt file
- reference IDs and roles
- source images, audio, or video by project-relative path
- target width, height, aspect ratio, duration, frame rate, or sample format when the project requires them
- exact dialogue or visible text
- expected output ID and destination category
- continuity preserve rules
- unresolved requirements

## What the package does not invent

Do not guess:

- ComfyUI node class names
- widget indices
- local model file paths
- API endpoints
- custom-node serialization
- another project's private workflow schema

A downstream tool can map the portable intent to its own live workflow.

## Completion rule

The handoff is complete when another tool can identify every requested generation task, its inputs, its prompt, its continuity requirements, and its expected output without reading the originating conversation.
