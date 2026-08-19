# Programmatic Video

Programmatic video is an optional composition route for motion graphics, explainers, data-driven video, complex title sequences, animated maps, kinetic typography, and reusable campaign templates.

The portable source of truth is `05_post/programmatic/compositions.json`. Each composition uses a stable `COMP-###` ID and describes dimensions, frame rate, duration, assets, and layers without requiring a specific renderer.

## Remotion adapter

`scripts/remotion_adapter.py` can translate the portable composition manifest into a small Remotion project under `05_post/programmatic/remotion/`.

The package does not bundle Remotion and does not require it for ordinary film production. Remotion has its own license terms. Rendering or installation must be treated as an optional external-runtime operation, and the agent must not claim eligibility for a license on the user's behalf.

## Composition principles

- data and media references stay project-relative;
- user edits to generated programmatic-video code must be preserved;
- animation timing should be frame-deterministic;
- motion design should remain connected to `GFX-###`, campaign, trailer, or film source IDs;
- final renders enter the media registry and QC system like any other media candidate;
- a Remotion project is an implementation target, not higher authority than the portable composition manifest.

## Portable animation

Layers may use ordered `keyframes` with frame-relative values such as `x`, `y`, `scale`, `opacity`, `rotate_deg`, `rotate_x_deg`, `rotate_y_deg`, and `perspective`. This is sufficient to describe card swivels, pan/3D transitions, push-ins, kinetic type, and other deterministic transforms without making one named transition a special case.

