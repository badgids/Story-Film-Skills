# Create a Screenplay

[Documentation home](../README.md) | [Workflows](../README.md#2-main-workflows) | [Story to film](story-to-film.md)

## Table of contents

- [Output](#output)
- [Main steps](#main-steps)
- [Production IDs](#production-ids)
- [Verify dialogue](#verify-dialogue)

## Output

The main screenplay is `02_screenplay/screenplay.fountain`.

The production control files are `scene_manifest.json` and `line_manifest.jsonl`.

## Main steps

1. Approve the story or adaptation plan.
2. Write filmable action in present tense.
3. Keep dialogue character-specific.
4. Build `SCN-###` scene records.
5. Build `LINE-###` production records.
6. Update story state and continuity.
7. Revise the whole screenplay after the draft is complete.
8. Run the screenplay consistency verifier.
9. Freeze an approved baseline before expensive shot production.

## Production IDs

A screenplay line can flow into voice, blocking, shot, generation, and edit records.

Stable IDs keep that chain traceable.

## Verify dialogue

Run:

```bash
python3 scripts/screenplay_consistency.py /path/to/project
```

The verifier reads character names from project canon. It does not use a hardcoded character list. It checks exact dialogue text, dialogue order, and `CHAR-###` speaker identity.

If a character cue has a likely spelling error, the verifier reports the line and suggests the closest canonical cue.

See [Screenplay consistency](../../references/SCREENPLAY_CONSISTENCY.md).

## Related pages

- [Stable IDs](../reference/stable-ids.md)
- [Feature film](feature-film.md)
- [Long-range continuity](../production/continuity.md)
