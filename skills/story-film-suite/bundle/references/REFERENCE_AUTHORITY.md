# Reference Authority Contract

A reference asset may be authoritative for one production concern without being authoritative for every visible property in the image.

## Scopes

Use zero or more `authority_scopes` on a `REF-###` manifest entry:

- `frame-zero-composition`
- `temporal-continuity`
- `character-identity`
- `location-identity`
- `style-world`
- `prop-or-context`

Use `must_not_control` to state concerns that a renderer must not inherit from that reference, such as `composition`, `camera`, `location-geometry`, `character-identity`, or `style`.

`drift_risks` remains an observation about generator failure. It is not canon and it is not an authority scope.

## Atlas semantics

A multi-view sheet may declare:

```json
{
  "atlas": {
    "semantic": "single-entity-multiview",
    "layout_is_reference_only": true,
    "views": ["front", "right", "rear", "left", "detail"]
  }
}
```

The grid layout itself is never a camera-composition instruction when `layout_is_reference_only` is true.

## Staging

Authoritative images should normally be staged with aspect-safe contain/fit behavior and padding. Do not stretch identity references or crop away required identity features merely to fill a model input rectangle.
