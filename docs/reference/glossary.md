# Glossary

[Documentation home](../README.md) | [Up: Reference](../README.md#8-reference) | [Next: Licensing](licensing.md)

## Table of contents

- [Agent](#agent)
- [Artifact](#artifact)
- [Blocker](#blocker)
- [Candidate](#candidate)
- [Capture behavior](#capture-behavior)
- [Context shard](#context-shard)
- [Drift risk](#drift-risk)
- [Dynamic register](#dynamic-register)
- [Ensemble baseline](#ensemble-baseline)
- [Dependency](#dependency)
- [Feature sequence](#feature-sequence)
- [Manifest](#manifest)
- [Movement signature](#movement-signature)
- [Performance signature](#performance-signature)
- [Primary](#primary)
- [QC](#qc)
- [Speech signature](#speech-signature)
- [Stable ID](#stable-id)
- [Stillness signature](#stillness-signature)
- [Visible dialogue sync](#visible-dialogue-sync)
- [Workflow](#workflow)

## Agent

The AI program that follows the skills and project files.

## Artifact

A file or durable project record created during production.

## Blocker

A problem that prevents safe progress.

## Candidate

A generated option that has not yet become the approved primary choice.

## Capture behavior

Visible optical and operator behavior such as focus response, exposure response, stabilization, rolling-shutter tendency, depth of field, sharpening, grain, or noise. It does not require a camera brand.

## Context shard

A small working set for one feature sequence. It keeps the agent from loading the full film state.

## Drift risk

A recurring generation failure recorded on a reference asset, such as mirrored scars or changing hair length. A drift risk is not canon.

## Dynamic register

An optional semantic description of scene energy: restrained, responsive, kinetic, or extreme. It never forces camera movement.

## Ensemble baseline

The canonical normal or starting behavior between two recurring characters. Current changed relationship state belongs in `story_state.json`.

## Dependency

A relationship where one item depends on another item. A change upstream can make downstream work stale.

## Feature sequence

A manageable production unit with a `SEQ-###` ID. It contains one or more screenplay scenes.

## Manifest

A structured file that lists production items and their state.

## Movement signature

A recurring character's normal gait, gesture quality, body carriage, habitual physical actions, and pressure changes.

## Performance signature

The canonical combination of speech, movement, and stillness behavior used as a character default across writing and production.

## Primary

The approved main media choice for an item.

## QC

Quality control. QC checks measurable evidence such as file validity, duration, streams, or declared constraints.

## Speech signature

A recurring character's canonical cadence, register, vocabulary behavior, habits, and pressure changes. It is separate from acoustic TTS voice identity.

## Stable ID

A durable identifier such as `SHOT-014` or `SEQ-003`.

## Stillness signature

A recurring character's recognizable posture, hands, gaze, breath, and resting behavior when not moving through the space.

## Visible dialogue sync

A model-neutral requirement that an exact screenplay line be visibly spoken by its canonical speaker with explicit visibility, timing, and cut intent.

## Workflow

A defined process. For ComfyUI, a workflow is also the executable node graph submitted to the server.

## Related pages

- [Stable IDs](stable-ids.md)
- [How Story-Film works](../getting-started/how-it-works.md)
