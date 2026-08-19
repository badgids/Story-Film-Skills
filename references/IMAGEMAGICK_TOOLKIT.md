# ImageMagick Toolkit Contract

ImageMagick 7 is a first-class deterministic still-image and image-sequence manipulation runtime for this package.

## Runtime truth

ImageMagick builds differ by delegates, formats, quantum depth, HDRI mode, policies, modules, and available fonts. Discover the installed runtime before relying on optional formats or delegates:

```bash
python scripts/media_toolkit.py discover --project PROJECT --deep
python scripts/media_toolkit.py query magick --category formats
python scripts/media_toolkit.py query magick --category delegates
python scripts/media_toolkit.py query magick --category policy
python scripts/media_toolkit.py query magick --category resources
python scripts/media_toolkit.py query magick --category colorspaces
python scripts/media_toolkit.py query magick --category fonts
```

## Capability families

Use ImageMagick when appropriate for installed and policy-allowed operations including:

- image format conversion
- resize, resample, thumbnail, crop, extent, trim, rotate, flip, flop, deskew, affine, and perspective transforms
- alpha, masks, clipping, matte, transparency, and compositing
- layers, flatten, merge, mosaic, append, montage, contact sheets, sprite sheets, and grids
- drawing, shapes, text, captions, labels, borders, frames, and title-card construction
- colorspace conversion, ICC profiles, color matrices, levels, curves, gamma, contrast, saturation, channel work, CLUTs, CDL, and HDRI-aware operations where supported
- blur, sharpen, unsharp, despeckle, denoise, morphology, convolution, threshold, edge detection, connected components, and other image analysis
- distortions, warps, remaps, displacement maps, virtual pixels, and perspective correction
- histogram, statistics, identify, moments, perceptual hash, compare, difference, and reconstruction checks
- image sequences, coalesce, deconstruct, delay, disposal, GIF/APNG/WebP-style animation work when the build supports the format
- batch processing
- metadata and profiles
- visual reference sheets, storyboard sheets, thumbnails, title cards, posters, social artwork, mattes, masks, and QC comparison images

This is not a frozen option list. For advanced or unfamiliar work, inspect `magick -help`, `magick -list`, and the installed operation behavior.

## Safety

ImageMagick supports powerful delegates and resource access. Respect the installed ImageMagick security policy.

Never weaken the user's security policy merely to make a conversion succeed. If policy blocks a format or delegate, report the blocker and use a safer available route if one exists.

`magick mogrify` edits files in place. The bundled bridge refuses it unless `--allow-overwrite` is explicitly supplied. Prefer `magick INPUT operations OUTPUT` so source media remains unchanged.

## Raw operation

Use the generic bridge for operations not represented by another skill:

```bash
python scripts/media_toolkit.py run magick -- INPUT.png -resize 1920x1080 OUTPUT.png
```

For reproducible multi-step work, use the portable tool-manifest format described in `FFMPEG_TOOLKIT.md` and set `tool` to `magick`.

## Completion

After image manipulation:

1. verify the command succeeded;
2. verify output format and dimensions with `magick identify` or FFprobe when appropriate;
3. compare against the source when fidelity matters;
4. preserve source assets unless an in-place operation was explicitly requested;
5. run media QC for production-critical images.
