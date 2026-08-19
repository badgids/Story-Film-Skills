# Edit Assist

Edit assist handles repetitive deterministic editorial tasks without replacing the creative edit.

## Supported jobs

- silence mapping and speech-aware jump-cut preparation
- optional local transcription when a compatible transcription runtime is installed
- subtitle burn-in from reviewed subtitle files
- source clipping with precise in/out points
- subject-aware reframing with optional face-derived focus estimation
- delivery compression using project presets
- chapter, teaser, interview, or social clip extraction from approved time ranges

## Non-destructive rule

Source media is never overwritten by default. Every operation writes a new project-relative output.

## Silence maps

`05_post/edit_assist/silence_map.json` records detected silence and complementary keep intervals. Detection is evidence, not an automatic editorial decision. The agent should preserve intentional pauses, reactions, music, room tone, and dramatic silence when they matter.

## Transcription

Transcription is optional. If `faster-whisper` is unavailable, report that capability as missing instead of inventing captions. Generated transcripts are drafts until checked against the authoritative screenplay or source recording.

## Reframing

When adapting landscape material to vertical or square delivery:

1. prefer purpose-shot media for the destination ratio;
2. otherwise use approved focus metadata;
3. optionally estimate a focus point from detected faces;
4. preserve required action, props, eyelines, subtitles, and title-safe regions;
5. use contain/pad when a fill crop would remove required information.

## Delivery presets

Built-in presets are project defaults, not permanent platform rules. Current platform requirements must be verified when they matter.

Use `scripts/edit_assist.py` for deterministic execution.
