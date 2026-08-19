# Create a Feature Film

[Documentation home](../README.md) | [Workflows](../README.md#2-main-workflows) | [Feature-scale production](../production/feature-scale.md)

## Table of contents

- [Why a feature is different](#why-a-feature-is-different)
- [Main phases](#main-phases)
- [Sequence rule](#sequence-rule)
- [Global gates](#global-gates)
- [Completion rule](#completion-rule)

## Why a feature is different

A feature film can have hundreds of shots and thousands of production records.

A local LLM should not load all of that detail at the same time.

Story-Film Skills uses sequences and context shards to keep the working set small.

## Main phases

1. Develop the story.
2. Write and revise the screenplay.
3. Freeze the screenplay baseline.
4. Divide the screenplay into `SEQ-###` production sequences.
5. Build global identity references.
6. Produce one sequence at a time.
7. Generate and approve media in bounded batches.
8. Reconcile each sequence into the main edit.
9. Run global continuity and editorial gates.
10. Master the film.
11. Run delivery checks.
12. Run the final completeness audit.

## Sequence rule

Each active screenplay scene belongs to one sequence.

Use the sequence context shard for normal agent work.

Do not load every detailed feature file when one shard is enough.

## Global gates

Some checks need the whole story at low resolution.

Examples are long-range continuity, whole-film editorial order, audio mastering, delivery QC, and final completeness.

Use indexes and reports first.

Open detailed sequence files only when the global report points to them.

## Completion rule

Do not call a feature complete because `film_master.mp4` exists.

Run `completeness_audit.py`.

The audit must have no deterministic blockers.

The user must still accept the creative result.

## Related pages

- [Sequences and shards](../production/sequences-and-shards.md)
- [Resource-safe generation](../generation/resource-safe.md)
- [Editorial reconciliation](../postproduction/editorial.md)
- [Final completeness audit](../release/completion.md)
