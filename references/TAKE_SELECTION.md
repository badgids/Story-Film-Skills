# Take Selection Contract

Generation and approval are separate stages.

`04_generation/take_manifest.jsonl` records every candidate that matters. `04_generation/selections.json` records the currently approved take for each shot.

## Take record

```json
{
  "take_id": "TAKE-001",
  "shot_id": "SHOT-001",
  "prompt_id": "",
  "path": "04_generation/comfyui/outputs/example.mp4",
  "status": "candidate",
  "source": "comfyui",
  "assessment": {
    "identity": "",
    "action": "",
    "composition": "",
    "motion": "",
    "continuity": "",
    "technical": "",
    "cut_fit": ""
  },
  "rejection_reason": ""
}
```

Allowed statuses are `candidate`, `selected`, `rejected`, and `superseded`.

A take ID is stable. Regeneration creates a new take, even when it uses the same prompt or seed.

## Selection record

```json
{
  "schema_version": 1,
  "shots": {
    "SHOT-001": {
      "selected_take_id": "TAKE-001",
      "reason": "",
      "alternates": []
    }
  }
}
```

## Selection order

Reject hard failures first:

1. wrong identity or required object
2. action contradicts the shot
3. continuity break that cannot be edited around
4. unusable corruption, timing, audio, or framing defect

Then compare viable takes on:

- dramatic job
- performance and readable intention
- composition and eye trace
- motion quality and physical plausibility
- cut compatibility with adjacent selected shots
- sound/dialogue sync when relevant

Do not select a take because it is newest, largest, slowest to generate, or most expensive.

## Multiple takes

Generate multiple takes only when the expected value justifies the cost: pivotal performance, fragile continuity, uncertain motion, a disputed visual choice, or a user request for alternatives.

For routine coverage with an already approved result, do not create variants merely to fill a quota.

## Replacement

When a new take replaces an approved take:

- keep the old take record
- mark its status `superseded`
- update `selections.json`
- check adjacent cut continuity
- mark downstream editorial artifacts stale if the replacement changes timing, dialogue, action, or sound
