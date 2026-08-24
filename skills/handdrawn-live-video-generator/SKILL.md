---
name: handdrawn-live-video-generator
description: "Adapt MiniMax H3 prompts for surreal single-scene clips where rough hand-drawn animation physically contacts, deforms around, or interacts with live-action hands, objects, surfaces, and camera motion."
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Handdrawn Live Video Generator

Use for live-action scenes containing a deliberately rough hand-drawn animated element that interacts physically with real-world objects or a hand.

## Prompt overlay

- Clearly define the live-action environment, contact object/hand, drawn subject, first contact point, deformation, reaction, movement path, and final state.
- The drawn layer should retain hand-made line texture and visibly react to contact rather than floating as an unrelated overlay.
- Preserve convincing occlusion, surface contact, pressure/deformation cues, and local shadow/light interaction when appropriate.
- Let handheld or observational camera movement react slightly after the drawn action rather than predicting it.
- Keep the interaction continuous and physically readable within one scene unless the user explicitly requests multiple scenes.
- Avoid automatically turning the result into polished CG, a plush character, horror jump scare, or generic compositing effect.
- Respect the project's requested duration/aspect ratio instead of forcing example defaults.

## H3 handoff

Whether this skill was selected automatically or invoked directly, return through `h3-prompt-writing`, then `minimax-h3`, then `scripts/minimax_h3_prompt_validator.py`, and finally `prompt-qc`; this skill is a content/style overlay, not a standalone final-prompt path.
Use this overlay for action and texture, then encode the final clip with `h3-prompt-writing` and Story-Film's `minimax-h3` adapter.
