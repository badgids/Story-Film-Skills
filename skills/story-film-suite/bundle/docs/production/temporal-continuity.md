# Temporal Continuity

[Documentation home](../README.md) | [Up: Production](../README.md#3-feature-film-production)

## Table of contents

- [End frame and motion tail](#end-frame-and-motion-tail)
- [Visual-only rule](#visual-only-rule)
- [Related pages](#related-pages)

## End frame and motion tail

Use the previous approved end frame for exact positional handoff and an optional short tail for motion state. The duration is adapter policy rather than universal canon.

## Visual-only rule

Continuation tails used as visual references must have audio stripped so dialogue or soundtrack from the previous shot cannot leak into the next generation. `scripts/temporal_continuity.py extract-tail` creates that derivative.

## Related pages

- [Dialogue audio authority](dialogue-audio-authority.md)
- [Reference authority](reference-authority.md)
