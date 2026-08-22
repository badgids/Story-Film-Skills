---
name: storyboard-prompts
description: Build progressive storyboards from narrative anchors through visual anchor frames and sequence boards, preserving staging, eyelines, screen direction, action continuity, visual identity, and motion handoff for selected shots.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Storyboard Prompts

## Workflow

1. Read core contract, `STORYBOARD_PIPELINE.md`, dramaturgy rules, film grammar, continuity, visual bible, reference manifest, shot briefs, and model routing.
2. Select adaptive narrative anchors. Choose only moments that establish, change, reveal, pressure, transition, or pay off something the sequence needs.
3. Write `03_preproduction/storyboards/anchors.jsonl` and keep `03_preproduction/storyboard_plan.md` as the human-readable index.
4. Build `03_preproduction/storyboards/beat_board.jsonl` from approved anchors. Lock shared identity, location, light-source logic, optical character, palette behavior, aspect ratio, and references before model adaptation.
5. Expand only anchors that need temporal clarification into `03_preproduction/storyboards/sequence_boards/`. Use the minimum frames needed to show start state, decisive action/gaze change, and end or cut state.
6. Check 180-degree axis, eyeline match, screen direction, match on action, prop handoffs, entrances/exits, and physical plausibility.
7. Write model-neutral still briefs to `04_generation/image_briefs.jsonl` and motion handoff records to `03_preproduction/storyboards/motion_handoff.jsonl` when video generation needs them. When a shot has `end_frame.required = true`, make that endpoint inspectable in the sequence board or motion handoff. If an approved last-frame image becomes authoritative, register it as a `REF-###` with role `last frame`.
8. Adapt with `krea-2` for exploratory boards or `qwen-image-2512` for locked production frames. Use `qwen-image-edit-2511` to revise an established frame while preserving approved identity or composition.
9. A generated panel is a candidate, not approval. If alternatives are generated, use `take-selection` before downstream work treats one as authoritative.

## Done

The storyboard advances progressively from approved narrative intent to readable visual state, difficult motion is exposed before video prompting, and every generated frame remains traceable to its anchor and shot.
