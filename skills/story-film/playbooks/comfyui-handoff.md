# ComfyUI Portable Package


> Before ComfyUI generation or model-specific prompt adaptation, run `generation-workflow-setup`. Select a complete workflow from the ordinary numbered catalog. The selected workflow owns its checkpoint/model, VAE, encoders, LoRAs, audio models, upscalers, nodes, and other graph settings. Do not run the retired per-resource TUI interview.

1. Run `project-impact` if upstream artifacts changed since the last generation package.
2. Read the requested scene, shot, cue, or sequence scope.
3. Ensure required `reference-assets` are approved or explicitly missing.
4. Run `generation-pack` for missing or stale model-neutral briefs.
5. Run `generation-workflow-setup` for each task required by the portable package. Record the complete workflow choice; run the prompt adapter implied by the selected workflow when prewritten prompts belong in the package.
6. `comfyui-handoff`: write the standalone portable handoff file with workflow selections or materialized project-relative workflow paths.
7. Run `prompt-qc` on included prompts and continuity checks across regenerated boundaries.

Done when `04_generation/comfyui_handoff.json` contains exactly the requested work, all paths are project-relative, every selected workflow/input/expected output is identifiable, and no external skill pack is required to understand the package.
