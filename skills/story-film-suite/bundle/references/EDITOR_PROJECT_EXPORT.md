# Editable Project Export Contract

Story-Film Skills can create editable Kdenlive and Shotcut projects from the canonical postproduction timeline or from an advanced editor-project manifest.

The rendered master remains the delivery truth. An editable project is a secondary production artifact.

## Canonical advanced manifest

Recommended path:

`05_post/editorial/editor_project.json`

Shape:

```json
{
  "schema_version": 1,
  "project_title": "Example",
  "profile": {
    "width": 1920,
    "height": 1080,
    "fps": 24,
    "progressive": true,
    "colorspace": 709,
    "audio_channels": 2,
    "audio_sample_rate": 48000
  },
  "bin": [
    {
      "clip_id": "CLIP-001",
      "kind": "video",
      "path": "04_generation/video/shot.mp4",
      "name": "SHOT-001"
    }
  ],
  "tracks": [
    {
      "track_id": "V1",
      "name": "V1",
      "type": "video",
      "clips": [
        {
          "edit_id": "EDIT-001",
          "clip_id": "CLIP-001",
          "timeline_start": 0,
          "duration": 4.5,
          "source_in": 1.0,
          "filters": []
        }
      ]
    }
  ],
  "transitions": [],
  "global_filters": [],
  "markers": [],
  "subtitle_file": "05_post/subtitles.srt",
  "notes": []
}
```

## Filters

Filters use installed MLT service names rather than invented editor UI labels:

```json
{
  "service": "volume",
  "properties": {
    "level": "-6dB"
  }
}
```

Optional `shotcut_filter` or `kdenlive_id` metadata may be supplied only when verified against the intended editor/runtime.

## Transitions

A transition record identifies:

- MLT service
- `a_track`
- `b_track`
- timeline start
- duration
- service properties

Use only services that exist in the target MLT runtime when the project must open with that effect intact.

## Kdenlive export

Default output:

`05_post/editorial/kdenlive/film_project.kdenlive`

The exporter follows current Kdenlive Generation 5 structure:

- MLT profile
- source producers
- two internal playlists per Kdenlive timeline track so normal same-track mixing structure is represented
- track tractors
- a sequence tractor with `kdenlive:uuid`
- `main_bin`
- `kdenlive:docproperties.version` set to `1.1`
- source and sequence bin entries
- a final wrapper tractor with `kdenlive:projectTractor=1`
- adjacent/project-relative subtitle reference through the MLT subtitles filter when requested

Kdenlive can change its document format in future releases. Before promising compatibility with a specifically installed version, inspect that version or open the generated file in it.

## Shotcut export

Default output:

`05_post/editorial/shotcut/film_project.mlt`

The exporter writes an MLT XML project with Shotcut project semantics including:

- MLT profile
- source producers
- `main_bin`
- `shotcut:projectAudioChannels`
- `shotcut:projectFolder`
- named timeline playlists using `shotcut:name`
- video/audio playlist flags
- background producer/track
- a main tractor with `shotcut=1`
- automatic audio mixing transitions
- declared MLT filters and user transitions
- subtitle burn/reference filter when requested

## Generate from executable timeline

If only `05_post/timeline.json` exists, the exporter can derive a basic editor manifest automatically:

```bash
python scripts/editor_project_export.py PROJECT --target both --write-derived-manifest
```

This creates a single V1 picture track plus the final audio master when present. It preserves the exact cut order and source trims represented by the executable timeline.

## Advanced multitrack export

For layered editorial work, first create `editor_project.json` with explicit tracks and clip placements, then export:

```bash
python scripts/editor_project_export.py PROJECT \
  --editor-project 05_post/editorial/editor_project.json \
  --target both \
  --require-sources
```

Targets may be `kdenlive`, `shotcut`, or `both`.

## Limits and honesty

The exporter must not invent editor-private state.

A generated XML file passing structural validation proves that the project representation is internally coherent. It does not prove a future or differently configured editor build will preserve every optional third-party effect.

For a stronger target-specific result:

1. discover the installed MLT services;
2. use only available services for filters/transitions;
3. export the project;
4. parse and validate the generated XML;
5. when Kdenlive or Shotcut is installed in the execution environment, open/import the file as an integration check if the user requested that validation.

The package does not require either GUI editor in order to produce the project file.
