# Video Finishing

Video finishing prepares selected picture media for edit and delivery while preserving the selected creative take.

## Operations

A finish pass may include:

- source trim
- frame-rate normalization
- resolution normalization
- fit with letterbox or pillarbox
- deliberate fill-and-crop
- sample-aspect normalization
- pixel-format normalization
- codec normalization
- deterministic conventional upscale
- optional AI upscale through an approved model route

## Manifest

Use `05_post/video_finish.jsonl` when selected media need explicit preprocessing.

```json
{
  "finish_id": "MEDIA-201",
  "source_media_id": "MEDIA-001",
  "input_path": "04_generation/comfyui/outputs/shot-001.mp4",
  "output_path": "05_post/finished/shot-001.mp4",
  "width": 1920,
  "height": 1080,
  "fps": 24.0,
  "fit": "contain",
  "codec": "libx264",
  "crf": 18
}
```

`fit` is `contain` or `cover`.

## Rules

1. Never replace the source candidate in place.
2. Preserve the relationship to the selected source media ID.
3. Do not call a conventional scale filter an AI upscale.
4. If AI upscaling is requested, route through a declared generation capability and keep the result as a new media candidate.
5. Run media QC again after a destructive or generative finishing pass.
6. The executable timeline may normalize clips itself, so a separate finish file is optional when no dedicated picture finishing is required.
