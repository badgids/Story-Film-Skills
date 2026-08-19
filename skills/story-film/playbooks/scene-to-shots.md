# Scene to Shots

1. Read the screenplay scene and canon.
2. `production-breakdown` for that scene.
3. `director-book` for scene engine, intent, blocking, rhythm, and final image or sound.
4. `reference-assets` for missing continuity-critical subjects used by the scene.
5. `production-diagrams` only if geography, blocking, eyelines, or axis remain hard to communicate in prose.
6. `shot-design`.
7. `shot-list`.
8. `storyboard-prompts` using the progressive storyboard stages when the scene needs more than a single anchor frame.
9. `generation-pack`.
10. Run the requested video adapter, plus a still-image adapter if generated keyframes are needed.
11. `prompt-qc`.
12. If multiple generated candidates exist for a shot or storyboard panel, run `take-selection` before treating one as approved.
13. If the user asks to render the scene through ComfyUI, run `comfyui-handoff` and then follow the ComfyUI Generate playbook for these shot IDs only. Use `take-selection` on generated alternatives before editorial work treats a take as approved.

Done when every shot has a dramatic job, continuity, duration, readable geography, motivated camera behavior, and a self-contained generation prompt when prompts were requested. If rendering was requested, each rendered result is traceable to its shot ID, take ID when reviewed, and prompt ID.
