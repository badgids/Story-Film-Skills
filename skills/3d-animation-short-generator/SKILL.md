---
name: 3d-animation-short-generator
description: "Adapt MiniMax H3 prompts for stylized 3D narrative animation with locked character identity, environment continuity, readable acting, per-shot timing, physical action, camera, and audio continuity."
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# 3D Animation Short Generator

Story-Film portability adaptation of MiniMax's Hub-oriented 3D animation skill. Use it as a narrative-animation prompt overlay.

## Use when

Use for stylized 3D animated shorts where character consistency, scene continuity, performance, and multi-shot timing matter. Do not auto-use for photorealistic live action or a generic isolated clip.

## H3 prompt overlay

- Lock each character's silhouette, proportions, costume, signature props, and do-not-change identity traits from Story-Film reference assets.
- Lock scene landmarks and spatial anchors so shots preserve geography.
- Give each shot an explicit continuity handoff from the previous shot and an intended end state for the next.
- Describe animation performance through readable poses, anticipation, follow-through, expression changes, eye focus, body mechanics, and clear line of action.
- Keep stylization coherent across shots. Do not let a style preset overwrite project visual-bible authority.
- Each generated H3 clip must have a complete time-bounded action, camera path, dialogue/audio timing, and continuity result.
- For a film longer than H3's single-clip duration, generate shot-sized clips and use Story-Film temporal continuity and editorial assembly rather than asking H3 for an overlong clip.

## H3 handoff

`h3-prompt-writing` controls final H3 syntax. `minimax-h3` controls Story-Film reference, dialogue, audio, and temporal constraints.
