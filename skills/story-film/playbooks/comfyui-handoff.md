# ComfyUI Portable Package

1. Run `project-impact` if upstream artifacts changed since the last generation package.
2. Read the requested scene, shot, cue, or sequence scope.
3. Ensure required `reference-assets` are approved or explicitly missing.
4. `generation-pack` for missing or stale model-neutral briefs.
5. Resolve video generation through `MODEL_SELECTION.md`: honor the user's choice; otherwise default to `minimax-h3`. Do not silently select LTX or another video model. Run selected model adapters when prewritten prompts belong in the package.
6. `comfyui-handoff`: write the standalone portable handoff file.
7. Run `prompt-qc` on included prompts and continuity checks across regenerated boundaries.

Done when `04_generation/comfyui_handoff.json` contains exactly the requested work, all paths are project-relative, every input and expected output is identifiable, and no external skill pack is required to understand the package.
