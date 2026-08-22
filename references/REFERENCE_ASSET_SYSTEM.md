# Reference Asset System

Reference assets are production state. They reduce identity drift, preserve location geometry, and keep separate generation tasks compatible.

## Stable reference IDs

Every approved reference uses `REF-###` and one explicit role.

Common roles:

- character identity master
- character turnaround
- character expression sheet
- wardrobe variant
- location master
- location coverage sheet
- prop master
- vehicle master
- visual moodboard
- style board
- color reference
- composition reference
- first frame
- last frame
- motion reference
- voice identity reference
- music identity reference

One asset may serve more than one role only when each inherited trait is stated explicitly.

## Canonical identity versus scene state

Canonical identity stays stable unless canon changes:

- face and body identity
- age range
- defining marks
- base proportions
- core prop geometry
- location architecture
- voice identity

Scene state may change by scene:

- expression
- pose
- dirt, blood, sweat, or damage
- wardrobe variant
- carried props
- time of day
- lighting
- temporary hair or makeup state

A scene prompt may alter scene state while preserving identity. It may not silently rewrite identity.

## Character reference package

Create only views justified by planned production.

Useful coverage may include:

- clean full-body master with safe edge margin
- face identity view
- left profile
- right profile
- rear view
- difficult recurring expressions
- approved wardrobe variants
- prop-holding pose when the prop changes silhouette

Prefer multiple views derived from one approved anchor or one coherent multi-view generation over unrelated text-only rerolls.

## Character turnaround plan

When a turnaround is useful, write `03_preproduction/references/character/<CHAR-ID>-turnaround-plan.json`.

Minimum fields:

```json
{
  "character_id": "CHAR-001",
  "identity_ref": "REF-001",
  "views": ["full-front", "face", "left-profile", "right-profile", "rear"],
  "framing": "full body with safe margin",
  "must_preserve": [],
  "may_vary": ["pose-neutralization"],
  "generation_mode": "single coherent sequence or anchored edits",
  "selection_rules": ["sharp", "uncropped", "distinct view", "identity-consistent"]
}
```

Do not claim an unseen side is verified when the source material cannot establish it. Mark inferred coverage as `inferred` until approved.

## Location coverage

A location package must answer production geography, not just appearance.

Useful coverage may include:

- primary establishing direction
- reverse direction
- important side directions
- entrances and exits
- practical light sources
- fixed architectural details
- important furniture or obstacles
- optional overhead blocking plan

When only one source view exists, distinguish `verified geometry` from `generated extrapolation`.

Write `03_preproduction/references/location/<LOC-ID>-coverage-plan.json` for complex locations.

## Prop coverage

For continuity-critical props, lock:

- scale relative to hand or body
- material
- color
- unique marks or damage
- moving parts
- readable text
- state variants such as open, closed, broken, empty, or full

## Contact-sheet plan

When several candidate views or versions exist, create `03_preproduction/references/contact_sheet_plan.json`.

Each requested panel must state:

- reference or candidate ID
- subject ID
- role
- view or expression
- reason it earns a panel
- quality checks

Reject near-duplicates, blurred frames, cropped continuity-critical parts, and panels that cannot be mapped back to their source candidate.

## Reference manifest

Store reference records in `03_preproduction/references/reference_manifest.json`.

Example:

```json
{
  "ref_id": "REF-001",
  "role": "character identity master",
  "subject_ids": ["CHAR-001"],
  "path": "03_preproduction/references/character/REF-001.png",
  "status": "approved",
  "version": 1,
  "inherits": [],
  "must_preserve": ["face identity", "scar under left eye"],
  "must_not_be": ["scar under right eye"],
  "may_vary": ["expression", "pose"],
  "drift_risks": ["hair length tends to increase in side views"],
  "source": "generated",
  "rights_note": "project-created asset",
  "verification": "approved by project",
  "notes": ""
}
```

## Exclusions and drift risks

`must_not_be` is a canonical exclusion inherited from approved identity or world facts. A reference or prompt may not silently contradict it.

`drift_risks` is a production observation about recurring generation failure. It is not canon. Record risks such as mirrored scars, changing hair length, disappearing jewelry, or geometry drift so later local generations can defend against known failure without rewriting identity.

## Provenance and rights

Record whether a reference is user-owned, licensed, public-domain, generated, or inspiration-only. An inspiration image is not automatically an identity source.

## Approval rule

Exploration may use draft references. Continuity-critical production prompts should use approved references whenever possible.

Never silently replace an approved identity master. Create a new version, record the reason, and calculate downstream impact.
