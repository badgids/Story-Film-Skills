# Production Coverage Contract

A long-form project is not generation-ready merely because it has many shot briefs. Coverage must prove that the approved screenplay scope survives the planning hierarchy.

Use `scripts/production_coverage.py` to generate a report from machine-readable project artifacts.

## Coverage dimensions

For each `LINE-###` record in `02_screenplay/line_manifest.jsonl`, check as applicable:

- scene identity resolves
- dialogue text remains exact across voice cue and shooting script
- audible dialogue has a voice cue
- on-screen dialogue or action has planned shot coverage
- on-screen performer work has a blocking record when blocking is required
- shooting-script references resolve to existing shots
- measured speech does not exceed a locked planned unit duration unless overlap or intentional timing is recorded

## Output

- required visible dialogue has the same `LINE-###` and speaker in the shooting script and at least one covering shot
- required visible speakers are actually shot subjects
- visible-dialogue timing and hold-through-line policy fit the covering shot
The script can write:

- `03_preproduction/production_coverage.json`
- `03_preproduction/production_coverage.md`

The JSON report contains totals, missing coverage, text drift, unresolved references, timing conflicts, visible-dialogue sync conflicts, and a `ready` boolean.

## Scope rule

Coverage can be checked for the whole project or a selected scene set. Feature projects should check one approved sequence at a time during production and run a global check before final packaging.

## Creative limitation

A complete coverage report proves traceability, not quality. It cannot prove that the coverage is dramatically effective, the camera is tasteful, or the performance is convincing.
