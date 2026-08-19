# Portable Previz Schema

Previz planning in Story-Film Skills is tool-neutral. It describes spatial intent without depending on a specific 3D application or ComfyUI node pack.

## Output

Create one JSON file per scene when previz is useful:

`03_preproduction/previz/SCN-###.json`

## Coordinate convention

Use meters by default.

- X: screen-world left and right
- Y: vertical
- Z: depth
- positive rotations use degrees

The coordinate system is a planning convention, not a promise about a downstream tool's native axes.

## Minimum schema

```json
{
  "schema_version": 1,
  "scene_id": "SCN-001",
  "units": "meters",
  "space": {
    "description": "",
    "verified_geometry": [],
    "assumed_geometry": [],
    "bounds": null,
    "entrances": [],
    "exits": [],
    "obstacles": [],
    "practical_lights": []
  },
  "actors": [],
  "props": [],
  "paths": [],
  "eyelines": [],
  "camera_setups": [],
  "cut_order": [],
  "continuity_notes": [],
  "open_questions": []
}
```

## Actor record

```json
{
  "character_id": "CHAR-001",
  "start": {"x": 0, "y": 0, "z": 0, "facing_deg": 0},
  "objective": "reach the door without revealing the key",
  "end": {"x": 2.5, "y": 0, "z": 4, "facing_deg": 90}
}
```

## Path record

```json
{
  "path_id": "PATH-001",
  "character_id": "CHAR-001",
  "points": [
    {"x": 0, "y": 0, "z": 0, "beat": "start"},
    {"x": 1.2, "y": 0, "z": 2.0, "beat": "hesitates"}
  ]
}
```

## Camera setup

```json
{
  "shot_id": "SHOT-001",
  "position": {"x": 0, "y": 1.6, "z": -4},
  "target": {"type": "character", "id": "CHAR-001"},
  "framing": "medium",
  "movement": "static",
  "movement_reason": "nothing spatial changes before the reveal",
  "axis_side": "A",
  "screen_direction": "left-to-right",
  "notes": ""
}
```

## Accuracy rule

Use exact coordinates only when they are known or intentionally chosen for planning. Otherwise use relative placement descriptions or mark coordinates as approximate.

Never convert an aesthetic reference image into fake architectural measurements.
