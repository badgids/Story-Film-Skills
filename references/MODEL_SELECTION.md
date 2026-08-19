# Generation Model and Resource Selection

The user owns generation model and resource choices.

## Scope

Use this contract for these production processes:

- image generation
- image edit generation
- video generation
- text to speech
- music generation
- SFX and Foley generation
- image upscaling
- video upscaling
- frame interpolation

The process list is extensible. A future process must follow the same user-choice rules.

## Two separate choices

Do not mix these two concepts:

1. **Adapter or model family**: the Story-Film prompt/workflow family, such as `minimax-h3`, `qwen-image-2512`, or `qwen3-tts`.
2. **Concrete ComfyUI resources**: the exact installed checkpoint, diffusion model, VAE, text encoder, LoRA, ControlNet, audio encoder, upscaler, frame-interpolation model, or another server-reported model resource.

Choosing an adapter does not authorize Story-Film Skills to guess its concrete ComfyUI resources.

## Required inventory step

Before model-specific ComfyUI work:

1. Discover the active ComfyUI server.
2. Run `scripts/model_inventory.py scan <project-root> --url <comfyui-url>`.
3. Read `00_project/comfyui_model_inventory.json` or its Markdown companion.
4. Run `scripts/model_inventory.py menu <project-root> --process <process-id>` for each process that the production needs.
5. Show the available choices to the user.
6. Record the user's selections in `00_project/model_preferences.json`.

Do not infer user preference from file names, folder order, workflow examples, installed nodes, available VRAM, or the fact that a model is installed.

## Video default

If the user does not select a video adapter/model family, use `minimax-h3`.

This default applies only to the video adapter/model family. It does not choose a checkpoint, diffusion model, VAE, text encoder, or LoRA.

If the MiniMax H3 adapter or required resources are unavailable at generation time, report the blocker and show the available alternatives. Do not silently switch to LTX or another adapter.

## Other process defaults

Story-Film Skills does not force a default adapter for image generation, image editing, TTS, music, SFX/Foley, upscaling, or frame interpolation.

For those processes, ask the user to choose from the installed inventory. The user can also explicitly delegate the choice.

## User delegation

The user can say that Story-Film Skills may choose a model or resource for them.

When the user delegates a choice:

- explain the available options
- record the selection source as `delegated`
- set `user_confirmed` to true
- keep `allow_agent_substitution` false after the choice is recorded

Delegation for one process does not delegate another process.

## Model-specific profiles

Each process can store more than one adapter/model-family profile.

A profile can record exact resources by the folder names returned by ComfyUI. Examples include:

- `checkpoints`
- `diffusion_models`
- `vae`
- `text_encoders`
- `loras`
- `clip_vision`
- `controlnet`
- `audio_encoders`
- `upscale_models`
- `latent_upscale_models`
- `frame_interpolation`

Unknown or custom model folders are allowed when the running ComfyUI server reports them.

This lets a user keep one exact VAE, text-encoder, and LoRA stack for MiniMax H3 and a different stack for LTX without overwriting either profile.

## LoRA rule

Every selected LoRA records:

- exact installed file name
- model strength
- CLIP strength

Do not add a LoRA because it appears useful. The user must select it or explicitly delegate LoRA selection.

## Inventory validation

When `00_project/comfyui_model_inventory.json` exists, every selected concrete resource must exist in that inventory.

A missing selected resource is a blocker. It is not permission to substitute another resource.

## Runtime availability

Model choice and runtime availability are different facts.

A selected model that is not installed is a blocker. It is not permission to silently substitute another model.
