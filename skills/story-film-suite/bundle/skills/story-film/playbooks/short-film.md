# Short Film


> Before ComfyUI generation or model-specific prompt adaptation, run `generation-workflow-setup`. Select a complete workflow from the ordinary numbered catalog. The selected workflow owns its checkpoint/model, VAE, encoders, LoRAs, audio models, upscalers, nodes, and other graph settings. Do not run the retired per-resource TUI interview.

1. `story-brief`: include target runtime.
2. `story-architecture`: one central dramatic question and minimal subplot load.
3. `character-bible`: only characters who affect the film.
4. `world-bible` when setting rules matter.
5. `beat-sheet`.
6. `scene-outline`.
7. `write-screenplay`.
8. `revise-screenplay`: remove setup that does not pay off within the runtime.
9. `production-breakdown`, `director-book`, and `visual-bible` when visual rules need to persist.
10. `reference-assets`: create only continuity-critical references the short uses.
11. `previz-plan` or `production-diagrams` for scenes whose blocking or geography needs them.
12. Run `production-capabilities`, `performance-blocking`, `shot-design`, `shot-list`, `storyboard-prompts`, audio skills as needed, then `shooting-script` and `production-coverage`. Required visible dialogue must preserve exact line, speaker, timing, and covering-shot sync before generation.
13. Run `generation-pack`. For every generation task actually needed by the scope, run `generation-workflow-setup`, show the complete numbered workflow list, and record the user's workflow choice. Then run only the prompt adapter required by that selected workflow, `prompt-qc`, `edit-plan`, and `editorial-package` as needed. If media is generated, run `media-qc` before `take-selection`.
14. Use `comfyui-handoff` when the user wants a portable generation package. The handoff records selected workflow identities rather than rebuilding model stacks.
15. If the user also wants actual ComfyUI rendering, follow the ComfyUI Generate playbook after the handoff and keep prompt IDs and outputs tied to the originating shot/cue IDs. Register concrete outputs with `asset-approval`.
16. If the endpoint is an actual finished short film, run `film-finishing`.
17. If editable Kdenlive/Shotcut projects or additional deterministic media edits are requested, run `media-editing-and-project-export`.
18. If trailers or a social release campaign are requested, run `trailer-campaign`, `social-campaign`, and `release-package` as required.

Done when runtime and generation duration estimates are internally consistent, every shot has a job, references are explicit, and the requested endpoint is complete. A finished-film endpoint requires an actual verified master file.
