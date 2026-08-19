# Executable Timeline

The executable timeline is the standalone bridge from editorial intent to a real rendered picture master. It is deliberately simpler than a full nonlinear-editor project so weak models can build and validate it reliably.

## File

Write `05_post/timeline.json` for the main film. Trailer and social timelines use the same schema in their own release directories.

## Shape

```json
{
  "schema_version": 1,
  "timeline_id": "MASTER-001",
  "title": "Untitled",
  "video": {
    "width": 1920,
    "height": 1080,
    "fps": 24.0,
    "pixel_format": "yuv420p",
    "background": "black"
  },
  "audio_master_path": "05_post/masters/film_audio_master.wav",
  "subtitles_path": "05_post/subtitles.srt",
  "subtitle_mode": "muxed",
  "output_path": "05_post/masters/film_master.mp4",
  "events": [
    {
      "event_id": "EVT-001",
      "kind": "video",
      "source_id": "TAKE-001",
      "media_id": "MEDIA-001",
      "path": "04_generation/comfyui/outputs/shot-001.mp4",
      "source_in": 0.0,
      "duration": 4.5,
      "shot_id": "SHOT-001"
    }
  ]
}
```

## Event kinds

`video`
: A moving-image source. `path` is required.

`image`
: A still held for `duration`. `path` is required.

`color`
: A generated solid-color plate. `path` is omitted and `color` is required.

## Rules

1. Event order is playback order. Hard cuts are the portable default.
2. Every event needs a positive duration.
3. Source media paths are project-relative.
4. A video event may set `source_in` but cannot read before zero.
5. Keep shot, take, media, line, trailer, or social IDs when known.
6. Text cards should normally be rendered as approved image or video media first. Do not rely on platform-specific title effects for core delivery.
7. The main film timeline must cover the entire approved edit. Missing sections are blockers, not placeholders in a final master.
8. A trailer or social timeline may intentionally use only a subset of the film.
9. `subtitle_mode` is `none`, `sidecar`, or `muxed`. `sidecar` preserves the subtitle file outside the media container. `muxed` requires the renderer and delivery QC to include a subtitle stream.
10. Use `scripts/render_timeline.py` for actual rendering. The renderer normalizes each event into a resumable cache before concatenation.
11. When a synchronized audio master is muxed, render to the planned picture duration rather than truncating picture to the shorter input stream.
12. Do not claim a finished movie exists until the render and delivery QC both succeed.
