# MLT Editable Timeline Export

The suite can export the executable timeline as generic standard MLT XML. For actual Kdenlive or Shotcut project requests, use `EDITOR_PROJECT_EXPORT.md` and `scripts/editor_project_export.py`.

## Boundary

The generic MLT exporter is an interchange convenience. The FFmpeg-rendered master remains the standalone finished-film path. A generic MLT file must not be mislabeled as a Kdenlive or Shotcut project when the target-specific exporter is available.

The exporter does not fabricate editor-private effects, UI state, proxy metadata, plugin data, or version-specific Kdenlive fields that were not tested.

## Output

Recommended path:

`05_post/editorial/film_timeline.mlt`

Trailer and social timelines may export their own `.mlt` files next to the corresponding timeline manifest.

## Rules

1. Resources use project-relative paths.
2. Event order and duration must match the executable timeline.
3. Audio master is represented as a synchronized audio producer when supplied.
4. Hard cuts are the portable baseline.
5. A successful XML export is not proof that a particular installed editor version imported it correctly. Live editor import remains an integration test.
