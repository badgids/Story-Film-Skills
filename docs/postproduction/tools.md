# Postproduction Tools

[Documentation home](../README.md) | [Up: Editorial](editorial.md) | [Next: Final completeness](../release/completion.md)

## Table of contents

- [FFmpeg and FFprobe](#ffmpeg-and-ffprobe)
- [ImageMagick](#imagemagick)
- [MLT](#mlt)
- [Kdenlive](#kdenlive)
- [Shotcut](#shotcut)
- [Runtime discovery](#runtime-discovery)

## FFmpeg and FFprobe

Use FFmpeg for deterministic video and audio operations. Use FFprobe to inspect media.

The toolkit discovers installed filters, encoders, decoders, formats, devices, protocols, and hardware acceleration before it relies on optional features.

## ImageMagick

Use ImageMagick for deterministic still-image work such as resize, crop, composite, masks, text, contact sheets, and image analysis.

The toolkit respects the installed ImageMagick security policy.

## MLT

MLT is an optional timeline and media-service runtime. Story-Film Skills can query installed producers, filters, transitions, consumers, profiles, and presets when `melt` is available.

## Kdenlive

Kdenlive export writes an editable `.kdenlive` project based on documented MLT/Kdenlive structure.

## Shotcut

Shotcut export writes an editable `.mlt` project with Shotcut project properties.

## Runtime discovery

Run:

```bash
python scripts/media_toolkit.py discover --project PROJECT --deep
```

Do not claim that an optional runtime was used if it is not installed.

## Related pages

- [Editorial](editorial.md)
- [Finishing](finishing.md)
- [GitHub-ready development](../development/github-ready.md)
