# Feature Film


> Workflow preflight gate: when the requested endpoint includes ComfyUI, complete the `film-production` workflow preflight before step 1 and before story/canon creation. Select every required workflow now. Sequence production later reuses those durable selections and does not ask again unless the user explicitly changes one.

Use for a full-length film package. Never attempt all screenplay pages, shots, references, and prompts in one working buffer.

1. `story-brief`: include target runtime and production constraints.
2. `story-architecture`, `character-bible`, `world-bible`, `beat-sheet`, and `scene-outline`. Lock recurring character identity, speech/movement/stillness signatures, and ensemble baselines globally before sequence production.
3. `write-screenplay` in sequential scene batches. After each batch, update the scene manifest, line manifest, `story-state`, and continuity state.
4. `revise-screenplay` on the whole script after a complete draft exists.
5. Freeze an approved screenplay baseline before shot production. Then run `feature-scale-production` to create `SEQ-###` boundaries, sequence shards, recovery controls, and feature-scale gates. Rebuild context shards after relevant canon or story-state changes so each sequence carries only its applicable character/location/prop canon and current state.
6. `visual-bible`: lock visual rules that must survive across sequences.
7. Build global `reference-assets` for recurring characters, locations, props, voices, and visual rules before sequence production. Add sequence-specific references only when needed.
8. Run `production-capabilities` for the selected production route. Divide production into sequences of related `SCN-###` IDs. Process one sequence at a time through `production-breakdown`, `director-book`, optional `production-diagrams`, optional `previz-plan`, `performance-blocking`, `shot-design`, `shot-list`, progressive `storyboard-prompts`, `dialogue-voice` where needed, `shooting-script`, `production-coverage`, and `generation-pack`. Required visible-dialogue sync is part of coverage. Do not advance an uncovered sequence into generation.
9. Before generation for a sequence, verify the playbook-entry workflow preflight remains complete and use its recorded task workflows. Do not reopen workflow selection. Each selected workflow determines the concrete model stack and any model-specific prompt adapter. Run `prompt-qc` per sequence. When candidates are generated, run `media-qc` before `take-selection`. Do not wait until the end to discover continuity drift.
10. Run `dialogue-voice`, `score-plan`, and `sound-design` across the full film after sequence needs are known. Lock recurring voice and motif identities globally.
11. `edit-plan` and `editorial-package`: reconcile sequence durations, audio bridges, subtitles, stems, placeholders, and pickups.
12. Final `continuity-check` across the whole package.
13. When the user wants a ComfyUI-ready export, run `comfyui-handoff` one sequence or stale dependency slice at a time with the selected workflow identities.
14. When the user wants actual ComfyUI rendering, follow the ComfyUI Generate playbook for one approved sequence or stale slice at a time. Preserve prompt IDs, rejected runs, and accepted output mappings instead of rendering the feature as one opaque batch. Register concrete media with `asset-approval`.
15. For an actual finished feature, run `film-finishing` after all required picture and audio groups are approved. The executable timeline may still be built sequence by sequence, but the final master gate covers the whole film.
16. If trailers or a social release campaign are requested, run `trailer-campaign`, `social-campaign`, and `release-package` after the required source media are stable.
17. Before declaring a finished feature complete, run `editorial-reconciliation`, the global `long-range-continuity` gate, `production-health`, and `film-completeness`. A master file by itself is not completion proof.

When editable Kdenlive/Shotcut projects or additional deterministic media manipulation are requested, run `media-editing-and-project-export` after editorial intent is reconciled.

Done when every screenplay scene belongs to exactly one production sequence, every planned shot maps to a scene, recurring references are versioned, and the requested endpoint can be reproduced without chat history or another skill pack. A finished-feature endpoint requires a verified final master.
