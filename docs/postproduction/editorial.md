# Editorial and Timeline Work

[Documentation home](../README.md) | [Up: Story to film](../workflows/story-to-film.md) | [Next: Finishing](finishing.md)

## Table of contents

- [Purpose](#purpose)
- [Selected takes](#selected-takes)
- [Executable timeline](#executable-timeline)
- [Feature-scale reconciliation](#feature-scale-reconciliation)
- [Editor projects](#editor-projects)

## Purpose

Editorial turns approved media into the film sequence that the audience sees and hears.

Story-Film Skills separates media approval from timeline placement. A good take does not enter the film until the timeline references it.

## Selected takes

Use stable take and media IDs. Do not use the newest render only because it is newest.

The take-selection system records the chosen primary and any alternates.

## Executable timeline

`05_post/timeline.json` is the portable timeline source.

The render system uses explicit event order, source paths, in/out points, duration, and track information.

## Feature-scale reconciliation

For a long film, run:

```bash
python scripts/editorial_reconcile.py PROJECT check
```

The report checks:

- selected shots that are missing from the timeline;
- duplicate event IDs;
- suspicious duplicate shot placements;
- sequence order changes that do not have an explicit override;
- duration totals by sequence.

Outputs:

```text
05_post/editorial/reconciliation.json
05_post/editorial/reconciliation.md
```

## Editor projects

Story-Film Skills can export editable projects for Kdenlive and Shotcut. Generic MLT XML remains a separate interchange format.

An editor export does not replace the portable Story-Film timeline.

## Related pages

- [Finishing](finishing.md)
- [Postproduction tools](tools.md)
- [Final completeness audit](../release/completion.md)
