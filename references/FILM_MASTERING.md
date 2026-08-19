# Film Mastering

Film mastering converts approved picture, synchronized audio, subtitles, and delivery settings into a finished film file.

## Required inputs

Before final mastering:

- approved screenplay baseline
- production coverage pass
- selected picture media
- no unresolved hard media-QC failures in selected picture
- executable main timeline
- rendered audio master or a valid audio mix manifest
- subtitle file when required
- target delivery specification

## Main outputs

Recommended project paths:

- `05_post/masters/film_audio_master.wav`
- `05_post/masters/film_master.mp4`
- `05_post/qc/film_master.json`
- `05_post/render_reports/film_master.json`

## Mastering gate

A final film is complete only when:

1. every required timeline source exists;
2. the audio master exists and is readable;
3. the picture timeline renders successfully;
4. the final container contains the required picture and audio streams;
5. duration is within the declared tolerance;
6. resolution and frame rate match delivery intent;
7. the requested subtitle policy is satisfied;
8. delivery QC has no blocking failure;
9. the master is registered in the media registry;
10. its SHA-256 checksum is recorded for release packaging.

A portable manifest is valuable, but it is not a finished film file.
