# Audio and Video Finishing

[Documentation home](../README.md) | [Up: Editorial](editorial.md) | [Next: Tools](tools.md)

## Table of contents

- [Purpose](#purpose)
- [Video finishing](#video-finishing)
- [Audio finishing](#audio-finishing)
- [Mastering](#mastering)
- [Quality control](#quality-control)

## Purpose

Finishing makes approved editorial media technically ready for the final master.

## Video finishing

Typical work can include:

- resolution normalization;
- frame-rate normalization;
- pixel-format conversion;
- aspect handling;
- subtitle treatment;
- overlays and titles;
- codec selection for a declared delivery target.

Use FFmpeg capability discovery when the operation depends on an optional codec, filter, or hardware path.

## Audio finishing

Typical work can include:

- dialogue alignment;
- music and effect placement;
- fades;
- channel mapping;
- resampling;
- loudness work;
- final stereo master creation.

Do not hide missing audio by silently shortening the picture timeline.

## Mastering

A final master is rendered from the executable timeline and approved media.

A file existing on disk does not prove that the master is complete.

## Quality control

Probe the final media. Check expected streams, duration, and declared delivery rules.

The final feature also passes the completeness audit.

## Related pages

- [Editorial](editorial.md)
- [Tools](tools.md)
- [Completeness audit](../release/completion.md)
