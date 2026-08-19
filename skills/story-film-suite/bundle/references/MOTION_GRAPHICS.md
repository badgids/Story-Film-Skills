# Motion Graphics

Motion graphics are timeline assets with stable identity, not one-off filter strings.

Use `GFX-###` IDs and `05_post/graphics/graphics.json`.

A graphics package may contain:

- title cards
- lower thirds
- location straps
- watermarks and bugs
- end cards
- letterbox or framing treatments
- text overlays
- subtitle presentation styles
- fades
- clip-to-clip transitions
- campaign calls to action

Example:

```json
{
  "schema_version": 1,
  "input": "05_post/masters/picture.mp4",
  "output": "05_post/finished/picture_with_graphics.mp4",
  "graphics": [
    {"gfx_id":"GFX-001","type":"lower-third","start":2.0,"end":6.0,"text":"Pippa Pebblehoof","secondary":"The goat who looked beyond the fence","position":"lower-left","style":{}}
  ]
}
```

## Design rules

- exact names and release text come from verified project facts;
- overlays must respect title-safe and subtitle-safe regions;
- reusable style values should come from the project design system;
- lower thirds and watermarks should not obscure required story information;
- animation exists to support hierarchy and timing, not to decorate every cut;
- final graphics are subject to delivery QC.

Use `scripts/motion_graphics.py` for FFmpeg-backed deterministic overlays and transitions. Use the programmatic-video subsystem when the requested motion design needs richer animation or code-driven composition.
