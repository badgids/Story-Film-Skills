# Generation Prompts Only

1. Read the supplied model-neutral brief and canon.
2. Read `MODEL_SELECTION.md` and `MODEL_ROUTING.md`. For video, honor the user's choice. If the user did not choose a video model, use `minimax-h3`.
3. Run only the selected model adapter. Do not silently substitute LTX or another model.
4. Run `prompt-qc`.
5. Do not create new story facts to make the prompt more colorful. Done when each source brief has a self-contained adapter prompt.
