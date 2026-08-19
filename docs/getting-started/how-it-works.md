# How Skills and Playbooks Work

[Documentation home](../README.md) | [Up: Start here](overview.md) | [Quick start](quick-start.md)

## Table of contents

- [Skill](#skill)
- [Playbook](#playbook)
- [Project state](#project-state)
- [Validation gate](#validation-gate)
- [Dependency impact](#dependency-impact)

## Skill

A skill is a small instruction set for one kind of work.

Example skills include `write-screenplay`, `shot-design`, and `film-master`.

A small skill is easier for a small local LLM to follow.

## Playbook

A playbook is an ordered process that uses several skills.

For example, the feature-film playbook moves from story planning to screenplay, production sequences, generation, editing, and release.

## Project state

The project folder is the memory of the production.

Important facts go into JSON, JSONL, CSV, Fountain, Markdown, or media files.

Do not depend on an old chat message when a durable project file can store the fact.

## Validation gate

A gate checks whether a step is safe to complete.

If a gate fails, the pipeline stays on the current step.

The Todo can show the step as blocked.

## Dependency impact

An upstream change can make downstream work stale.

Story-Film Skills uses a dependency graph to find the smallest affected set.

Do not rebuild unrelated approved work.

## Related pages

- [Stable IDs](../reference/stable-ids.md)
- [Project folder layout](../reference/project-layout.md)
- [Architecture](../development/architecture.md)
