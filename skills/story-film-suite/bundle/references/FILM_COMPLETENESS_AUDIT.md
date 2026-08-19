# Final Film Completeness Audit

[Release delivery](RELEASE_DELIVERY.md) | [Feature-scale contract](FEATURE_SCALE_PRODUCTION.md) | [Documentation home](../docs/README.md)

A film is not complete because a master file exists.

Run:

```bash
python scripts/completeness_audit.py PROJECT --strict
```

The audit checks the final control evidence, including:

- required screenplay and production files
- approved feature sequences
- production coverage
- long-range continuity when present
- editorial reconciliation
- failed generation state
- stale dependency state
- unsettled resource handoff state
- rich-document Markdown companions
- final master existence and FFprobe stream evidence when FFprobe is available
- delivery and release readiness state

A `complete: true` result means the deterministic completion gates passed. It does not prove that the film is artistically good or that an audience will like it.
