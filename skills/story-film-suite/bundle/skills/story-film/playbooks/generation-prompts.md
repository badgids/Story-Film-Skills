# Generation Prompts Only


> Before model-specific prompts or ComfyUI workflows, run `generation-model-setup`. Poll the live ComfyUI model inventory and record the user-selected adapter plus exact model resources for each production process. MiniMax H3 is only the default video adapter. Do not guess concrete model files, VAEs, text encoders, LoRAs, audio models, or upscalers.

1. Read the supplied model-neutral brief and canon.
2. Read `MODEL_SELECTION.md` and `MODEL_ROUTING.md`. For video, honor the user's choice. If the user did not choose a video model, use `minimax-h3`.
3. Run only the selected model adapter. Do not silently substitute LTX or another model.
4. Run `prompt-qc`.
5. Do not create new story facts to make the prompt more colorful. Done when each source brief has a self-contained adapter prompt.
