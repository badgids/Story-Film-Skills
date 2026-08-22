---
name: reference-assets
description: Plan, create, version, approve, and quality-check visual and audio reference assets for characters, locations, props, styles, keyframes, voices, and music while separating canonical identity from scene state.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Reference Assets

## Workflow

1. Read the standalone contract, core contract, reference asset system, canon, continuity, planned scenes, shot needs, and current reference manifest.
2. Identify only continuity risks that justify a reference asset.
3. Assign stable `REF-###` IDs and one explicit role per reference record.
4. Write or update `03_preproduction/references/reference_manifest.json`.
5. Write model-neutral reference briefs for missing character, location, prop, style, keyframe, voice, or music references.
6. For character turnarounds or location coverage, write the native coverage-plan JSON described in the reference asset system.
7. When several candidates must be reviewed, write `contact_sheet_plan.json` with panel roles and acceptance checks.
8. Use the appropriate model adapter to create prompt documents when generation prompts are requested.
9. Separate canonical identity from scene-state variants such as expression, dirt, wardrobe, damage, props, and lighting.
10. Mark references `draft`, `approved`, `superseded`, or `rejected`. Never silently replace an approved identity master.
11. If an approved reference changes, run `project-impact` before continuing downstream.

## Quality gate

A production reference is approvable only when its continuity-critical traits are inspectable, its role is clear, its provenance is recorded, and its crop or framing does not hide required identity information.

## Done

Every continuity-critical subject has an approved reference or an explicit missing-reference record, and downstream prompts can state exactly what to preserve and what may vary.
