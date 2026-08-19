# Release Delivery

Release delivery verifies and packages the finished film, trailers, social masters, subtitles, artwork, audio masters, copy, and metadata into a traceable release set.

## Layout

```text
06_release/
  delivery_specs.json
  release_manifest.json
  SHA256SUMS.txt
  trailers/
    delivery_report.json
  social/
    delivery_report.json
  artwork/
  package/
```

## Delivery specification

```json
{
  "schema_version": 1,
  "deliverables": [
    {
      "delivery_id": "DELIV-001",
      "kind": "film-master",
      "path": "05_post/masters/film_master.mp4",
      "required": true,
      "width": 1920,
      "height": 1080,
      "fps": 24.0,
      "duration": 600.0,
      "duration_tolerance": 1.0,
      "video_codec": "h264",
      "audio_required": true,
      "audio_sample_rate": 48000
    }
  ]
}
```

## QC

Delivery QC should verify what can be observed deterministically:

- file exists and is nonempty
- container can be probed
- video/audio stream presence
- codec when constrained
- width and height
- frame rate within tolerance
- duration within tolerance
- audio sample rate and channels when constrained
- subtitle stream presence when a muxed subtitle delivery is required
- checksum
- optional black-frame or frozen-frame detection when requested

Optional signal checks can be declared in a delivery spec:

```json
{
  "black_frame_check": {"enabled": true, "min_duration": 1.0, "severity": "warn"},
  "freeze_frame_check": {"enabled": true, "min_duration": 2.0, "noise_db": -60.0, "severity": "warn"}
}
```

The deterministic checker uses FFmpeg `blackdetect` and `freezedetect` when those checks are enabled. `severity` may be `warn` or `fail`. A signal detector reports evidence. It does not decide whether an intentional black frame or held image is artistically wrong.

## Release manifest

Every release entry should include stable ID, kind, project-relative path, required/optional status, source IDs when applicable, QC status, and SHA-256 after the final file exists.

## Package rule

Never mark the release package complete while a required deliverable is missing or has blocking QC failure. Optional assets may remain absent if the manifest records that choice.

## Promotional readiness gate

Before collecting a release package, reconcile trailers and social deliverables with `scripts/promo_delivery.py PROJECT --reconcile`. The trailer and social delivery reports are deterministic evidence that required campaign outputs agree with approval state, final paths, QC records, and referenced copy. Release packaging should depend on these reports instead of assuming that a populated campaign manifest means the media exists.
