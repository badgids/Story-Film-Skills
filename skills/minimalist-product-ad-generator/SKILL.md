---
name: minimalist-product-ad-generator
description: "Adapt MiniMax H3 prompts for minimalist physical-product ads with strict product fidelity, clean negative space, product-specific motion, restrained integrated typography, and premium camera language."
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Minimalist Product Ad Generator

Story-Film portability adaptation of MiniMax's Hub-oriented product-ad skill. Use this as a prompt overlay, not as a replacement for `h3-prompt-writing`.

## Use when

Use for a physical product ad, e-commerce short, product launch, or premium minimalist product film. Do not auto-use for a generic brand reel, talking-head ad, complex screen demo, or narrative film.

## H3 prompt overlay

- Treat product body color, material tint, finish, silhouette, and visible structure as fidelity constraints.
- Build a product-specific narrative rather than a generic tech-ad template.
- Prefer one primary product action per beat: opening, rotating, snapping, folding, sliding, lighting, screen change, texture reveal, or another visible real feature.
- Use clean composition, readable negative space, restrained motion, product macro detail, and deliberate highlights.
- If integrated advertising copy is requested, keep it short, single-line, readable, and visually integrated rather than subtitle-like. Do not invent claims.
- Multiple variants should have a named main variant and a clear entry order rather than an e-commerce grid.
- Transitions should come from product edges, highlights, physical actions, matched geometry, or controlled camera movement, not random effects.

## H3 handoff

After applying these content rules, format the final prompt through `h3-prompt-writing` and then `minimax-h3`. Story-Film canon, reference authority, duration, and exact visible text remain authoritative.
