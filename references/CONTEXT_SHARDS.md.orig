# Context Shards

[Feature-scale contract](FEATURE_SCALE_PRODUCTION.md) | [Documentation home](../docs/README.md)

Context shards stop a feature-film agent from loading the full project state for routine work.

Run:

```bash
python scripts/context_shards.py build PROJECT
```

The script writes one folder per sequence under `00_project/shards/SEQ-###/`.

Each shard contains:

- the sequence scene IDs
- related stable IDs
- only the matching scene, line, blocking, shot, generation, take, media, and timeline records that can be traced into that sequence
- hashes of source control files used to build the shard
- a short Markdown summary

Read the shard first. Open a full source file only when the shard points to it or a global validator needs it.
