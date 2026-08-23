# Story to Finished Film

[Documentation home](../README.md) | [Workflows](../README.md#2-main-workflows) | [Feature film](feature-film.md)

## Table of contents

- [Simple view](#simple-view)
- [Story work](#story-work)
- [Screenplay work](#screenplay-work)
- [Preproduction](#preproduction)
- [Generation](#generation)
- [Postproduction](#postproduction)
- [Release](#release)

## Simple view

The full path is:

```text
idea
  -> story plan
  -> story or book
  -> screenplay
  -> production plan
  -> shots and audio plans
  -> workflow selection
  -> generated media
  -> approved takes
  -> edit
  -> master
  -> delivery checks
  -> release package
```

## Story work

Start with the creative brief.

Build the story architecture.

Define characters and world rules.

Build beats and scenes.

Write the story if the project needs prose first.

## Screenplay work

Write the screenplay in Fountain format.

Create stable scene IDs.

Create stable line IDs.

Keep exact dialogue linked to production records.

## Preproduction

Build the director book.

Define production capabilities.

Create references for recurring characters, locations, props, voices, and style.

Plan performance blocking.

Design shots.

Build storyboards and previz when they help.

Run production coverage before generation.

## Generation

Prepare model-neutral briefs first.

For each required generation task, choose a complete ComfyUI workflow from the ordinary numbered catalog. Story-Film can offer bundled workflows, project defaults, saved ComfyUI workflows, templates, external sources, or a generated live-schema workflow.

The selected workflow owns its checkpoint/model, VAE, encoders, LoRAs, audio models, upscalers, nodes, and other graph settings.

Adapt prompts only as required by the selected workflow/model family.

Validate the selected ComfyUI workflow before a run.

Use resource-safe generation when the local LLM and ComfyUI models cannot fit in memory at the same time.

Keep every generated candidate traceable.

Run media QC.

Select approved takes explicitly.

## Postproduction

Build the edit plan.

Build the executable timeline.

Master the audio.

Render the film master.

Run delivery QC.

## Release

Create trailers when needed.

Create social material when needed.

Create production and release documents.

Build the release manifest and checksums.

Run the final completeness audit for a finished feature.

## Related pages

- [Feature film](feature-film.md)
- [Choose ComfyUI workflows](../generation/workflow-selection.md)
- [ComfyUI generation](../generation/comfyui.md)
- [Final completeness audit](../release/completion.md)
