---
name: dialogue-timing-preflight
description: Measure approved dialogue before expensive generation and block impossible clip timing without silently changing speech.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Dialogue Timing Preflight

## Procedure

Read `../../references/DIALOGUE_TIMING_PREFLIGHT.md`. Run `scripts/dialogue_timing_preflight.py PROJECT` before dialogue-heavy video batches.

## Done

Durable project state and deterministic validation agree before downstream generation continues.
