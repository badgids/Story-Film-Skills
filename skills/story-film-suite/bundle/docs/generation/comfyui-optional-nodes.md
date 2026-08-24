# Optional ComfyUI Custom Nodes

[Documentation home](../README.md) | [Up: Generation](../README.md#4-image-audio-and-video-generation)

## Table of contents

- [Policy](#policy)
- [Suggested packages](#suggested-packages)
- [Exact H3 audio lock](#exact-h3-audio-lock)
- [Installation](#installation)
- [Related pages](#related-pages)

## Policy

Story-Film does not bundle, install, update, or silently substitute custom-node code.

Bundled and package-custom workflows from Story-Film's `comfyui_workflows/` library can require optional custom nodes. Before use, Story-Film checks the live ComfyUI node inventory and reports missing packages.

A missing node blocks that selected workflow. It is not permission to silently choose another workflow or install the package.

## Suggested packages

| Package | Repository | Used for |
| --- | --- | --- |
| ComfyUI-H3-ExactAudioLock | `https://github.com/badgids/ComfyUI-H3-ExactAudioLock` | Exact timed H3 target audio and hybrid AddGuide conditioning |
| ComfyUI-OrbitSheets | `https://github.com/lumos675/ComfyUI-OrbitSheets` | Character/location/prop multi-view reference sheets |
| ComfyUI-VideoHelperSuite | `https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite` | `VHS_LoadVideo` and `VHS_VideoCombine` |
| ComfyUI-GGUF | `https://github.com/city96/ComfyUI-GGUF` | Optional GGUF model loaders used by compatible workflows |
| ComfyUI-Qwen-TTS | `https://github.com/flybirdxx/ComfyUI-Qwen-TTS` | Qwen3-TTS voice design and cloning workflows |
| Nvidia_RTX_Nodes_ComfyUI | `https://github.com/Comfy-Org/Nvidia_RTX_Nodes_ComfyUI` | Optional NVIDIA RTX video super resolution |
| ComfyUI_VLM_nodes | `https://github.com/gokayfem/ComfyUI_VLM_nodes` | Optional MiniMax music/API and VLM workflow nodes |

Exact dependencies depend on the workflow selected by the user. The table is not a claim that every bundled workflow uses every package.

## Exact H3 audio lock

`ComfyUI-H3-ExactAudioLock` provides `MiniMaxH3TimedAudio` and `MiniMaxH3ExactAudioLock`.

It builds a deterministic target waveform, locks H3's target audio latent, and leaves video denoisable.
It can be paired with core `MiniMaxH3AddGuide` at the same H3 frame.
Story-Film stores model-neutral seconds and approved audio hashes; the H3 workflow/adapter performs frame conversion as required.

A useful strict dialogue policy is overlapping sources allowed with no silent end-of-clip cropping. Consult the custom-node repository for the current node inputs and policies before adapting a workflow.

## Installation

Prefer ComfyUI Manager when the package is available there. For manual installation, enter the active ComfyUI `custom_nodes` directory and clone only the package you need.

Follow that package's current README for Python dependencies or platform requirements, then restart ComfyUI.

Story-Film detects the resulting node classes through live `/object_info`; it does not run installation commands itself.

## Related pages

- [Choose ComfyUI workflows](workflow-selection.md)
- [Dialogue audio authority](../production/dialogue-audio-authority.md)
- [Reference sheets](../production/reference-sheets.md)
