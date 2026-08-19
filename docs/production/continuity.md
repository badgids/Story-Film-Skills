# Long-Range Continuity

[Documentation home](../README.md) | [Up: Feature-scale production](feature-scale.md) | [Sequences and shards](sequences-and-shards.md)

## Table of contents

- [Why this exists](#why-this-exists)
- [Continuity anchor](#continuity-anchor)
- [Observation](#observation)
- [Run the check](#run-the-check)

## Why this exists

A feature can return to a fact long after the fact first appears.

Examples include an injury, a missing prop, a costume state, a secret, or a relationship change.

## Continuity anchor

Create a `CONT-###` anchor.

The anchor names the source sequence.

The anchor names later target sequences.

The anchor states what must still be true.

## Observation

When you produce a target sequence, record the observed state.

Link evidence when possible.

Mark `intentional_change: true` when the story changed the state on purpose.

## Run the check

```bash
python scripts/long_range_continuity.py PROJECT --strict
```

Resolve missing observations and conflicts before the final feature gate.

## Related pages

- [Feature film](../workflows/feature-film.md)
- [Final completeness audit](../release/completion.md)
