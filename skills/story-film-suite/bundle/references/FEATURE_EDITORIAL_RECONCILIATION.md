# Feature Editorial Reconciliation

[Executable timeline](EXECUTABLE_TIMELINE.md) | [Feature-scale contract](FEATURE_SCALE_PRODUCTION.md) | [Documentation home](../docs/README.md)

The final timeline must reconcile approved shot state with feature sequence order.

Run:

```bash
python scripts/editorial_reconcile.py PROJECT --strict
```

The report checks:

- duplicate event IDs
- selected shots that are missing from the main timeline
- shot-to-sequence mapping
- sequence order that moves backward without an explicit editorial override
- duplicate shot placements that need review
- per-sequence event counts and durations

A deliberate nonlinear edit can use `editorial_order_override: true` on the event that crosses the normal sequence order. This records intent instead of hiding the exception.
