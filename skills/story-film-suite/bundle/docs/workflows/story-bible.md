# Build a Story Bible

[Documentation home](../README.md) | [Up: Main workflows](../README.md#2-main-workflows)

## Table of contents

- [Recommended workflow](#recommended-workflow)
- [Character depth](#character-depth)
- [Baseline versus current state](#baseline-versus-current-state)
- [Related pages](#related-pages)

Story-Film does not store a project bible inside one giant skill file.

A Story-Film bible is a small set of durable project files:

```text
00_project/brief.md
00_project/canon.json
01_story/story_bible.md
01_story/characters.md
01_story/world.md
01_story/story_state.json
03_preproduction/visual_bible.md   optional
```

This separation lets permanent facts stay stable while current injuries, knowledge,
possessions, and relationships change through the story.

## Recommended workflow

Use the `story-bible-development` playbook.

The agent develops:

1. premise and dramatic architecture;
2. one consequential character at a time;
3. recurring world rules and locations;
4. mutable starting state only after it is settled;
5. visual era or capture rules only when visual production is in scope.

## Character depth

A developed recurring character can have:

- story function;
- objective and pressure behavior;
- canonical visual identity;
- speech signature;
- movement signature;
- stillness signature;
- baseline ensemble behavior;
- private knowledge and relevant backstory;
- arc start and target.

Unknown creative choices stay open. The agent must not invent detailed canon just to fill
every field.

## Baseline versus current state

A normal relationship pattern belongs in canon.

A relationship that changes because of `SCN-###` belongs in `story_state.json`.

The same rule applies to injuries, possessions, current location, knowledge, and other
chronology-sensitive facts.

## Related pages

- [Character performance](../production/character-performance.md)
- [Visible dialogue synchronization](../production/dialogue-sync.md)
- [Project layout](../reference/project-layout.md)
