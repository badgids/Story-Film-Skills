# Screenplay to Film Package

1. `continuity-check`: establish a clean baseline.
2. Ensure `scene_manifest.json` and `line_manifest.jsonl` are synchronized with the approved screenplay.
3. `production-breakdown`: one breakdown per scene.
4. `director-book`: scene engine, performance, blocking, visual, rhythm, light, transition, and sound strategy.
5. `production-capabilities`: record what the selected production route can actually execute or only conditionally attempt.
6. `visual-bible`: establish persistent visual language when the project needs one.
7. `reference-assets`: create only continuity-critical references.
8. `production-diagrams` or `previz-plan` only when relationship, timeline, geography, blocking, eyelines, shot flow, or dependency structure benefits from them.
9. `performance-blocking`: compile playable movement and action for production-relevant `LINE-###` units.
10. `shot-design` and `shot-list`: create coverage tied back to source line IDs.
11. `storyboard-prompts`: develop only the visual depth each scope needs.
12. `dialogue-voice`, `score-plan`, and `sound-design` as needed. Preserve line IDs and exact dialogue.
13. `shooting-script`: compile line, blocking, camera, and timing into a portable execution plan.
14. `production-coverage`: prove that the requested screenplay scope has not been silently dropped.
15. `generation-pack`, selected model adapters, and `prompt-qc`.
16. If actual generation occurs, register concrete media with `asset-approval`; run `media-qc`, then `take-selection` for picture candidates.
17. `edit-plan` and `editorial-package` as requested.
18. If actual ComfyUI generation is requested, run `comfyui-handoff` and the ComfyUI Generate playbook by approved scope.
19. If the request is for the actual finished film rather than a film package, continue with the `film-finishing` playbook.

When the requested endpoint includes editable Kdenlive/Shotcut projects or deterministic FFmpeg/MLT/ImageMagick manipulation, run `media-editing-and-project-export` after the canonical editorial state exists.

Done when every required screenplay unit maps through its production path, the capability registry contains no hidden assumptions, production coverage is ready for the requested scope, and generated alternatives have explicit approval state when present.
