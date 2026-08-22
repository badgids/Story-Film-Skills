# Executable Production Plan

Use when the user wants a shooting script, detailed performance blocking, executable scene plan, or proof that a screenplay is fully covered for generation.

1. `continuity-check`: establish the approved narrative baseline.
2. Ensure `02_screenplay/scene_manifest.json` and `02_screenplay/line_manifest.jsonl` are current.
3. `production-capabilities`: record the selected production route's real locations, actions, camera behavior, audio/sync features, limits, and unknowns.
4. `production-breakdown` and `director-book` for the requested scene scope.
5. `previz-plan` when geography or movement is non-trivial.
6. `performance-blocking`: annotate playable performer state, movement, actions, and estimated timing.
7. `shot-design`: design coverage and link shots to `LINE-###` source units where applicable.
8. `shot-list`: compile practical setups.
9. `dialogue-voice` when audible dialogue is in scope. Preserve `LINE-###` and exact text.
10. `dialogue-audio-authority` when a dialogue take is approved. Bind the exact `MEDIA-###`, speaker, start time, and SHA-256 used for generation/review.
11. `dialogue-timing-preflight` before expensive dialogue-heavy generation. An impossible line returns to shot design; never silently speed, crop, rewrite, or reassign it.
12. `shooting-script`: compile positions, moves, actions, shot IDs, dialogue, and timing into one portable execution record.
13. `production-coverage`: prove the requested scope has no missing machine-readable line, shot, voice, or blocking links.
14. If measured speech or generated-media timing later changes, refresh only affected units and rerun coverage.

Done when the requested scope is executable from saved artifacts and the production coverage report is ready or names an explicit blocker.
