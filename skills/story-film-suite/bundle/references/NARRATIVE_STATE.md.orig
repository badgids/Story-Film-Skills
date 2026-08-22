# Narrative State Contract

Story state must be recoverable from project files without rereading the whole manuscript or relying on chat memory.

`01_story/story_state.json` is the compact machine-readable ledger for facts that change over time. Canon defines what is true in the project. Story state records when mutable facts become true, stop being true, or remain unresolved.

## Minimum shape

```json
{
  "schema_version": 1,
  "scene_order": [],
  "characters": {},
  "props": {},
  "questions": {},
  "promises": {},
  "events": []
}
```

## Stable IDs

Use these additional stable IDs:

- `QST-###`: a question the audience or a character is waiting to have answered
- `PROM-###`: a setup, expectation, commitment, warning, clue, or dramatic promise that needs later handling
- `TAKE-###`: one generated candidate for a planned `SHOT-###`

Do not recycle IDs after an item is resolved, rejected, or superseded.

## Character state

A character entry may contain:

```json
{
  "life_state": "alive",
  "death_scene": null,
  "current_location": "LOC-001",
  "injuries": [],
  "possessions": [],
  "knowledge": {},
  "relationships": {}
}
```

Allowed life states are `alive`, `dead`, `unknown`, and `not-yet-introduced`.

Knowledge belongs to the character, not to the narrator. Store concise facts as keys or records with the scene where the character learned them. A character simulation or dialogue pass may use only knowledge available at the requested story moment.

## Prop state

A prop entry may contain:

```json
{
  "owner": "CHAR-001",
  "location": "LOC-001",
  "condition": "unbroken",
  "status": "active",
  "last_changed_in": "SCN-003"
}
```

Allowed statuses are `active`, `lost`, `destroyed`, `consumed`, `hidden`, and `unknown`.

## Questions

A question entry records an information gap that matters to a reader, viewer, or character.

```json
{
  "text": "Who copied the key?",
  "introduced_in": "SCN-002",
  "status": "open",
  "resolved_in": null,
  "answer": null,
  "audience_knows": false
}
```

Allowed statuses are `open`, `partially-answered`, `resolved`, `abandoned`, and `intentional-open-ending`.

A resolved question may not resolve before it is introduced in `scene_order`.

## Promises

A promise is broader than a mystery question. It may be a planted object, a threat, a relationship expectation, a declared plan, a genre expectation, or foreshadowing that creates a reasonable expectation of later consequence.

```json
{
  "text": "The cracked pressure gauge will matter during the dive.",
  "setup_in": "SCN-004",
  "status": "open",
  "payoff_in": null,
  "payoff": null,
  "target": "before climax"
}
```

Allowed statuses are `open`, `paid`, `subverted`, `cancelled`, and `intentionally-unpaid`.

A paid or subverted promise may not have a payoff before its setup in `scene_order`.

## Events

Events make presence and chronology explicit without trying to encode the whole story twice.

```json
{
  "scene_id": "SCN-005",
  "order": 5,
  "active_characters": ["CHAR-001"],
  "mentions": ["CHAR-003"],
  "flashback": false,
  "state_changes": []
}
```

Use `mentions` for recordings, memories, photographs, dialogue references, corpses, or other non-active appearances when that distinction matters. A character who died in an earlier scene may not appear in `active_characters` later unless the later event is explicitly a flashback or another chronology exception.

## Update discipline

Update this ledger after a chapter or screenplay scene settles, not while brainstorming alternatives. Write only changed state. Do not promote a possibility into state because an agent suggested it.

When a revision moves, deletes, or rewrites a scene, update `scene_order`, affected question/promise records, character state, prop state, and event records before declaring continuity clean.

## What the deterministic validator can prove

It can check structural facts such as:

- ID and status validity
- duplicate scene order
- question resolution before introduction
- promise payoff before setup
- active appearances after a recorded death when no flashback is marked
- selected takes that reference missing or mismatched shot/take records

It cannot prove character motivation, thematic coherence, suspense quality, or whether a payoff is emotionally satisfying. Those require creative review.
