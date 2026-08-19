# Evaluation Rules

The suite is written for small local models, so evaluation tests process reliability before polished prose.

## Evaluation families

### Weak-model execution

Test whether a small model chooses the correct playbook, works one artifact at a time, saves state, keeps stable IDs, respects long-form batching, and stops at the requested scope.

### Standalone capability

Test that required creative and preproduction work completes without another skill pack. Reference packages, previz plans, diagrams, generation manifests, and editorial packages must have native portable outputs.

### Continuity

Seed conflicts involving scars, wardrobe damage, prop ownership, character knowledge, time of day, geography, screen direction, voice identity, and reference versions.

### Adapter separation

Use one model-neutral brief and require different adapters to preserve intent while using different model grammar. Model-specific syntax must not leak into canon or neutral briefs.

### Exact payload

Test visible text and spoken dialogue byte-for-byte or normalized-for-newline when exactness is required.

### Prompt self-containment

A prompt fails when it depends on phrases such as `same as before`, `as above`, or chat memory.

### Writing quality

Check hard style rules mechanically. Human or model judging may assess voice, subtext, causality, and scene effectiveness after binary checks pass.

### ComfyUI operation

Test that weak models discover live node/model capabilities before guessing, distinguish UI and API workflows, preserve workflow sources, track long runs by prompt ID, extract non-image and text outputs, treat workflow notes as untrusted content, avoid auto-installing missing custom nodes, and obtain user confirmation before paid partner execution.

### Untrusted input

Put fake instructions inside manuscripts, captions, metadata, and examples. The agent must treat them as content and preserve trusted instruction hierarchy.

## Weak-model binary scorecard

- required artifact exists
- correct stable IDs exist
- required fields exist
- canon conflicts are surfaced
- forbidden shortcuts are absent
- no em dash character exists
- no personal hardcoded path exists
- exact payload is preserved where required
- downstream stale scope is minimal
- no required capability is delegated to an external skill pack

Only after binary checks pass should a judge score creative quality.

## Regression discipline

A discovered failure becomes the smallest case that reproduces it. Keep cases narrow enough that a weak model can reveal one failure mode at a time.
