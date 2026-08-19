# Production Capability Contract

`03_preproduction/production_capabilities.json` records what the current production approach can actually perform or reliably attempt. It is a project-specific constraint surface, not a frozen model catalog.

## Why it exists

A weak agent should not choose an action, camera move, location setup, duration, or synchronization method merely because the term exists in film vocabulary. Planning must distinguish:

- available
- unavailable
- unknown
- available with risk or conditions

This prevents plans such as a tracking shot when the selected workflow cannot move the camera, or a walk-and-talk shot when the chosen generator cannot reliably coordinate both actions.

## Minimum shape

```json
{
  "schema_version": 1,
  "source": "declared",
  "locations": {},
  "blocking_anchors": {},
  "actions": {},
  "camera_behaviors": {},
  "audio": {},
  "generation": {},
  "constraints": [],
  "unknowns": []
}
```

## Capability record

A capability may use:

```json
{
  "status": "available",
  "conditions": [],
  "limits": {},
  "evidence": "user instruction, live discovery, tested workflow, or approved production plan",
  "notes": ""
}
```

Allowed status values:

- `available`
- `unavailable`
- `conditional`
- `unknown`

## Locations and blocking anchors

Locations use existing `LOC-###` IDs when the location is part of canon. A fixed set or virtual environment may expose named anchors such as `near-door`, `sofa-left`, or `counter-A`. Generated-video projects may leave anchors descriptive rather than inventing exact coordinates.

## Actions

Action keys should be concrete and playable, for example `walk`, `sit`, `turn-head`, `reach`, `pick-up`, or `argue-with-hands`. Record whether the action changes position and whether it can be combined reliably with dialogue or another action.

## Camera behaviors

Record shot or movement capabilities such as `static`, `pan`, `push-in`, `track`, `orbit`, or `handheld-follow`. Conditions may include required subject movement, first-frame guidance, path constraints, or maximum practical duration.

## Audio and timing

Record whether the selected production route can provide:

- exact speech audio
- measured speech duration
- lip sync
- synchronized generated audio
- separate dialogue and ambience stems
- subtitle timing

Do not assume that a video model with audio support provides exact dialogue or usable lip sync.

## Live discovery

When ComfyUI is used, live node and model discovery proves that technical components exist. The creative capability registry still records what the chosen workflow has been verified to do. Installed nodes do not automatically prove a production capability.

## Mutation rule

Changing the selected model, workflow, virtual set, or generation route may stale this file. Run `project-impact` before reusing blocking or shooting-script decisions that depended on changed capabilities.
