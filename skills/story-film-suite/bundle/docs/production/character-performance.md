# Character Performance

[Documentation home](../README.md) | [Up: Production](../README.md#3-feature-film-production)

## Table of contents

- [Speech signature](#speech-signature)
- [Movement signature](#movement-signature)
- [Stillness signature](#stillness-signature)
- [Ensemble baseline](#ensemble-baseline)
- [Production flow](#production-flow)
- [Related pages](#related-pages)

Story-Film can keep a recurring character recognizable by behavior as well as appearance.

## Speech signature

Speech describes how the character tends to speak: cadence, vocabulary, pause behavior,
volume, habits, and changes under pressure.

It is not the same as a TTS voice. Audible timbre, accent, clone audio, and voice model
settings belong in the voice bible and voice cues.

## Movement signature

Movement describes recurring physical behavior such as gait, gesture scale, body carriage,
and habitual actions.

It is a default. A scene can deliberately break it when the story gives the performer a reason.

## Stillness signature

Stillness describes what the character does when not moving through the space: posture,
hands, gaze, breathing, resting expression, and how the character occupies silence.

A still performer does not need filler gestures.

## Ensemble baseline

A relationship baseline records how two recurring characters normally share a room, divide
leadership, use proximity, and handle conflict.

Current trust, hostility, power, and other changed relationship state belong in
`01_story/story_state.json`.

## Production flow

```text
canon character profile
        |
story-state current condition
        |
director book
        |
performance blocking
        |
shot brief
        |
local model adapter or local workflow
```

The downstream production plan may adapt a behavior to the scene. It may not silently
rewrite canonical identity.

## Related pages

- [Build a story bible](../workflows/story-bible.md)
- [Visible dialogue synchronization](dialogue-sync.md)
- [Sequences and context shards](sequences-and-shards.md)
