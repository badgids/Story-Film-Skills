# Production Health

[Feature-scale contract](FEATURE_SCALE_PRODUCTION.md) | [Documentation home](../docs/README.md)

`production_health.py` creates a deterministic status report from durable project state.

It checks known blockers such as:

- stale artifacts
- blocked sequences
- blocked pipeline progress
- failed resource handoff state
- failed offline generation jobs
- incomplete production coverage
- failed long-range continuity
- failed editorial reconciliation
- missing rich-document Markdown companions

Run:

```bash
python scripts/production_health.py PROJECT
python scripts/production_health.py PROJECT --strict
```

The report does not judge artistic quality. It reports known production state only.
