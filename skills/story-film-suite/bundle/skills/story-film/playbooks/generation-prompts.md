# Generation Prompts Only


> Before ComfyUI generation or model-specific prompt adaptation, run `generation-workflow-setup`. Select a complete workflow from the ordinary numbered catalog. The selected workflow owns its checkpoint/model, VAE, encoders, LoRAs, audio models, upscalers, nodes, and other graph settings. Do not run the retired per-resource TUI interview.

1. Read the supplied model-neutral brief and canon.
2. Read `WORKFLOW_SELECTION.md` and `MODEL_ROUTING.md`.
3. Use the workflow already selected for the target task. If no workflow is selected, run `generation-workflow-setup` and let the user choose from the ordinary numbered list.
4. Determine the prompt adapter from that selected workflow/model family when the workflow needs model-specific prompt grammar. Do not ask for a separate checkpoint/VAE/LoRA selection.
5. Run `prompt-qc`.
6. Do not create new story facts to make the prompt more colorful.

Done when each source brief has a self-contained prompt compatible with its selected workflow.
