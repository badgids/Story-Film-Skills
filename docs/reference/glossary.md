# Glossary

[Documentation home](../README.md) | [Up: Reference](../README.md#8-reference) | [Next: Licensing](licensing.md)

## Table of contents

- [Agent](#agent)
- [Artifact](#artifact)
- [Blocker](#blocker)
- [Candidate](#candidate)
- [Context shard](#context-shard)
- [Dependency](#dependency)
- [Feature sequence](#feature-sequence)
- [Manifest](#manifest)
- [Primary](#primary)
- [QC](#qc)
- [Stable ID](#stable-id)
- [Workflow](#workflow)

## Agent

The AI program that follows the skills and project files.

## Artifact

A file or durable project record created during production.

## Blocker

A problem that prevents safe progress.

## Candidate

A generated option that has not yet become the approved primary choice.

## Context shard

A small working set for one feature sequence. It keeps the agent from loading the full film state.

## Dependency

A relationship where one item depends on another item. A change upstream can make downstream work stale.

## Feature sequence

A manageable production unit with a `SEQ-###` ID. It contains one or more screenplay scenes.

## Manifest

A structured file that lists production items and their state.

## Primary

The approved main media choice for an item.

## QC

Quality control. QC checks measurable evidence such as file validity, duration, streams, or declared constraints.

## Stable ID

A durable identifier such as `SHOT-014` or `SEQ-003`.

## Workflow

A defined process. For ComfyUI, a workflow is also the executable node graph submitted to the server.

## Related pages

- [Stable IDs](stable-ids.md)
- [How Story-Film works](../getting-started/how-it-works.md)
