# Trailer System

A trailer is a separate short-form narrative edit with its own dramatic job, spoiler policy, source selection, pickups, score, sound design, titles, timing, aspect ratio, and QC.

## Project layout

```text
06_release/trailers/
  trailer_manifest.json
  assets.jsonl
  delivery_report.json
  TRL-001/
    timeline.json
    audio_mix.json
    subtitles.srt
    master.mp4
    qc.json
```

## Trailer manifest

```json
{
  "schema_version": 1,
  "campaign_id": "CAMP-001",
  "trailers": [
    {
      "trailer_id": "TRL-001",
      "type": "official",
      "target_duration": 90.0,
      "duration_tolerance": 3.0,
      "aspect_ratio": "16:9",
      "spoiler_policy": "Do not reveal the final resolution",
      "timeline_path": "06_release/trailers/TRL-001/timeline.json",
      "audio_mix_path": "06_release/trailers/TRL-001/audio_mix.json",
      "output_path": "06_release/trailers/TRL-001/master.mp4",
      "structure": [
        {"role": "hook", "purpose": "Immediate curiosity"},
        {"role": "world", "purpose": "Establish premise and characters"},
        {"role": "problem", "purpose": "State the central disruption"},
        {"role": "escalation", "purpose": "Increase stakes and pace"},
        {"role": "button", "purpose": "End on a memorable unresolved beat"},
        {"role": "title", "purpose": "Present verified title and release information"}
      ]
    }
  ]
}
```

## Recommended trailer classes

Do not force fixed durations, but support at least:

- official trailer, commonly 60 to 120 seconds
- teaser, commonly 20 to 45 seconds
- vertical teaser or cutdown, commonly 6 to 20 seconds

## Pickup rule

A trailer pickup is allowed when the existing film lacks a clean marketing beat, title card, isolated reaction, establishing image, or aspect-safe composition. A pickup must not silently change film canon.

## Spoiler rule

The trailer plan must state what cannot be revealed. Trailer source selection and copy should be checked against that policy before rendering.

## Mastering

Trailer timelines and mixes use the same executable timeline and audio mastering contracts as the film. This avoids a second editor-specific format.

## Delivery reconciliation

Rendering a trailer is not the same as declaring it release-ready. Run `scripts/promo_delivery.py PROJECT --scope trailers --reconcile` after trailer rendering and QC. A required trailer is `ready` only when its output exists, its `TRL-###` approval group resolves to the same primary media path, the primary media QC state is non-blocking, and the trailer QC report is complete. Optional trailers that were intentionally not produced are recorded as `optional-missing`.

The reconciliation report is written to `06_release/trailers/delivery_report.json`.
