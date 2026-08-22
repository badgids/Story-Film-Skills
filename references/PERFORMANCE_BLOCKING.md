# Performance Blocking Contract

`03_preproduction/performance_blocking.jsonl` records line or beat level staging as physical production intent.

It complements previz. Previz describes scene geometry. Performance blocking describes what performers do through time inside that geometry.

## Record

```json
{
  "line_id": "LINE-001",
  "scene_id": "SCN-001",
  "character_ids": ["CHAR-001"],
  "initial_state": {
    "posture": "standing",
    "anchor": "near-door"
  },
  "moves": [
    {
      "character_id": "CHAR-001",
      "action": "walk",
      "from": "near-door",
      "to": "table"
    }
  ],
  "actions": [
    {
      "character_id": "CHAR-001",
      "action": "looks away before answering",
      "capability_key": "turn-head"
    }
  ],
  "end_state": {
    "posture": "standing",
    "anchor": "table"
  },
  "timing": {
    "source": "estimated",
    "dialogue_duration_s": null,
    "action_window_s": null
  },
  "constraints": []
}
```

## Rules

1. Use existing `LINE-###`, `SCN-###`, and `CHAR-###` IDs.
2. Read canonical speech, movement, and stillness signatures when present. Treat them as character defaults, not mandatory gestures.
3. Read current relationship, injury, possession, and knowledge state from `story_state.json` when it affects the beat.
4. Separate movement that changes position from gestures or performance actions that do not.
5. Describe playable behavior, not abstract emotion. `looks at the exit and folds the receipt` is playable. `feels conflicted` is not enough.
6. Preserve initial and end state when the action changes posture, position, possession, or orientation.
7. When a capability registry exists, use its exact action or anchor key for hard execution constraints.
8. Do not invent an exact coordinate when a relative anchor is sufficient.
9. Dialogue timing may begin as estimated and later change to measured after voice generation.

## Complex interactions

Walking, speaking, object handling, and camera motion in one short generation may exceed the selected model or workflow. When capability status is conditional or unknown, split the action into simpler shots or explicitly mark the risk instead of pretending execution is reliable.
