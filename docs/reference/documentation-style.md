# Documentation Writing Rules

[Documentation home](../README.md) | [Up: Reference](../README.md#8-reference) | [Next: Architecture](../development/architecture.md)

## Table of contents

- [Goal](#goal)
- [Controlled English](#controlled-english)
- [ELI5 rule](#eli5-rule)
- [Page structure](#page-structure)
- [Terms](#terms)

## Goal

Documentation must be usable by a young reader, a non-native English reader, and a small local language model.

## Controlled English

Use these rules:

1. Use short sentences when possible.
2. Give one main instruction in one sentence.
3. Use the same term for the same thing.
4. Prefer common words.
5. Define technical terms before you depend on them.
6. Use active voice when it is clear who performs the action.
7. Put conditions before the instruction when the condition matters.
8. Use lists for ordered procedures.
9. Use exact filenames and commands in code blocks.
10. Avoid jokes, idioms, slang, and figurative instructions in procedures.

These rules use important ASD-STE100 controlled-English ideas. The project does not claim official ASD-STE100 certification.

## ELI5 rule

Explain the simple idea first.

Then show the technical detail.

Example:

> A context shard is a small box of project information for one part of the film. It helps the AI read only what it needs.

After that sentence, document the JSON files and commands.

## Page structure

A normal page should contain:

- links at the top;
- a table of contents;
- purpose or goal;
- procedure or explanation;
- warnings when needed;
- related links at the bottom.

## Terms

If a term can confuse a new user, link to the [Glossary](glossary.md).

## Related pages

- [Documentation home](../README.md)
- [Contributing](../development/contributing.md)
