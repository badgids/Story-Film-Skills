# Visible Dialogue Synchronization

[Documentation home](../README.md) | [Up: Production](../README.md#3-feature-film-production)

## Table of contents

- [Required links](#required-links)
- [Timing](#timing)
- [End-frame handoff](#end-frame-handoff)
- [Validation](#validation)
- [Related pages](#related-pages)

Use visible-dialogue synchronization when the viewer must see a character speak an exact
screenplay line.

Story-Film stores the requirement as model-neutral production intent. A local adapter or
ComfyUI workflow decides how to execute it.

## Required links

A required visible line keeps the same:

- `LINE-###`;
- `CHAR-###` speaker;
- exact screenplay text;
- speech timing when measured;
- covering `SHOT-###`;
- mouth-visibility requirement;
- cut policy.

Off-screen dialogue and voice-over do not automatically require lip sync.

## Timing

Before voice audio exists, use estimated timing.

After voice audio exists, measured speech duration should flow into the shooting script and
relevant shot brief. Do not silently shorten the line to fit a generation limit.

## End-frame handoff

A shot can define an exact end-frame state when the next shot, a last-frame-conditioned local
workflow, match on action, or editorial handoff depends on the final pose, prop state, gaze,
camera state, or frame reference.

Most shots do not need this field.

## Validation

Run:

```bash
python scripts/dialogue_sync.py PROJECT
python scripts/production_coverage.py PROJECT
python scripts/validate_story_project.py PROJECT
```

These checks prove the production links and timing contract. They do not prove that generated
mouth motion looks convincing. Check that after generation with media QC.

## Related pages

- [Character performance](character-performance.md)
- [Build a story bible](../workflows/story-bible.md)
- [Project layout](../reference/project-layout.md)
