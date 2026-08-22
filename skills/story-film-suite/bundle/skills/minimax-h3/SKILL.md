---
name: minimax-h3
description: Adapt shot briefs into MiniMax H3 audio-video prompts for T2VA, I2VA, FL2VA, L2VA, or Ref2VA with synchronized visual timeline, soundscape, music, and reference alignment.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# MiniMax H3 Prompting

## Select mode

- `T2VA`: text to audio-video
- `I2VA`: start from a supplied first frame
- `FL2VA`: connect supplied first and last frames
- `L2VA`: converge to a supplied last frame
- `Ref2VA`: full-reference generation using labeled image, video, and audio references

## Base mode output

Preserve this order:

1. `integrated_multimodal_description`
2. `overall_soundscape`
3. `non_diegetic_music`

Build a chronological audiovisual timeline. State composition, subjects, environment, action, camera, dialogue, effects, and when each sound occurs. Match the timeline to the requested clip duration. H3 base modes are intended for short clips, typically within the model's 4 to 15 second generation range.

## Ref2VA output

Preserve this order:

1. `subject_definitions`
2. `summary`
3. `retention_analysis`
4. `detailed_description`
5. `overall_soundscape`
6. `non_diegetic_music`

Use stable labels such as `<Picture 1>`, `<Video 1>`, and `<Audio 1>` everywhere. State exactly what is retained from each reference and where it appears.

## Rules

- Preserve dialogue and visible scene text exactly in the requested language.
- When the source brief requires visible-dialogue sync, preserve the exact speaker, mouth-visibility intent, cut policy, and measured speech duration in the chronological audiovisual description.
- Keep reference labels consistent and preserve Story-Film reference authority scopes. A character atlas is not automatically composition authority and a temporal tail is not identity authority.
- Tie first or last frames to the timeline explicitly in keyframe modes. When `end_frame.required` is present, end the described timeline in that state and use FL2VA/L2VA only when the selected local workflow actually uses last-frame conditioning.
- For Ref2VA continuation, a registered visual-only previous-shot tail may carry temporal continuity. Its audio must be stripped before it becomes a visual reference.
- When approved dialogue audio exists, preserve the model-neutral seconds and exact approved source. If live ComfyUI exposes `MiniMaxH3TimedAudio` and `MiniMaxH3ExactAudioLock`, the optional exact-audio profile may convert start seconds to H3's 24 fps target timeline and pair the lock with core `MiniMaxH3AddGuide` at the same frame. If those nodes are absent, report the capability as unavailable; never install them silently.
- Preserve source `capture_behavior` as visible capture properties rather than inventing camera hardware.
- Use concrete image and sound descriptions instead of generic quality adjectives.
- Save under `04_generation/prompts/minimax-h3/<shot-id>.md`.

## Done

All references resolve, section order is correct, and described audiovisual time equals requested duration.
