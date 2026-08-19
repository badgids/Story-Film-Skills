# Final Film Completeness Audit

[Documentation home](../README.md) | [Up: Feature film](../workflows/feature-film.md) | [Next: Release campaign](campaign.md)

## Table of contents

- [Purpose](#purpose)
- [What the audit checks](#what-the-audit-checks)
- [Run the audit](#run-the-audit)
- [What a pass means](#what-a-pass-means)

## Purpose

A master file can exist while the project is still incomplete.

The completeness audit checks the evidence that must exist before Story-Film Skills can call a feature production complete.

## What the audit checks

The audit can check:

- required project control files;
- approved or retired feature sequences;
- production coverage;
- long-range continuity results;
- editorial reconciliation;
- delivery QC;
- release state;
- failed ComfyUI batches;
- stale artifacts;
- blocked pipeline state;
- resource handoff state;
- Markdown companions for rich documents;
- final master existence and size;
- video and audio streams when FFprobe is available.

## Run the audit

```bash
python scripts/completeness_audit.py PROJECT check
```

Outputs:

```text
06_release/completeness_audit.json
06_release/completeness_audit.md
```

## What a pass means

A pass means that the declared deterministic production evidence is complete.

It does not mean that the film is artistically good. It does not predict audience response.

## Related pages

- [Production health](../production/health.md)
- [Editorial](../postproduction/editorial.md)
- [Release campaign](campaign.md)
