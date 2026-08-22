# Dialogue Audio Authority

Approved dialogue audio is a production authority. The waveform used to condition visible speech and the waveform reviewed or muxed as the approved dialogue should resolve to the same `MEDIA-###` record and SHA-256 digest unless an explicit derived-audio transform is approved.

A record under `04_generation/dialogue_audio_authority.jsonl` may contain:

```json
{
  "line_id": "LINE-018",
  "speaker_id": "CHAR-002",
  "approved_audio_media_id": "MEDIA-083",
  "path": "04_generation/audio/dialogue/LINE-018.wav",
  "audio_sha256": "...",
  "start_seconds": 2.417,
  "visible_sync_required": true,
  "generation_audio_authority": "approved-dialogue",
  "review_audio_authority": "approved-dialogue"
}
```

Voice-over, radio, unseen phone speech, and other off-screen speech may be approved dialogue without becoming mouth-conditioning input. The visible-sync decision remains separate.

Frame indices are adapter-specific. Store seconds in the model-neutral record. An H3 adapter may convert seconds to H3's 24 fps target timeline.
