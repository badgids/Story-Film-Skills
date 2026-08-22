# Visible Dialogue Synchronization Contract

Story-Film can require an exact screenplay line to be visibly spoken by a specific character without depending on one video model, provider, or lip-sync implementation.

This contract describes production intent. Adapters and local workflows translate the intent into the controls they actually support.

## When to use it

Use visible-dialogue synchronization only when the viewer must see the speaker deliver the line.

Do not mark ordinary off-screen dialogue, voice-over, radio speech, phone audio from an unseen caller, narration, or deliberately obscured speech as lip-sync required.

## Shot brief record

`04_generation/shot_briefs.jsonl` may contain:

```json
{
  "lip_sync": [
    {
      "line_id": "LINE-018",
      "speaker_id": "CHAR-002",
      "required": true,
      "mouth_visibility": "required",
      "cut_policy": "hold-through-line",
      "timing_source": "measured-speech",
      "speech_duration_s": 2.42,
      "occlusion_constraints": ["mouth unobstructed"]
    }
  ]
}
```

Allowed `mouth_visibility` values:

- `required`
- `preferred`
- `not-required`

Allowed `cut_policy` values:

- `hold-through-line`
- `cut-allowed`
- `not-applicable`

Allowed `timing_source` values reuse the shooting-script contract:

- `estimated`
- `measured-speech`
- `measured-media`
- `locked`

`measured-speech`, `measured-media`, and `locked` require a positive `speech_duration_s`.

## Exactness

`line_id` must resolve to a dialogue `LINE-###` record.

`speaker_id` must match the line manifest speaker.

Do not paraphrase exact dialogue to make a visual generation easier. If the line cannot fit the intended duration, change coverage, split the production unit, or route the problem upstream.

## Visibility

When `required` is true, the speaker must be one of the shot subjects.

`mouth_visibility: required` means the planned composition must give the downstream route a reasonable view of the speaking mouth. It does not require a specific shot size in the universal contract because different performances and renderers have different needs.

Occlusion constraints record project-specific requirements such as an unobstructed mouth or no hand crossing the lower face during the line.

## Cutting

`hold-through-line` means the visible delivery is intended to remain in one covering shot for the line.

`cut-allowed` permits editorial coverage changes while preserving exact speech timing and speaker continuity.

This field is production intent. It does not force an adapter to invent an internal cut inside one generated clip.

## Timing

Use estimated timing before measured speech exists. When a generated or recorded voice cue has measured duration, propagate that duration into the shooting script and relevant shot sync record.

A hold-through-line sync requirement cannot fit a shot whose usable duration is shorter than the measured line unless the production plan explicitly changes.

## Shooting script

A dialogue unit may carry the same `lip_sync` array. The shooting script is the portable execution compilation; covering shots must preserve the matching required line and speaker.

## Production coverage

A required visible-dialogue line is covered only when:

- the exact dialogue line resolves
- the speaker resolves and matches the line manifest
- the shooting-script unit carries the requirement
- at least one covering shot carries the matching requirement
- required visible speakers are shot subjects
- measured timing is internally compatible

The deterministic coverage gate can prove those links. It cannot prove that generated mouth motion is visually convincing. That requires media QC after generation.

## End-frame continuity

A shot may also contain an optional `end_frame` object when the exact visual endpoint matters to a chained generation, match on action, last-frame-conditioned workflow, or editorial handoff.

Example:

```json
{
  "end_frame": {
    "required": true,
    "subjects": [
      {
        "subject_id": "CHAR-001",
        "region": "frame-left",
        "state": "standing with right hand on the door latch",
        "gaze": "frame-right"
      }
    ],
    "props": [
      {
        "prop_id": "PROP-004",
        "state": "held in right hand"
      }
    ],
    "camera_state": "medium close-up, camera settled",
    "continuity_handoff": "door fully closed; hand remains on latch",
    "reference_id": null
  }
}
```

Do not require an end-frame record for shots whose ending state does not need special continuity control.
