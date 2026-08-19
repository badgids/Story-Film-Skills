# FFmpeg Toolkit Contract

FFmpeg and FFprobe are first-class deterministic media tools in this package. Use them for video, audio, subtitle, metadata, container, codec, stream, filter, measurement, capture, and delivery work when they are the correct tool.

## Runtime truth

Do not assume that a named codec, filter, muxer, demuxer, device, protocol, or hardware accelerator exists merely because FFmpeg supports it in some builds. Builds differ.

Before advanced work, discover the local runtime:

```bash
python scripts/media_toolkit.py discover --project PROJECT --deep
```

Or query only what is needed:

```bash
python scripts/media_toolkit.py query ffmpeg --category filters
python scripts/media_toolkit.py query ffmpeg --category encoders
python scripts/media_toolkit.py query ffmpeg --category decoders
python scripts/media_toolkit.py query ffmpeg --category formats
python scripts/media_toolkit.py query ffmpeg --category protocols
python scripts/media_toolkit.py query ffmpeg --category devices
python scripts/media_toolkit.py query ffmpeg --category hwaccels
python scripts/media_toolkit.py query ffmpeg --category filters --name scale
```

Use `ffprobe` for stream, packet, frame, chapter, metadata, disposition, duration, color, codec, and container inspection rather than guessing from a filename.

## Capability families

The skill must be able to route work across the installed FFmpeg surface, including:

- demuxing and muxing
- decoding and encoding
- stream copy and remuxing
- transcoding
- video filtering and filter graphs
- audio filtering and filter graphs
- subtitle decode, encode, burn-in, extraction, and muxing
- scaling, crop, pad, rotate, transpose, perspective, overlay, blend, mask, chroma/luma keying
- frame-rate conversion, trim, setpts, concat, reverse, loop, freeze, thumbnail, select, scene detection
- color range, pixel format, colorspace, transfer, primaries, HDR metadata, tone mapping where installed
- denoise, sharpen, blur, deinterlace, stabilization, interpolation, optical-flow features where installed
- audio trim, delay, pan, channel mapping, resampling, fades, EQ, dynamics, compression, limiting, normalization, loudness analysis, mixing, ducking, convolution where installed
- waveform, vectorscope, histogram, signalstats, loudness, black-frame, silence, freeze, and other QC measurements
- metadata, chapters, stream dispositions, attachments, cover art, timecodes, and language tags
- image sequences and frame extraction
- animated image formats when supported
- screen, camera, microphone, deck, network, and other device capture when the local build exposes a suitable device
- network inputs and outputs through installed protocols
- hardware decode, encode, filtering, and device contexts when supported by the local build and hardware
- bitstream filters
- complex multi-input and multi-output filter graphs
- deterministic batch operations

This list is a routing map, not a frozen capability whitelist. For an unfamiliar operation, ask the installed FFmpeg itself using `-h`, `-filters`, `-encoders`, `-decoders`, `-formats`, and related discovery commands.

## Safe command execution

Use `scripts/media_toolkit.py run ffmpeg -- ...` when a task does not fit one of the higher-level bundled scripts.

The bridge executes an argv array directly. It does not invoke a shell. This prevents shell expansion from being mistaken for FFmpeg syntax.

`ffmpeg -y` requires explicit `--allow-overwrite` through the bridge. Prefer new output files. Never overwrite source media merely for convenience.

## Portable manifests

For repeatable project work, use a tool manifest:

```json
{
  "schema_version": 1,
  "steps": [
    {
      "step_id": "TOOL-001",
      "tool": "ffmpeg",
      "args": ["-i", "04_generation/source.mp4", "-vf", "scale=1920:1080", "05_post/finished/source-1080.mp4"],
      "inputs": ["04_generation/source.mp4"],
      "outputs": ["05_post/finished/source-1080.mp4"]
    }
  ]
}
```

Run it with:

```bash
python scripts/media_toolkit.py manifest PROJECT 05_post/tool_runs/operation.json
```

Explicit input and output paths in reusable manifests must be project-relative.

## Existing specialized helpers

Prefer these when they fit because they add domain validation:

- `audio_master.py`
- `video_finish.py`
- `render_timeline.py`
- `social_reframe.py`
- `delivery_qc.py`
- `film_master.py`
- `render_promos.py`

Use raw FFmpeg only when the requested operation needs a capability those wrappers do not expose.

## Evidence and completion

A command line is not evidence that media was produced correctly. After a material edit:

1. verify the process exit status;
2. verify required output files exist and are nonempty;
3. inspect streams with FFprobe when media structure matters;
4. run delivery or media QC appropriate to the endpoint;
5. preserve the command or tool manifest for reproducibility when the operation changes an approved production asset.
