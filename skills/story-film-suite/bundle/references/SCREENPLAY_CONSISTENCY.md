# Screenplay Consistency

Use `scripts/screenplay_consistency.py` to compare screenplay dialogue with project canon and `02_screenplay/line_manifest.jsonl`.

## Why this exists

Do not build a temporary verification script with a list such as `('ALICE', 'BOB')`.

A typed name can be wrong. A new character can also be missing from the list. The verifier must use project data instead.

## Source of character names

The verifier reads `00_project/canon.json`.

For each `CHAR-###`, it can use:

- `name`
- optional `screenplay_names`
- optional `aliases`
- the first word of `name` when that first name is unique in the project

Example:

```json
{
  "CHAR-002": {
    "name": "Elias Ruhn",
    "screenplay_names": ["ELIAS"]
  }
}
```

## What it checks

The verifier checks:

1. A Fountain dialogue cue resolves to one canonical character.
2. The screenplay and line manifest have the same number of dialogue blocks.
3. Spoken text matches exactly and in order.
4. The resolved character matches `character_id` in the line manifest.
5. A close spelling error is reported with a suggestion.

For example, if canon contains `Elias Ruhn` but the screenplay contains `EILIAS`, the verifier reports the unknown cue and suggests `ELIAS`. It does not keep searching for hours.

## Run it

```bash
python3 scripts/screenplay_consistency.py /path/to/project
```

A successful check prints the number of matching dialogue blocks.

## Important rule

File existence is not proof of screenplay completion. Run this verifier before the screenplay or screenplay-revision pipeline target is checkpointed.
