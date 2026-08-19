# Portable Shooting Script Contract

`03_preproduction/shooting_script.json` is the executable planning bridge between screenplay intent and generation or physical production.

It does not replace the Fountain screenplay. It compiles approved screenplay lines, performance blocking, camera coverage, and timing into a machine-readable sequence.

## Minimum shape

```json
{
  "schema_version": 1,
  "source_screenplay": "02_screenplay/screenplay.fountain",
  "line_manifest": "02_screenplay/line_manifest.jsonl",
  "scenes": []
}
```

## Scene record

```json
{
  "scene_id": "SCN-001",
  "location_id": "LOC-001",
  "initial_positions": [],
  "units": []
}
```

## Unit record

```json
{
  "line_id": "LINE-001",
  "kind": "dialogue",
  "speaker": "CHAR-001",
  "text": "Exact screenplay dialogue.",
  "current_positions": [],
  "moves": [],
  "actions": [],
  "shot_ids": ["SHOT-001"],
  "timing": {
    "source": "estimated",
    "speech_duration_s": null,
    "planned_duration_s": 4.0
  },
  "constraints": []
}
```

Allowed `kind` values are `dialogue`, `action`, `movement`, and `transition`.

## Exactness

For dialogue units, `text` must exactly match the corresponding dialogue text in `02_screenplay/line_manifest.jsonl`. Voice cues must use the same `line_id` and exact text.

## Movement

Movement that changes character position is stored under `moves`. Gestures, posture changes, object interactions, and performance behavior go under `actions`. This prevents a future executor from confusing locomotion with expression.

## Camera

`shot_ids` reference the approved model-neutral shot briefs. Do not replace stable shot IDs with a model-specific node, workflow, camera token, or prompt fragment.

## Timing

Timing source is one of:

- `estimated`
- `measured-speech`
- `measured-media`
- `locked`

When exact speech is generated, measured speech duration should replace an estimate where it affects the action window, shot length, subtitles, or edit. Do not stretch or rewrite exact dialogue silently to fit a video duration limit.

## Portability

All file paths are project-relative. The shooting script must remain useful if the project is moved to another machine or a different renderer is chosen.
