# Audio Mastering

A finished film requires an actual synchronized soundtrack, not only cue descriptions. The audio mastering layer turns approved dialogue, ambience, Foley, effects, score, and other stems into a reproducible master WAV.

## Portable manifest

Write `05_post/audio_mix.json`.

```json
{
  "schema_version": 1,
  "sample_rate": 48000,
  "channels": 2,
  "target_lufs": -16.0,
  "true_peak_db": -1.5,
  "master_duration": 600.0,
  "output_path": "05_post/masters/film_audio_master.wav",
  "tracks": [
    {
      "event_id": "AUD-001",
      "kind": "dialogue",
      "source_id": "VOICE-001",
      "media_id": "MEDIA-101",
      "path": "04_generation/audio/dialogue/line-001.wav",
      "start": 3.250,
      "source_in": 0.0,
      "duration": 2.100,
      "gain_db": 0.0,
      "pan": 0.0,
      "fade_in": 0.01,
      "fade_out": 0.03
    }
  ]
}
```

## Timing contract

- All timeline values are seconds from project time zero.
- `start` is destination timeline time.
- `source_in` is media trim-in time.
- `duration` is the amount of source media used.
- `master_duration` is the complete program duration when the soundtrack must match a film, trailer, teaser, or cutdown timeline.
- No audio event may extend past `master_duration`.
- The renderer pads true silence after the last audible event when needed so the audio stream reaches the declared program boundary.
- Dialogue generated from an exact screenplay line must preserve the line identity in `source_id` or metadata.
- Do not stretch dialogue silently to repair picture timing. Resolve timing conflicts explicitly.

## Track kinds

Recommended values:

- `dialogue`
- `voiceover`
- `ambience`
- `foley`
- `sfx`
- `score`
- `music`
- `room-tone`
- `other`

## Mix policy

1. Start from approved media only unless the user explicitly requests a rough mix.
2. Preserve exact start positions.
3. Apply per-event gain, pan, trim, and fades before the final bus.
4. Mix at the declared sample rate and channel count.
5. Apply target loudness and true-peak control on the final bus.
6. Keep source media unchanged.
7. Rebuild the master when the mix manifest or any source audio is newer than the existing output.
8. Write an execution report next to the master.
9. Do not claim an audio master exists until the renderer completes successfully and the output file is verified.

## Runtime

Actual rendering uses a local `ffmpeg` executable through `scripts/audio_master.py`. Planning remains valid without FFmpeg. If FFmpeg is absent and the user asked for a real master, report the missing runtime instead of pretending the manifest is a finished soundtrack.
