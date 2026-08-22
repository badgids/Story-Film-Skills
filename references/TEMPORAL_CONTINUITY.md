# Temporal Continuity Contract

An exact previous end frame preserves position and appearance. A short visual-only tail can also preserve motion direction, gait cadence, camera momentum, cloth movement, and other temporal state.

A temporal handoff may contain:

```json
{
  "shot_id": "SHOT-002",
  "previous_shot_id": "SHOT-001",
  "frame_zero_reference_id": "REF-041",
  "temporal_tail": {
    "source_media_id": "MEDIA-117",
    "derived_media_id": "MEDIA-118",
    "path": "04_generation/continuity/SHOT-002_tail.mp4",
    "duration_seconds": 2.0,
    "audio_policy": "strip",
    "sha256": "..."
  }
}
```

`duration_seconds` is model/profile policy, not universal canon. The Story-Film default validator permits any positive duration. A model adapter may recommend a value.

A continuation tail used only for visual continuity must contain no audio stream. The deterministic extraction tool uses FFmpeg with `-an` and can verify the result with FFprobe.
