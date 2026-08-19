# Sequence Management

[Feature-scale contract](FEATURE_SCALE_PRODUCTION.md) | [Documentation home](../docs/README.md)

`00_project/sequence_manifest.json` divides the approved screenplay into `SEQ-###` production units.

Each screenplay scene belongs to exactly one active sequence. A sequence can contain several related scenes. The sequence is the normal unit for preproduction, generation, review, and editorial reconciliation.

Allowed status values are `planned`, `ready`, `in-production`, `generated`, `editing`, `approved`, `blocked`, and `retired`.

Use:

```bash
python scripts/sequence_manager.py init PROJECT --chunk-size 5
python scripts/sequence_manager.py set PROJECT SEQ-001 in-production
python scripts/sequence_manager.py next PROJECT
python scripts/sequence_manager.py validate PROJECT
```

The automatic chunk size is only a starting point. A human or agent can edit the sequence boundaries when story, location, cast, production method, or model needs make another grouping better.
