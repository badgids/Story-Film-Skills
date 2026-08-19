# Storyboard Development

Use when the user wants a visual board or motion-ready storyboard from approved story or screenplay material without necessarily rendering final shots.

1. Establish the approved screenplay/scene scope, director intent, continuity, visual bible, and required reference assets.
2. Read `STORYBOARD_PIPELINE.md`.
3. `storyboard-prompts`: create adaptive narrative anchors and the visual anchor board.
4. Expand only difficult or important anchors into sequence boards that expose blocking, eyelines, screen direction, match on action, and cut points.
5. Derive motion handoff records from approved sequence state.
6. Use still-image adapters only when the user wants generated storyboard panels. Generated panels remain takes until approved.
7. If multiple candidates are generated, use `take-selection` to record the approved panel/take.
8. Use `crew-review` for a board stage that repeatedly fails or for a consequential choice between two visual strategies.
9. Run continuity and prompt quality checks before handing the storyboard to video generation.

Done when the sequence can be understood from approved visual state, every expanded frame has a reason, and motion can be generated without inventing new blocking or continuity facts.
