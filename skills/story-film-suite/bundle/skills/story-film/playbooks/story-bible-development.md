# Story Bible Development

Use when the requested endpoint is a durable Story-Film story bible, character/world lock, or deep cast/world development rather than a finished screenplay or film.

Story-Film uses a distributed bible. Do not create a project-specific installable skill as a second canon database.

1. `story-brief`: capture title, format, premise, dramatic question, genre/tone, constraints, must-have material, and open decisions.
2. Use `documented-creative-discovery` only for consequential unresolved creative decisions. Resolve discoverable facts from project files or tools instead of interviewing the user about them.
3. `story-architecture`: write the logline and story bible, including thematic tension and recurring narrative engines when they genuinely apply.
4. `character-bible`: develop one consequential character at a time. Lock identity, speech, movement, stillness, relationship baselines, and behaviorally relevant story facts.
5. `world-bible`: define recurring locations, chronology, factions/institutions, technology or power access, social rules, and other constraints that later scenes depend on.
6. `story-state`: initialize or update only mutable facts that are already settled by the approved story material. Do not promote brainstorming possibilities into state.
7. `visual-bible` only when the endpoint includes visual production language, era treatments, capture behavior, or recurring visual rules.
8. `continuity-check`: resolve contradictions across canon, character, world, story, state, and visual rules.
9. Run `scripts/character_profiles.py <project>` and `scripts/validate_story_project.py <project>`.

Done when the requested bible scope is recoverable from `brief.md`, `canon.json`, `story_bible.md`, `characters.md`, `world.md`, `story_state.json`, and optional `visual_bible.md` without relying on chat history.
