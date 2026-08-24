# Model Routing

Model routing is advisory. The selected ComfyUI workflow is the generation authority.

Read `WORKFLOW_SELECTION.md` first. Story-Film no longer asks the user to separately select a model family and then assemble checkpoints, VAEs, text encoders, LoRAs, audio models, and upscalers through a TUI.

Use the sections below to:

- describe what a workflow/model family is good at;
- rank or explain workflow choices in the numbered catalog;
- choose the correct prompt adapter after the user selects a workflow;
- recommend another workflow when the selected source has a documented limitation.

Do not let model routing override `00_project/workflow_preferences.json`.

## Qwen Image 2512

Use for production stills, character look development, locations, props, keyframes, title or poster images, and images containing exact visible text. It benefits from a complete natural-language image description.

## Qwen Image Edit 2511

Use when an existing image must remain recognizable while one or more controlled changes are made, or when elements from multiple images must be combined with explicit source roles.

## Krea 2

Use for look exploration, style search, moodboards, expressive stills, and style-reference-driven image generation. Use an exploratory prompt first when the visual direction is intentionally open. Use a locked prompt when production continuity matters.

## MiniMax H3

Use for audio-video generation where image, video, or audio references and synchronized sound are central. Workflow variants can cover text-to-audio-video, image-to-video, first/last-frame generation, reference-to-video/audio, chained generation, exact-audio routes, enhancement, and upscaling.

Every MiniMax H3 prompt must use `h3-prompt-writing` as the formatting base. Then route the brief through `references/MINIMAX_H3_SKILL_ROUTING.md` and `scripts/minimax_h3_skill_router.py` to select an optional style overlay. The eight style skills are conditional production grammars, not replacements for H3 syntax. Story-Film canon, reference authority, exact dialogue/audio, selected workflow, and duration remain authoritative.

## LTX

Use for production video workflows with explicit shot design, physical action, camera movement, lighting, dialogue, ambience, and music. The bundled library can contain more than one LTX generation or enhancement workflow.

## Wan 2.2

Use for compatible text-to-video, image-to-video, storyboard, and related video workflows when present in the selected workflow catalog.

## Qwen3 TTS

Use for character voice design, controlled predefined voices, and voice cloning when an available workflow provides that route.

## ACE-Step

Use for local score or song generation when an available workflow provides structured music controls.

## MiniMax Music 3

Use for score or song workflows that benefit from MiniMax Music generation.

## Stable Audio

Use for instrumental music, isolated stems, short sound effects, samples, ambience, audio-to-audio transformation, inpainting, and continuation when an available workflow provides that route. Do not use it for intelligible dialogue.
