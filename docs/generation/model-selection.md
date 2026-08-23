# Choose Generation Models and ComfyUI Resources

[Documentation home](../README.md) | [Up: ComfyUI generation](comfyui.md) | [Next: Resource-safe generation](resource-safe.md)

## Table of contents

- [What you can choose](#what-you-can-choose)
- [How Story-Film finds your installed models](#how-story-film-finds-your-installed-models)
- [Configure models with Pi](#configure-models-with-pi)
- [More than four decisions](#more-than-four-decisions)
- [Video default](#video-default)
- [Choose exact VAEs and text encoders](#choose-exact-vaes-and-text-encoders)
- [Choose LoRAs](#choose-loras)
- [Choose upscalers and frame interpolation](#choose-upscalers-and-frame-interpolation)
- [Change a saved choice](#change-a-saved-choice)
- [If a selected file is missing](#if-a-selected-file-is-missing)

## What you can choose

You control the generation setup.

Story-Film Skills has separate settings for these processes:

- image generation
- image edit generation
- video generation
- text to speech
- music generation
- SFX and Foley generation
- image upscaling
- video upscaling
- frame interpolation

For each process, you can choose two levels.

First, choose an adapter or model family. Examples are MiniMax H3, LTX 2.5, Qwen Image, or Qwen3 TTS.

Second, choose the exact files that ComfyUI will load. These can include:

- checkpoint models
- diffusion models
- VAE files
- CLIP or other text encoders
- LoRAs
- CLIP Vision models
- ControlNet models
- audio encoders
- upscalers
- frame-interpolation models
- custom model folders reported by ComfyUI

Choosing MiniMax H3 does not automatically choose a VAE or text encoder.

## How Story-Film finds your installed models

Story-Film asks the running ComfyUI server for its model folders and the models inside each folder.

From the project directory, run:

```bash
python scripts/model_inventory.py scan . --url http://127.0.0.1:8188
```

Do not replace this command with raw `curl`, `wget`, inline Python HTTP code, or a new helper script. The inventory tool is the tested Story-Film path for `/models` and `/models/{folder}`.

When Story-Film Skills is installed as a Pi Git package, Pi can run the copy of this script inside the installed package.

This server inventory also covers model directories registered outside the ComfyUI application directory, including directories configured through `extra_model_paths.yaml`. You do not need to move or duplicate those models into `ComfyUI/models`. Story-Film asks the running server what it can load.

Do not use a filesystem-wide model search as a fallback. If the server unexpectedly reports no models, stop and diagnose the live ComfyUI registry instead of creating mock media or downloading substitute models.

The scan writes:

```text
00_project/comfyui_model_inventory.json
00_project/comfyui_model_inventory.md
```

The JSON file is machine-readable.

The Markdown file is easy for a person to read.

Run another scan after you add, remove, or rename ComfyUI models.

## Configure models with Pi

You can tell Pi:

```text
Configure the generation models for this Story-Film project.
```

Pi must:

1. find the active ComfyUI server;
2. scan the current model inventory;
3. determine all required production processes and unresolved resource choices;
4. show only as many independent questions as the current Pi question UI supports;
5. wait for your answers;
6. save and validate those answers;
7. show the next page when unresolved required decisions remain;
8. continue until every required choice is selected, explicitly delegated, or proven not required by the selected workflow.

You can also print one process menu yourself:

```bash
python scripts/model_inventory.py menu . --process video_generation
```

Other process names are:

```text
image_generation
image_edit
video_generation
tts
music
sfx_foley
image_upscaling
video_upscaling
frame_interpolation
```

A Pi selection can look like this:

```text
Video generation
A1. minimax-h3 (default)
A2. ltx-2-5

Diffusion models
D1. example-video-model-a.safetensors
D2. example-video-model-b.safetensors

VAE
V1. example-video-vae.safetensors

Text encoders
T1. example-clip.safetensors
T2. example-t5.safetensors

LoRAs
L1. camera-motion.safetensors
L2. character-style.safetensors
```

You can then answer in normal language. For example:

```text
Use MiniMax H3. Use diffusion model D2, VAE V1, text encoders T1 and T2, and LoRA L1 at 0.8 model strength and 0.7 CLIP strength.
```

Pi must save the exact server-returned file names. It must not replace your choice with another file.

## More than four decisions

Some Pi question interfaces allow only a small number of questions in one interaction. Story-Film treats that limit as a page size, not as permission to make the remaining production decisions for you.

For example, a production can need separate choices for video, image generation, image editing, TTS, music, SFX/Foley, upscaling, and frame interpolation. Story-Film can ask the first page, wait for your answers, save and validate them, and then ask the next page.

Story-Film must not combine music and SFX/Foley merely to save a question slot. It must not silently choose SFX/Foley after asking about four other processes. It must not assume a VAE or text encoder is implied by the adapter name just to reduce the number of questions.

A later page is unnecessary only when the choice is already validly saved for this project, you explicitly delegated it, or the selected workflow proves that resource is not required.

## Video default

If you do not choose a video adapter, Story-Film Skills uses **MiniMax H3**.

The adapter name is:

```text
minimax-h3
```

This default selects only the Story-Film video adapter.

It does not choose:

- a checkpoint;
- a diffusion model;
- a VAE;
- a text encoder;
- a LoRA.

LTX 2.5 remains available, but it is not the default.

## Choose exact VAEs and text encoders

Selections are saved per process and per adapter profile.

For example, you can keep one VAE and text-encoder setup for MiniMax H3 and a different setup for LTX.

Example commands:

```bash
python scripts/model_preferences.py set-adapter . video_generation minimax-h3 --source user
```

```bash
python scripts/model_preferences.py set-resource . video_generation vae video-vae.safetensors
```

```bash
python scripts/model_preferences.py set-resource . video_generation text_encoders clip.safetensors t5.safetensors
```

The file names must match the active ComfyUI inventory exactly.

## Choose LoRAs

A LoRA selection stores the file name and its strengths.

Example:

```bash
python scripts/model_preferences.py add-lora . video_generation camera-motion.safetensors \
  --strength-model 0.8 \
  --strength-clip 0.7
```

Add more than one LoRA by running the command again with another file.

Remove one LoRA:

```bash
python scripts/model_preferences.py remove-lora . video_generation camera-motion.safetensors
```

Story-Film Skills must not add a LoRA unless you selected it or you explicitly asked Story-Film Skills to choose it for you.

## Choose upscalers and frame interpolation

First scan ComfyUI.

Then show the matching process menu:

```bash
python scripts/model_inventory.py menu . --process image_upscaling
```

or:

```bash
python scripts/model_inventory.py menu . --process frame_interpolation
```

Save an upscaler:

```bash
python scripts/model_preferences.py set-adapter . image_upscaling comfyui-native --source user
python scripts/model_preferences.py set-resource . image_upscaling upscale_models MyUpscaler.pth
```

The adapter name can identify the workflow family that you want to use. The exact installed model file is stored separately.

## Change a saved choice

Show all current choices:

```bash
python scripts/model_preferences.py show .
```

Change a process adapter:

```bash
python scripts/model_preferences.py set-adapter . music ace-step-xl --source user
```

Clear one resource folder:

```bash
python scripts/model_preferences.py clear-resource . music text_encoders
```

Reset a process:

```bash
python scripts/model_preferences.py reset-process . music
```

The older video commands still work:

```bash
python scripts/model_preferences.py set-video . ltx-2-5 --source user
python scripts/model_preferences.py reset-video .
```

## If a selected file is missing

Story-Film Skills stops and reports the missing file.

It can show the new inventory.

It must not silently select another checkpoint, VAE, text encoder, LoRA, audio model, or upscaler.

Run another scan after changing the ComfyUI model folders:

```bash
python scripts/model_inventory.py scan . --url http://127.0.0.1:8188
```

Then choose the replacement yourself.

## Related pages

- [ComfyUI generation](comfyui.md)
- [Resource-safe local generation](resource-safe.md)
- [RAM and VRAM generation budgets](memory-budget.md)
