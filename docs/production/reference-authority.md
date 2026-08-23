# Reference Authority

[Documentation home](../README.md) | [Up: Production](../README.md#3-feature-film-production)

## Table of contents

- [Authority scopes](#authority-scopes)
- [Multi-view atlases](#multi-view-atlases)
- [Workflow selection](#workflow-selection)
- [Related pages](#related-pages)

## Authority scopes

A reference can control identity without controlling composition. Use `authority_scopes` and `must_not_control` from `references/REFERENCE_AUTHORITY.md`. This prevents a character sheet from becoming an accidental camera layout or a location photo from becoming frame-zero composition.

## Multi-view atlases

Mark a grid as `layout_is_reference_only` when its cell arrangement is not production composition. Stage authoritative images with contain/fit behavior rather than destructive stretching.

## Workflow selection

Reference authority does not select the ComfyUI graph.

Choose the complete workflow separately through the workflow catalog. Then bind `REF-###` and `MEDIA-###` inputs only to the roles that the selected workflow actually exposes. A selected character-sheet or orbit workflow does not expand the authority scope of the reference itself.

## Related pages

- [Reference sheets](reference-sheets.md)
- [Temporal continuity](temporal-continuity.md)
- [Choose ComfyUI workflows](../generation/workflow-selection.md)
