---
name: reference-authority
description: Validate and preserve typed reference authority so identity, composition, location, style, and temporal references cannot silently control the wrong production concern.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Reference Authority

## Procedure

Read `../../references/REFERENCE_AUTHORITY.md`. Run `scripts/reference_authority.py PROJECT` before reference-driven generation. Keep authority model-neutral and map it only onto inputs the selected live workflow actually exposes.

## Done

Durable project state and deterministic validation agree before downstream generation continues.
