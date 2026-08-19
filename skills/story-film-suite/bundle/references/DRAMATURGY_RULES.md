# Dramaturgy Rules

Use this layer before model syntax, lenses, or prompt polish. A technically valid prompt is still a bad shot when the scene has no dramatic engine.

## Scene engine

Before shot design, state five things in plain language:

1. **Immediate desire.** What does the viewpoint character want in this scene right now?
2. **Obstacle.** What blocks that desire now?
3. **Geometry.** Where are the character, obstacle, threat, exit, and important object in relation to one another?
4. **Gaze.** Where should the audience look first, then next?
5. **Rhythm.** Where should the scene hold, accelerate, pause, and cut?

If one is unknown, fix the scene plan before writing shots.

## Every shot has a job

A shot must do at least one of these jobs:

- change the emotional or power relationship
- advance action or reveal useful information
- increase or release pressure

Delete a shot that does none of them unless the user explicitly requires it for a practical production reason.

## Concrete detail triad

For each important shot, specify:

- **environmental pressure:** one physical fact in the location that affects the scene
- **micro-action:** one observable body or object action that carries the performance
- **anchor:** one sound, object, color, reflection, texture, or recurring visual element that helps bind the scene

Do not replace these with words such as "cinematic", "epic", "powerful", or emotion labels.

## Motivated camera

Every camera move answers `what changed?`

Valid reasons include:

- a decision changed the scene
- new information entered the frame
- a look motivates a reveal
- pressure increased and framing must tighten
- a physical action must remain readable
- the spatial relationship changed

If nothing changed, prefer a locked camera.

## Spatial clarity

For action, suspense, comedy, or dialogue, keep these readable:

- hero or viewpoint subject
- obstacle or threat
- exit or goal direction
- screen direction
- eyelines
- axis of action

Break continuity deliberately only when the audience benefit is stated.

## Cut priority

When two cut points are possible, prefer the one that best serves this order:

1. emotional truth
2. story information
3. rhythm
4. eye trace
5. screen plane continuity
6. physical geography

Fast cutting is not a goal by itself.

## Sequence anchors

For a short sequence, name a small set of anchors before generating shots:

- dominant dramatic feeling
- recurring visual or sound motif
- important object or physical focus
- break, reversal, or decision
- final image or final sound

Do not keep adding motifs after the sequence already has enough to be legible.

## Shot card minimum

A production shot card should resolve:

- stable shot ID
- scene ID
- dramatic job
- beat or change
- framing and composition
- subject positions
- camera behavior
- movement reason
- eye trace
- physical action
- environmental pressure
- micro-action
- duration
- cut intent
- sound
- lighting logic
- continuity state
- references
- production note or generation constraint

A blank field is either a missing decision or a field that should be explicitly marked not applicable.

## Gate

Do not send a shot or generation prompt downstream until:

- the scene engine is complete
- every planned shot has a job
- every camera move is motivated
- geography is readable
- key shots have concrete physical detail
- the sequence has a deliberate ending image or sound
