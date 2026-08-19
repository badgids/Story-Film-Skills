# Production Health

[Documentation home](../README.md) | [Up: Feature-scale production](feature-scale.md) | [Continuity](continuity.md)

## Table of contents

- [Purpose](#purpose)
- [Run the report](#run-the-report)
- [Status meanings](#status-meanings)

## Purpose

The health report gives a quick view of known production state.

It reads durable files. It does not ask the LLM to guess.

## Run the report

```bash
python scripts/production_health.py PROJECT
```

Use strict mode when a blocker must fail a gate:

```bash
python scripts/production_health.py PROJECT --strict
```

The report is written to:

```text
00_project/health_report.json
00_project/health_report.md
```

## Status meanings

`healthy` means no known deterministic blocker was found.

`attention` means warnings need review.

`blocked` means at least one known gate needs repair.

A healthy report does not mean the film is artistically good.

## Related pages

- [Feature-scale production](feature-scale.md)
- [Final completeness audit](../release/completion.md)
