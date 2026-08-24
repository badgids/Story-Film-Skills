---
name: minimax-h3
description: "Adapt Story-Film shot briefs into MiniMax H3 audio-video prompts using the mandatory H3 prompt-writing format plus an appropriate optional style skill for T2VA, I2VA, FL2VA, L2VA, or Ref2VA."
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# MiniMax H3 Prompting

## Required skill stack

Every MiniMax H3 prompt uses this stack in order:

1. Story-Film canon, continuity, reference authority, approved dialogue/audio, and the source shot brief.
2. The selected ComfyUI workflow, which determines the H3 mode and actual runtime capabilities.
3. `skills/h3-prompt-writing/SKILL.md`, which is mandatory and controls final H3 field names, keyframe alignment, shot timing, speaker/dialogue syntax, and base-versus-Ref2VA section order.
4. Zero or one automatically selected H3 style skill from `references/MINIMAX_H3_SKILL_ROUTING.md`. Use more than one only when the user explicitly asks for a hybrid.
5. This Story-Film adapter's project-specific continuity, exact-audio, reference-scope, and capture constraints.

Run `python scripts/minimax_h3_skill_router.py --text "<brief>"` as the deterministic first-pass style route. An explicit user selection of one of the eight style skills overrides automatic classification.

A style skill enriches content. It never replaces `h3-prompt-writing`, never changes the selected workflow, and never overrides Story-Film canon or reference authority.

## Prompt audit metadata

Store these values in the Story-Film prompt file outside the final model prompt:

```text
adapter: minimax-h3
h3_base_skill: h3-prompt-writing
h3_style_skill: <selected-style-skill-or-none>
```

The generation operator sends only the final H3 prompt body to the model.

## Select mode

- `T2VA`: text to audio-video
- `I2VA`: start from a supplied first frame
- `FL2VA`: connect supplied first and last frames
- `L2VA`: converge to a supplied last frame
- `Ref2VA`: full-reference generation using labeled image, video, and audio references

Use the mode actually implemented by the selected workflow. Do not infer FL2VA/L2VA support merely because a last-frame asset exists.

## Base mode output

Read `skills/h3-prompt-writing/references/base-en.txt`.

Preserve this core order:

1. `integrated_multimodal_description`
2. `overall_soundscape`
3. `non_diegetic_music`

I2VA, FL2VA, and L2VA also require the correct alignment instruction before the core fields. Build a chronological audiovisual timeline. `[Shot 1]` has no cut timestamp; later cuts use strictly increasing `At MM:SS.mmm` times.

## Ref2VA output

Read `skills/h3-prompt-writing/references/ref-en.txt`.

Preserve this order:

1. `subject_definitions`
2. `summary`
3. `retention_analysis`
4. `detailed_description`
5. `overall_soundscape`
6. `non_diegetic_music`

Use stable `<Subject N>`, `<Picture N>`, `<Video N>`, and `<Audio N>` labels. State exactly what is retained from each reference and where it appears.

## Story-Film rules

- Preserve dialogue, lyrics, and visible scene text exactly in the requested/source language.
- Use stable `(S1)`, `(S2)`, and later speaker IDs and H3 `<d>[Language] ...</d>` blocks.
- When the source brief requires visible-dialogue sync, preserve exact speaker, mouth visibility, cut policy, and measured speech duration.
- Keep reference labels consistent and preserve Story-Film reference authority scopes. A character atlas is not automatically composition authority and a temporal tail is not identity authority.
- Tie first or last frames to the timeline explicitly in keyframe modes. When `end_frame.required` is present, end the described timeline in that state and use FL2VA/L2VA only when the selected local workflow actually uses last-frame conditioning.
- For Ref2VA continuation, a registered visual-only previous-shot tail may carry temporal continuity. Its audio must be stripped before it becomes a visual reference.
- When approved dialogue audio exists, preserve model-neutral seconds and the exact approved source. If live ComfyUI exposes `MiniMaxH3TimedAudio` and `MiniMaxH3ExactAudioLock`, the optional exact-audio profile may convert start seconds to H3's 24 fps target timeline and pair the lock with core `MiniMaxH3AddGuide` at the same frame. If those nodes are absent, report the capability as unavailable; never install them silently.
- Preserve source `capture_behavior` as visible capture properties rather than inventing camera hardware.
- Use concrete image and sound descriptions instead of generic quality adjectives.
- A style overlay must not invent brand facts, dialogue, lyrics, scientific claims, character identity, reference roles, or continuity facts.
- Save under `04_generation/prompts/minimax-h3/<shot-id>.md`.

## Done

The prompt file records its H3 base/style routing, all references resolve, H3 section order and syntax are correct, and described audiovisual time equals the requested duration.
