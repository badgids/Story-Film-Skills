---
name: co-op-game-intro-generator
description: "Adapt MiniMax H3 prompts for two-player co-op game menu and opening animations with locked player identity, stable UI hierarchy, exact game/player text, coordinated palette, and timed menu interaction."
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Co-op Game Intro Generator

Use for a two-player co-op game menu or opening animation with two named players/characters and visible UI interaction.

## Prompt overlay

- Lock PLAYER 1 and PLAYER 2 identity anchors separately. Do not swap names, faces, positions, colors, or reference roles.
- Preserve the exact game title, player names, menu copy, and any approved UI text.
- Establish a stable menu hierarchy, player-card placement, character positions, buttons/icons, palette, typography, and negative space before motion.
- Character reference images provide identity, not automatic photographic style authority.
- Keep UI readable and avoid wrapping or multiplying text blocks unless the approved design requires it.
- Describe event timing explicitly: character reaction, selector movement, hover/click state, button activation, UI response, and final menu state.
- If Story-Film already has an approved keyframe or UI reference, use that as the composition authority rather than rebuilding a different menu framework.

## H3 handoff

Use `h3-prompt-writing` for the selected H3 keyframe/reference mode. Use `minimax-h3` to preserve exact text, reference scopes, and timing.
