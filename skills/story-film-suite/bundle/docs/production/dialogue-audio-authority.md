# Dialogue Audio Authority

[Documentation home](../README.md) | [Up: Production](../README.md#3-feature-film-production)

## Table of contents

- [Approved waveform](#approved-waveform)
- [Visible speech](#visible-speech)
- [Related pages](#related-pages)

## Approved waveform

Store the approved `MEDIA-###`, path, SHA-256 digest, speaker, `LINE-###`, and start time. Generation conditioning and review audio should resolve to the same approved waveform unless an explicit derivative is approved.

## Visible speech

Visible-sync requirements remain separate from audio approval. Voice-over and other off-screen speech can be approved dialogue without becoming mouth-conditioning input. H3 frame conversion belongs in the H3 adapter; the durable record stores seconds.

## Related pages

- [Dialogue timing](dialogue-timing.md)
- [Temporal continuity](temporal-continuity.md)
- [Optional ComfyUI nodes](../generation/comfyui-optional-nodes.md)
