# Generated Media QC Contract

`04_generation/take_qc.jsonl` records evidence-based quality checks for generated candidate takes. It complements `take-selection` and does not replace human creative judgment.

## Record

```json
{
  "take_id": "TAKE-001",
  "shot_id": "SHOT-001",
  "checks": {
    "script_faithfulness": {"status": "pass", "evidence": ""},
    "character_identity": {"status": "pass", "evidence": ""},
    "background_continuity": {"status": "pass", "evidence": ""},
    "spatial_relationship": {"status": "pass", "evidence": ""},
    "human_action": {"status": "pass", "evidence": ""},
    "motion_smoothness": {"status": "pass", "evidence": ""},
    "physical_plausibility": {"status": "pass", "evidence": ""},
    "visual_artifacts": {"status": "pass", "evidence": ""},
    "dialogue_sync": {"status": "not-applicable", "evidence": ""},
    "subtitle_sync": {"status": "not-applicable", "evidence": ""}
  },
  "metrics": {},
  "overall": "pass",
  "notes": ""
}
```

Allowed check statuses:

- `pass`
- `warn`
- `fail`
- `not-applicable`
- `not-checked`

Allowed overall values are `pass`, `warn`, and `fail`.

## Automated evaluators

An optional evaluator may populate `metrics` with named values such as subject consistency, background consistency, motion smoothness, dynamic degree, or another measured score. Record the evaluator name and version when known.

Do not translate an arbitrary metric threshold into a creative verdict without a project-specific rule. Automated metrics can identify defects or drift, but they do not prove narrative quality.

## Selection gate

A take with `overall: fail` should not be selected unless `selections.json` records an explicit `qc_override` and reason. This makes a deliberate exception traceable.

## Review order

Check hard failures before taste:

1. script/action mismatch
2. wrong identity or required object
3. broken spatial or background continuity
4. impossible or visibly broken motion/physics
5. severe visual corruption or flicker
6. dialogue/subtitle sync defects
7. then compare performance, composition, emotional effect, and cut fit
