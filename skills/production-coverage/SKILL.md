---
name: production-coverage
description: Audit machine-readable screenplay-to-production coverage so scenes, screenplay lines, dialogue cues, blocking, shots, and shooting-script units cannot be silently dropped during long-form planning.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Production Coverage

## Workflow

1. Read core contract and `PRODUCTION_COVERAGE.md`.
2. Run `python scripts/production_coverage.py <project>` for the requested scope.
3. Inspect missing dialogue cues, missing shot coverage, blocking gaps, text drift, unresolved shot references, and timing conflicts.
4. Fix the smallest upstream artifact that owns the error. Do not invent coverage inside the report.
5. Re-run until `ready` is true for the intended production scope or record the blocker.

## Done

The report proves every required machine-readable screenplay unit in scope has the expected production links, with no exact-dialogue drift or unresolved production references.
