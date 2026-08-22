---
name: comfyui-binding-audit
description: Audit reference-to-workflow bindings so prompt ordinals, REF/MEDIA identities, staged files, hashes, and actual graph nodes cannot silently drift.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Comfyui Binding Audit

## Procedure

Run `scripts/comfy_binding_audit.py PROJECT` before queuing a reference-driven graph. A binding mismatch blocks generation.

## Done

Durable project state and deterministic validation agree before downstream generation continues.
