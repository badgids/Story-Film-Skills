# Prompt Packet Schema

Generation adapters consume model-neutral briefs.

## Shot brief JSONL

One JSON object per line:

```json
{
  "shot_id": "SHOT-001",
  "scene_id": "SCN-001",
  "line_ids": ["LINE-001"],
  "duration_seconds": 6,
  "purpose": "Reveal the hidden key in her palm without showing the guard.",
  "dramatic_job": ["advance action", "increase pressure"],
  "beat": "She proves she still has the key while pretending compliance.",
  "subjects": ["CHAR-001"],
  "location": "LOC-001",
  "continuity": {
    "wardrobe": "brown work coat, right sleeve torn at cuff",
    "props": ["PROP-002 brass key in right palm"],
    "time": "late afternoon"
  },
  "framing": "medium close-up",
  "composition": "face high frame-right, concealed hand low frame-left",
  "frame_regions": [
    {"subject_id": "CHAR-001", "region": "frame-right", "box": [0.55, 0.08, 0.95, 0.95]}
  ],
  "camera_capability_key": "push-in",
  "action_capability_keys": ["open-hand"],
  "camera": "slow push in from chest-up to hand and face",
  "movement_reason": "The push begins when her hand opens and new information becomes visible.",
  "capture_behavior": "stable exposure, deliberate focus response, restrained operator motion",
  "eye_trace": "eyes first, then right hand",
  "action": "She keeps eye contact off-screen while opening her right hand below frame line.",
  "environmental_pressure": "cold draft moves the loose cuff thread",
  "micro_action": "her thumb pins the key flat against her palm",
  "anchor": "small metallic scrape",
  "lighting": "soft window key from frame right, dim room behind",
  "dialogue": [],
  "ambience": "distant machinery and room tone",
  "music": "none",
  "sfx": ["small metal key shifts against skin"],
  "references": ["REF-001", "REF-007"],
  "lip_sync": [],
  "end_frame": null,
  "cut_intent": "cut after the key is readable but before the off-screen guard answers",
  "constraints": ["guard never visible", "no readable text"]
}
```

The extra dramaturgy fields are production intent. They are not provider syntax. They help adapters preserve why the shot exists. `capture_behavior`, `lip_sync`, and `end_frame` remain model-neutral. Use `VISIBLE_DIALOGUE_SYNC.md` for their exact contracts.

## Image brief JSONL

Use for character sheets, locations, props, keyframes, posters, storyboard frames, style boards, and approved reference assets. Include:

- stable source ID
- purpose or reference role
- subject IDs
- identity traits to preserve
- scene-state traits that may vary
- composition and crop requirements
- exact visible text only when required
- reference IDs and source roles

## Audio cue JSONL

Voice, music, and SFX cues use stable IDs and scene or shot links. Keep one creative goal per cue.

## Adapter output

Each model adapter writes a prompt file or JSON object that includes:

- source brief ID
- target model
- mode if the model has modes
- final prompt
- exact dialogue or text payload when applicable
- required references
- execution settings that belong outside prompt prose
- negative constraints only when the model supports or benefits from them

Never delete the model-neutral source brief after adaptation.

## Optional frame regions

`frame_regions` is optional screen-space production intent for multi-subject composition or workflows that support regional conditioning. A record may contain a semantic `region`, a normalized `box`, or both.

Normalized box order is `[x0, y0, x1, y1]` in the range 0 through 1, with `x0 < x1` and `y0 < y1`. Treat the box as a deliberate composition target, not a claim about what a generator will reproduce exactly.

Do not invent boxes from vague prose. Prefer semantic placement such as `frame-left`, `center`, `background-right`, or a previz-derived screen region unless exact normalized bounds are intentionally chosen. Adapters may omit the box when the target model has no meaningful spatial-conditioning control.

`camera_capability_key` and `action_capability_keys` may point into `03_preproduction/production_capabilities.json` when the production route has an explicit executable vocabulary. They are portable constraint identities, not model tokens.

## Optional visible dialogue, capture behavior, and end frame

Use `capture_behavior` for visible optical/operator behavior that must survive model adaptation without inventing a camera brand.

Use `lip_sync` only when an exact `LINE-###` must be visibly spoken by its canonical `CHAR-###` speaker. Off-screen dialogue does not require it.

Use `end_frame` only when a chained generation, last-frame-conditioned workflow, match on action, or editorial handoff needs an explicit final visual state. Subject, prop, and reference IDs must resolve.
