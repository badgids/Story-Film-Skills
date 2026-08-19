# Long-Range Continuity

[Feature-scale contract](FEATURE_SCALE_PRODUCTION.md) | [Documentation home](../docs/README.md)

A feature film can contain continuity facts that return many sequences later. Record those facts as `CONT-###` anchors in `03_preproduction/continuity/anchors.jsonl`.

Example:

```json
{"anchor_id":"CONT-001","kind":"injury","subject_id":"CHAR-001","source_sequence":"SEQ-002","target_sequences":["SEQ-007","SEQ-011"],"expected_state":"left arm bandaged"}
```

Record observed state in `observations.jsonl`.

```json
{"anchor_id":"CONT-001","sequence_id":"SEQ-007","observed_state":"left arm bandaged","evidence":"SHOT-231","intentional_change":false}
```

Run:

```bash
python scripts/long_range_continuity.py PROJECT --strict
```

A changed state is allowed when the story changes it on purpose. Mark that observation with `intentional_change: true` and preserve the story evidence for the change.
