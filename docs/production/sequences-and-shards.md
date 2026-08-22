# Sequences and Context Shards

[Documentation home](../README.md) | [Up: Feature-scale production](feature-scale.md) | [Next: Production health](health.md)

## Table of contents

- [Sequence](#sequence)
- [Create sequences](#create-sequences)
- [Context shard](#context-shard)
- [Build shards](#build-shards)
- [Agent rule](#agent-rule)

## Sequence

A sequence is a bounded part of the feature production.

Its stable ID is `SEQ-###`.

A sequence contains one or more `SCN-###` scenes.

Each active scene must belong to exactly one sequence.

## Create sequences

After the scene manifest exists, run:

```bash
python scripts/sequence_manager.py init PROJECT --chunk-size 5
```

The chunk size is a starting hint.

Edit the boundaries when story or production needs require a better grouping.

Set status with:

```bash
python scripts/sequence_manager.py set PROJECT SEQ-001 in-production
```

## Context shard

A context shard is a small package of records related to one sequence.

It includes matching scene, line, shot, blocking, generation, take, media, and timeline records when those records exist. It also includes only the relevant character/location/prop canon, relationship baselines, and current character/prop story state for the sequence.

## Build shards

Run:

```bash
python scripts/context_shards.py build PROJECT
```

Open:

```text
00_project/shards/SEQ-001/context.md
```

for a human view.

Open `context.json` for machine work.

## Agent rule

Load the shard first.

Do not load the whole film state unless a global gate needs it.

## Related pages

- [Feature-scale production](feature-scale.md)
- [Stable IDs](../reference/stable-ids.md)
