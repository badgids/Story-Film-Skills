# What Story-Film Skills Is

[Documentation home](../README.md) | [Next: Install](install.md)

## Table of contents

- [Purpose](#purpose)
- [What it can make](#what-it-can-make)
- [How it stays reliable](#how-it-stays-reliable)
- [What it does not promise](#what-it-does-not-promise)

## Purpose

Story-Film Skills is a local-first set of Agent Skills.

It gives an AI agent a repeatable way to make creative projects.

The system stores important decisions in files. It does not depend on chat memory alone.

## What it can make

The system can help create:

- stories
- novels and novellas
- screenplays
- character and world bibles
- storyboards
- image prompts and image assets
- dialogue and voice plans
- music and sound plans
- video shots
- short films
- feature films
- trailers
- social media material
- release packages
- production documents

## How it stays reliable

Story-Film Skills uses stable IDs such as `SCN-001`, `SHOT-001`, and `SEQ-001`.

It writes durable state to the project folder.

It validates important files before the pipeline moves forward.

It can stop on a blocker instead of pretending that work is complete.

It can split a feature film into small sequence shards. This keeps the AI context small.

It can unload a local LLM before large ComfyUI models use the same RAM or VRAM.

## What it does not promise

A passing validator does not prove that a story is good.

A passing health report does not prove that acting is good.

A generated master does not prove that a film is complete.

The final completeness audit checks production evidence. A human still decides whether the final creative result is acceptable.

## Related pages

- [Install Story-Film Skills](install.md)
- [How the system works](how-it-works.md)
- [Feature-film workflow](../workflows/feature-film.md)
