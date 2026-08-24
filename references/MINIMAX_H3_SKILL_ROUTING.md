# MiniMax H3 Skill Routing

Story-Film uses a layered MiniMax H3 prompt stack.

## Authority order

1. Story-Film canon, continuity, reference authority, approved dialogue/audio, and the source brief.
2. The selected ComfyUI workflow and the H3 input mode it actually supports.
3. `h3-prompt-writing`, which controls final MiniMax H3 prompt structure.
4. At most one automatically selected style skill, unless the user explicitly requests a style blend.
5. Generic aesthetic enrichment.

A style skill may enrich subject design, action, camera, typography, transitions, sound, or pacing. It may not replace exact dialogue, invent brand facts, change identity authority, override the selected workflow, change requested duration, or alter required first/last-frame constraints.

## Required base skill

Every MiniMax H3 prompt uses:

`skills/h3-prompt-writing/SKILL.md`

Base modes use the three-field H3 structure. Ref2VA uses the six-section H3 structure. The Story-Film `minimax-h3` adapter adds project-specific continuity, reference, dialogue, and exact-audio requirements around that official-format base.

## Conditional style skills

| Skill | Use when | Do not auto-use for |
| --- | --- | --- |
| `minimalist-product-ad-generator` | Minimalist physical-product ads, e-commerce product films, product launches | General brand films, talking-head ads, narrative films |
| `3d-animation-short-generator` | Stylized 3D narrative animation with character and scene continuity | Photorealistic live action, one isolated clip |
| `papercraft-stop-motion-explainer` | Educational or knowledge content using layered handmade paper, diorama, pop-up, or cut-paper stop motion | Generic 2D animation or live action |
| `brand-promo-video-generator` | Verified brand/product/app/site promotional shorts and campaigns | Unverified brand claims or long narrative films |
| `music-video-subtitle-generator` | Music videos with locked lyrics, beat-aware shots, spatial lyric typography, or master-audio continuity | Ordinary captions or non-music promos |
| `co-op-game-intro-generator` | Two-player co-op menu/opening animation with player identities and UI interaction | Playable game development or generic title cards |
| `paper-collage-explainer-generator` | Explanatory narration using tactile paper collage, halftone layers, and cut-paper metaphor | Papercraft diorama when dimensional stop-motion staging is the main look |
| `handdrawn-live-video-generator` | Rough hand-drawn animation physically interacting with live-action scenes | Polished CG, horror jump scares, unrelated animation |

## Routing

Run:

```bash
python scripts/minimax_h3_skill_router.py --text "<brief or shot intent>"
```

The result always includes `h3-prompt-writing` as `base_skill`. `style_skill` is either one matching overlay or `null`.

An explicit user request for one of the eight style skills overrides automatic routing. Do not silently combine multiple style skills because a brief contains overlapping vocabulary. If the user explicitly wants a hybrid, record the requested overlays and resolve contradictions before prompt writing.

## Prompt file audit metadata

A Story-Film MiniMax H3 prompt file should record:

```text
adapter: minimax-h3
h3_base_skill: h3-prompt-writing
h3_style_skill: <skill-name-or-none>
```

Keep this routing metadata outside the final model prompt. The final H3 prompt itself must preserve the field and section structure required by `h3-prompt-writing`.
