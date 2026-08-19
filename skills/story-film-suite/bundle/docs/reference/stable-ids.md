# Stable IDs

[Documentation home](../README.md) | [Up: Project layout](project-layout.md) | [Next: Commands](commands.md)

## Table of contents

- [Purpose](#purpose)
- [Common IDs](#common-ids)
- [Rules](#rules)

## Purpose

A stable ID gives one production item one durable identity.

Do not identify important work only by filename or list position.

## Common IDs

Examples include:

```text
SCN-###    scene
LINE-###   screenplay line or action unit
SHOT-###   shot
TAKE-###   generated take
MEDIA-###  registered media
SEQ-###    feature production sequence
CONT-###   long-range continuity anchor
JOB-###    generation job
BATCH-###  generation batch
UNIT-###   production work unit
DEC-###    production decision
GFX-###    motion graphic
COMP-###   programmatic composition
CONTENT-### campaign derivative
CLAIM-###  factual/public claim
SRC-###    source evidence
```

## Rules

1. Keep an ID stable after creation.
2. Do not reuse a retired ID for a different item.
3. Reference IDs across manifests instead of copying ambiguous names.
4. Use dependency tracking when a changed item makes downstream work stale.

## Related pages

- [Project layout](project-layout.md)
- [Feature-scale production](../production/feature-scale.md)
