---
name: music-video-subtitle-generator
description: "Adapt MiniMax H3 prompts for music videos with locked master audio, exact lyrics, beat-aware shot timing, spatial lyric typography, performance continuity, and multi-clip stitching when duration exceeds one H3 generation."
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Music Video Subtitle Generator

Use for music videos or emotional music shorts where lyrics, beat, performance, typography, references, and camera language must be designed together.

## Prompt overlay

- User-provided music is the master music bed unless replacement is explicitly requested.
- User-provided lyrics are locked. Do not rewrite, translate, expand, or paraphrase them unless explicitly requested.
- Visible lyric typography must exactly match the performed phrase.
- Treat typography as a spatial visual layer, not an automatic lower-third subtitle bar. Keep it away from eyes and critical mouth visibility.
- Map shots, cuts, gestures, typography events, and transitions to real lyric/beat timing.
- Keep character, scene, and typography reference roles separate.
- For target duration beyond H3's single-generation range, split into shot-sized H3 clips, preserve one master-audio timeline, use tail/head continuation where appropriate, and cut on musically coherent boundaries.
- Do not cut through an active lyric unless continuity is intentionally designed and preserved.
- Preserve Story-Film approved dialogue/audio authority and measured timing over any preset rhythm suggestion.

## H3 handoff

Use `h3-prompt-writing` to encode each H3 clip. Long-form stitching remains a Story-Film editorial task, not a request for one overlong H3 prompt.
