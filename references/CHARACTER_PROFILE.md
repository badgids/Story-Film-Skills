# Character Profile Contract

Story-Film keeps rich human-facing character development in `01_story/characters.md` and only durable identity and performance facts in `00_project/canon.json`.

The goal is not to encode a complete biography. The goal is to preserve the facts that later writing, directing, reference creation, voice work, blocking, and generation must not reconstruct from chat.

## Human-readable character section

For each consequential `CHAR-###`, prefer these sections when relevant:

- story function
- objective
- fear or limit
- contradiction
- pressure behavior
- canonical identity
- speech signature
- movement signature
- stillness signature
- relationships and ensemble behavior
- private knowledge
- behaviorally relevant backstory
- arc start and target
- open decisions

Work one consequential character at a time when project scope is large or the active model is small. Resolve function and present behavior before expanding biography.

## Canonical character record

Existing character records remain valid. A richer record may add:

```json
{
  "name": "Mara Vale",
  "identity": {
    "physical_identifiers": ["short ash-brown hair", "scar below left eye"],
    "must_preserve": ["scar below left eye"],
    "must_not_be": ["scar on right side"],
    "may_vary": ["expression", "temporary dirt", "scene wardrobe"]
  },
  "performance_signature": {
    "speech": {
      "register": "low",
      "texture": "dry",
      "cadence": "deliberate",
      "volume": "quiet",
      "vocabulary": "plainspoken and precise",
      "habits": ["brief pause before direct refusals"],
      "pressure_changes": ["sentences shorten under threat"],
      "must_not_do": []
    },
    "movement": {
      "gesture_quality": "economical",
      "body_carriage": "grounded and contained",
      "gait": "deliberate",
      "habitual_actions": ["keeps hands close to body while listening"],
      "pressure_changes": ["movement becomes faster but not larger"],
      "must_not_do": []
    },
    "stillness": {
      "posture": "weight centered",
      "hands": "usually occupied or loosely closed",
      "gaze": "watches the speaker without constant eye movement",
      "breath": "controlled",
      "resting_expression": "watchful",
      "habits": [],
      "pressure_changes": [],
      "must_not_do": []
    }
  }
}
```

All fields are optional. Add only facts supported by approved project decisions.

## Identity rules

`must_preserve` contains canonical traits that cannot drift without a canon change.

`must_not_be` contains explicit canonical exclusions. Use it when the wrong version is likely to be mistaken for the character or when a mirrored/reversed trait would break identity.

`may_vary` contains traits that can legitimately change by scene or production choice.

Do not turn an observed generation failure into canon. Put repeated renderer failures in the reference manifest as `drift_risks`.

## Speech signature

Speech describes character writing and performance behavior, not an audio model preset. It may include register, cadence, vocabulary, habitual phrasing, default volume, pause behavior, and changes under pressure.

Acoustic identity such as timbre, audible age, accent, and clone/reference audio belongs in the voice bible and voice cues.

## Movement signature

Movement describes recurring physical behavior such as gait, gesture scale, body carriage, habitual actions, and how movement changes under pressure.

It is a default, not a cage. A scene may intentionally depart from it when the story provides a reason.

## Stillness signature

Stillness describes recognizable behavior when the character is not locomoting. It may include posture, hands, gaze, breath, resting expression, and how the character occupies silence.

Do not add meaningless gestures simply because a performer is otherwise still.

## Relationship baselines

`canon.json` may contain `relationship_baselines` for recurring pair behavior.

Use a canonical sorted pair key:

```json
{
  "relationship_baselines": {
    "CHAR-001::CHAR-002": {
      "characters": ["CHAR-001", "CHAR-002"],
      "room_shape": "Mara fills practical silence; Elias allows emotional silence to remain.",
      "leadership": "Mara leads physical decisions; Elias leads technical decisions.",
      "proximity": "comfortable working distance",
      "conflict_pattern": "neither raises their voice until trust is challenged",
      "notes": ""
    }
  }
}
```

This is the normal or starting ensemble pattern. It is not the current relationship after story events change it.

## Mutable relationship and psychology state

Current trust, hostility, allegiance, knowledge, injury, possession, and other chronology-sensitive conditions belong in `01_story/story_state.json`.

Preferred relationship state:

```json
{
  "relationships": {
    "CHAR-002": {
      "state": "guarded trust",
      "power_balance": "CHAR-002 controls access to the evidence",
      "last_changed_in": "SCN-014",
      "notes": ""
    }
  }
}
```

Legacy string relationship values remain valid.

Do not place a temporary emotional state in canon merely because it matters strongly in one scene or act.

## Downstream use

- screenplay and prose use speech and relationship behavior without copying biography into dialogue
- director book uses movement, stillness, ensemble baseline, and current state
- performance blocking uses the signatures as defaults, then records scene-specific action
- dialogue voice uses speech behavior while separately defining acoustic voice identity
- reference assets use canonical identity locks and exclusions
- shot design uses current story state and visible performance requirements
- model adapters consume the model-neutral shot and voice briefs, not the canon record directly when a compiled brief already exists

## Unknowns

Do not invent detailed canon to fill an empty field. Use an existing open decision or create a durable `DEC-###` when the missing choice matters to the requested endpoint.
