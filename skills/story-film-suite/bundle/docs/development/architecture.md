# Architecture

[Documentation home](../README.md) | [Up: Development](../README.md#9-development-and-testing) | [Next: Testing](testing.md)

## Table of contents

- [Design goal](#design-goal)
- [Layers](#layers)
- [Sources of truth](#sources-of-truth)
- [Local-first rule](#local-first-rule)
- [Deterministic boundaries](#deterministic-boundaries)

## Design goal

Story-Film Skills must help an agent finish long creative work without trusting one huge conversation context.

## Layers

The repository has five main layers:

1. skills explain specialized behavior;
2. playbooks order skills into workflows;
3. references define durable contracts and schemas;
4. scripts perform deterministic operations;
5. project files store the real production state.

## Sources of truth

The chat is not the project database.

Durable manifests, progress state, dependency state, media state, and recovery state are the source of truth.

## Local-first rule

Creative planning must remain useful without cloud services.

Optional external runtimes are discovered when needed. Missing optional software becomes a blocker, not a fake success.

## Deterministic boundaries

Use code for facts that code can decide, such as:

- file presence;
- hashes;
- dependency edges;
- queue status;
- media probing;
- schema validation;
- completion counts;
- resumable cursors.

Use the LLM for semantic work such as story decisions, critique, writing, and creative repair.

## Character and performance state flow

Character production uses the same layered authority model:

```text
canon identity / performance / ensemble baseline
                |
story-state current condition
                |
director book and performance blocking
                |
model-neutral shot brief
                |
selected local adapter or workflow
```

A lower layer may express or stage an approved fact. It may not silently rewrite the higher layer.

## Related pages

- [Testing](testing.md)
- [Feature-scale production](../production/feature-scale.md)
- [Project layout](../reference/project-layout.md)
