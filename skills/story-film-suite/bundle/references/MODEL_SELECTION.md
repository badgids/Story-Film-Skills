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

## Question pagination and decision completeness

A host question tool can limit how many questions are shown in one invocation. That is a page-size limit only. It is never a limit on how many Story-Film decisions the user may control.

For every required production process:

1. Build an ordered queue of unresolved adapter/model-family and concrete-resource decisions.
2. Ask only as many independent questions as the current host UI supports in one interaction.
3. Wait for the user's answers.
4. Save and validate those answers in `00_project/model_preferences.json`.
5. If required decisions remain unresolved, ask the next page after the user has answered the previous page.
6. Repeat until every required decision is selected, explicitly delegated, or proven not required by the selected workflow.

Do not fire multiple question-tool invocations back-to-back without a user response merely to bypass a host UI limit.

Do not merge independent production decisions just to fit one question page. For example, music and SFX/Foley are separate processes, image generation and image editing are separate processes, and upscaling and frame interpolation are separate processes.

Do not silently default, omit, infer, or substitute a required decision because the current question page is full. The only forced adapter default is the documented MiniMax H3 video default, and that default never chooses its checkpoint, diffusion model, VAE, text encoder, LoRA, or another concrete resource.

Reducing question count is valid only when a still-valid saved project selection already exists, the user explicitly delegated that decision, or the selected workflow proves the resource is not required.

### External ComfyUI model directories

ComfyUI can load model roots that are outside its application directory. A common configuration uses `extra_model_paths.yaml`.

Story-Film does not need the filesystem location of those models. The running ComfyUI process registers those roots, and its `/models` and `/models/{folder}` endpoints return the model filenames that ComfyUI can actually load. Use those server results as the source of truth.

Do not use a filesystem-wide `find` command to locate models. Do not assume an empty local `ComfyUI/models` directory means no models are installed. Do not parse `extra_model_paths.yaml` merely to rediscover paths that the server has already registered.

`/object_info` has a different purpose. It reports installed node schemas. Current node inputs are described under `input.required` and `input.optional`. Story-Film can use dropdown choices from those schemas as secondary evidence, but it must not replace the `/models` registry with an ad hoc node parser.

If `/models` unexpectedly reports no model filenames, record a discovery blocker and diagnose the active server/configuration. Do not download replacement models and do not create mock generated media to bypass the blocker.

### One inventory implementation

The ComfyUI `/models` API is the source of truth, but Story-Film agents must access that API through `scripts/model_inventory.py` during production. This keeps parsing, exact filenames, external model paths, and saved inventory state in one tested implementation.

Do not replace `model_inventory.py` with raw `curl`, `wget`, `urllib`, `requests`, shell loops, or a temporary helper script. Do not write a new model-directory parser. If the inventory tool fails, report that failure as a blocker and repair the tool or server connection.

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
