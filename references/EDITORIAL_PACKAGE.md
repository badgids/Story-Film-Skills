# Portable Editorial Package

The editorial package turns generated or planned media into a tool-neutral assembly specification.

## Outputs

Write when applicable:

- `05_post/edit_plan.md`
- `05_post/editorial_manifest.json`
- `05_post/cue_sheet.csv`
- `05_post/subtitles.srt`

## Editorial manifest

Minimum fields:

```json
{
  "schema_version": 1,
  "project_title": "Example",
  "frame_rate": 24,
  "timeline": [],
  "audio_stems": [],
  "subtitle_file": "05_post/subtitles.srt",
  "missing_media": [],
  "placeholders": [],
  "notes": []
}
```

## Timeline event

Each event should identify:

- event ID
- scene ID
- shot ID when visual
- source media path or placeholder ID
- source in and out when known
- timeline start and end
- transition
- dialogue or subtitle linkage
- music and sound cue linkage
- continuity note when relevant

## Portable first

Do not fabricate a native Premiere, Resolve, Final Cut, or editor-private project file without a tested exporter for that exact format. v00.00.07 includes a generic MLT exporter plus target-specific Kdenlive and Shotcut project exporters built from a shared canonical editor manifest. See `EDITOR_PROJECT_EXPORT.md`.

The editorial manifest remains the tool-neutral intent record. When the requested endpoint is an actual finished film, continue into `AUDIO_MASTERING.md`, `EXECUTABLE_TIMELINE.md`, and `FILM_MASTERING.md`; a portable edit plan alone is not a rendered movie.
