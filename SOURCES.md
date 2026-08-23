# Sources and Reviewed References

Story-Film Skills does not require network access at runtime. These sources informed model adapters, skill mechanics, film-planning rules, or development hardening.

Checked August 2026.

## Pi Agent

- Pi Skills documentation: https://pi.dev/docs/latest/skills

## Agent skill design

- Matt Pocock skills: https://github.com/mattpocock/skills
- Cursor pstack: https://github.com/cursor/plugins/tree/main/pstack

## Reviewed creative-skill projects

These were reviewed for patterns and ideas. They are not runtime dependencies.

- Visual Skills: https://github.com/smixs/visual-skills
  - Useful patterns adopted in original wording: dramaturgy before model syntax, motivated camera movement, concrete shot detail, progressive disclosure, and reference-aware image planning.
  - Source is CC BY 4.0. No source files are bundled.
- OpenClaw film-director skill: https://github.com/cloudaipro/openclaw-agent-skills/tree/main/skills/film-director
  - Useful patterns: explicit output validation, regression datasets, prompt-injection tests, and continuity risk reporting.
- ComfyUI-Pi-Agent: https://github.com/badgids/ComfyUI-Pi-Agent
  - Useful patterns: stable IDs, reference roles, dependency invalidation, incremental production scope, and portable editorial intent. Story-Film Skills implements its own standalone versions of required capabilities.
- ComfyUI-OrbitSheets: https://github.com/lumosai8/ComfyUI-OrbitSheets
  - Useful patterns: coherent multi-view references, explicit character versus location coverage strategies, contact-sheet selection, and positive spatial constraints.
- Diagram Design: https://github.com/cathrynlavery/diagram-design
  - Useful patterns: one-question-per-diagram, strict complexity budgets, semantic records, and deletion of decorative structure.


## Official ComfyUI operation sources

These official Comfy repositories were reviewed for release 00.00.03. ComfyUI is required only when the user asks this suite to perform actual ComfyUI execution. The other repositories below are optional interfaces or development references, not package runtime dependencies.

- ComfyUI: https://github.com/Comfy-Org/ComfyUI
  - Used for the native HTTP surface, live node schemas, model lists, queue/history behavior, workflow submission, uploads, output viewing, cancellation, feature/system discovery, and memory release.
- comfy-cli: https://github.com/Comfy-Org/comfy-cli
  - Used for workspace/lifecycle concepts, JSON agent envelopes, workflow execution and UI conversion, templates, live node discovery, source-oriented fragment/blueprint workflows, jobs, downloads, resources, and safe mutation boundaries.
- comfy-api-proxy: https://github.com/Comfy-Org/comfy-api-proxy
  - Used for the public Comfy API v2 jobs/assets contract, poll-first durable execution, idempotency, content-addressed asset handling, and secure proxy deployment rules.
- comfy-mcp: https://github.com/Comfy-Org/comfy-mcp
  - Used for canonical agent flows around server discovery, async generations, current templates, workflow validation, missing dependencies, remote targets, VRAM coordination, partner authentication, and user confirmation for spending.
- comfy-skills: https://github.com/Comfy-Org/comfy-skills
  - Used for the stable-steering/live-specifics rule and generation-agent checks such as selecting current workflows dynamically and ensuring requested outputs are actually exposed before spending compute.

No source code from these repositories is bundled in Story-Film Skills. The native controllers in `scripts/` are independent standard-library implementations of documented public interfaces.

## Local LLM lifecycle APIs

- llama.cpp server documentation: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
  - Used for router-mode model listing and native `POST /models/load` and `POST /models/unload` lifecycle behavior.
- Ollama API documentation: https://docs.ollama.com/api
  - Used for `GET /api/ps` resident-model discovery and `/api/generate` `keep_alive` lifecycle behavior.

Story-Film implements these calls with a standard-library HTTP helper. It does not bundle llama.cpp or Ollama source code and does not require an agent-authored lifecycle script.

## Image and video models

- Qwen Image: https://github.com/QwenLM/Qwen-Image
- Qwen Image 2512 prompt utility: https://github.com/QwenLM/Qwen-Image/blob/main/src/examples/tools/prompt_utils_2512.py
- Krea 2 introduction: https://www.krea.ai/blog/krea-2-image-model
- Krea 2 exploratory prompting: https://www.krea.ai/blog/explorative-prompting-krea-2
- MiniMax H3 official prompt skill: https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md
- LTX 2.5 prompt guide: https://ltx.io/blog/ltx-2-5-prompt-guide
- LTX open-source prompting guide: https://docs.ltx.io/open-source-model/usage-guides/prompting-guide

## Voice, music, and sound

- Qwen3 TTS: https://github.com/QwenLM/Qwen3-TTS
- ACE-Step 1.5: https://github.com/ace-step/ACE-Step-1.5
- MiniMax Music skills: https://github.com/MiniMax-AI/skills/tree/main/skills/minimax-music-gen
- Stable Audio 3: https://github.com/Stability-AI/stable-audio-3
- Stable Audio 3 prompting guide: https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md


## Story, writing, storyboard, and collaborative film review

These sources were reviewed during the 00.00.04 and 00.00.05 prototype passes. Concepts were independently implemented and the repositories are not runtime dependencies.

- FilmAgent paper: https://arxiv.org/abs/2501.12909
  - Useful concepts: specialized film roles, bounded critique/correction, peer comparison and judging, performer action/position state, camera choice, and production timing.
- MovieAgent: https://github.com/showlab/MovieAgent
- MovieAgent paper: https://arxiv.org/abs/2503.07314
  - Useful concepts: hierarchical synopsis-to-scene-to-shot planning, scene-level cinematic intent, shot-level character composition, and automated media evaluation dimensions.
- danjdewhurst/story-skills: https://github.com/danjdewhurst/story-skills
  - Useful concepts: deterministic story state, chronology, promise/payoff order, knowledge state, object state, and active-versus-mentioned character distinctions.
- haowjy/creative-writing-skills: https://github.com/haowjy/creative-writing-skills
  - Useful concepts: character knowledge boundaries, first-time reader simulation, review-level separation, and role-specific critique.
- dalestudy/skills: https://github.com/dalestudy/skills
  - Reviewed, but its Storybook material is frontend component tooling rather than narrative film storyboarding.
- Aradotso oh-story writing skill: https://github.com/Aradotso/trending-skills/blob/main/skills/oh-story-claudecode-writing/SKILL.md
  - Useful concepts: file-backed long-form state, hooks, reversals, and separate prose-cleanup passes. Platform-specific formulas were not adopted as universal rules.
- Aradotso research-writing skill: https://github.com/Aradotso/trending-skills/blob/main/skills/awesome-ai-research-writing/SKILL.md
  - Adapted concept: modification verification so rewrites, adaptations, compression, and expansion preserve declared facts/effects unless change is intentional.
- AI Video Storyboard skill: https://github.com/aicontentskills/ai-video-storyboard-skill
  - Useful concepts: shared visual language and cross-shot consistency before isolated prompt optimization.
- Storyboard Manager: https://github.com/ailabs-393/ai-labs-claude-skills/tree/main/dist/skills/storyboard-manager
  - Useful concepts: action/aftermath diagnostics, scene turns, and consistency checks.
- inference-sh skills: https://github.com/inference-sh/skills
  - Useful film concepts: match on action, eyeline match, screen direction, axis discipline, and annotated boards. The external generation service is not a dependency.
- rainlib/ai-storyboard: https://github.com/rainlib/ai-storyboard
  - Useful concepts: progressive storyboard stages, review gates, and file-backed recoverability. Fixed panel counts were not adopted.

## User-provided production benchmark for 00.00.06

- `Pippa_Pebblehoof_Production_Studio_v6.4.41(1).zip`
  - Reviewed as a capability benchmark for end-to-end short-film production, resumable stages, candidate approval, soundtrack mastering, editable project output, trailer variants, social deliverables, and narrow invalidation.
  - No code or private path assumptions from the package are bundled into Story-Film Skills. The finishing and release layer is an original implementation built on portable manifests and public runtimes.
## Deterministic media editing and editor project export for 00.00.07

Reviewed sources:

- FFmpeg source repository: https://github.com/FFmpeg/FFmpeg
  - Adopted the library/tool separation and runtime-discoverable codec, format, filtering, device, scaling, resampling, probing, and CLI model.
  - The package does not bundle FFmpeg.
- MLT source repository: https://github.com/mltframework/mlt
  - Adopted the producer/playlist/tractor/filter/transition/link/consumer service-graph model, XML serialization contract, current v7 DTD shape, and melt runtime-query approach.
  - The package does not bundle MLT.
- MLT XML documentation: https://www.mltframework.org/docs/mltxml/
- MLT melt documentation: https://www.mltframework.org/docs/melt/
- ImageMagick source repository: https://github.com/ImageMagick/ImageMagick
  - Adopted runtime format/delegate/policy discovery, ImageMagick 7 `magick` command routing, broad deterministic image manipulation categories, and security-policy discipline.
  - The package does not bundle ImageMagick.
- ImageMagick command-line tools: https://imagemagick.org/command-line-tools/
- Kdenlive source repository: https://github.com/KDE/kdenlive
  - Reviewed `dev-docs/fileformat.md` for current Generation 5 project structure, `main_bin`, document version `1.1`, track tractors/playlists, sequence tractors, final project wrapper, filters, transitions, and subtitles.
  - No Kdenlive code was copied into the package.
- Kdenlive project file documentation: https://docs.kdenlive.org/en/project_and_asset_management/file_management/project_files.html
- Shotcut source repository: https://github.com/mltframework/shotcut
  - Reviewed current MLT XML serialization behavior and Shotcut project properties such as project audio channels, project folder state, named timeline playlists, and main timeline tractor semantics.
  - No Shotcut code was copied into the package.

Implementation is original Python and documentation. External programs are runtime tools, not bundled dependencies for creative planning.
## Evidence, edit assistance, motion graphics, documents, and publishing for 00.00.08

These repositories were reviewed for transferable production patterns. They are not required runtime dependencies unless explicitly described as an optional external tool.

- ComposioHQ content-research-writer: https://github.com/ComposioHQ/awesome-claude-skills/tree/master/content-research-writer
  - Adopted in original form: explicit research gaps, source-aware factual support, claim-to-source traceability, preserving disagreements, and pre-publication fact checks.
  - Not adopted: generic prose workflow as a replacement for existing story-writing/review skills.
- wells1137 video-overlay: https://github.com/wells1137/media-skills/tree/main/skills/video-overlay
  - Adopted in original form: first-class packaging identities for intros/outros, lower thirds, title cards, watermarks, subtitle presentation, and transitions.
  - Existing FFmpeg infrastructure remains the execution layer; MoviePy is not required.
- aiagentwithdhruv video-edit: https://github.com/aiagentwithdhruv/skills/tree/main/video-edit
  - Adopted in original form: speech/silence analysis, reviewed jump cuts, caption workflows, destination reframing, clip extraction, and delivery compression.
  - Not adopted: YouTube downloading/uploading, Auphonic dependency, Apple-only encoder assumptions, or fixed social-platform requirements as permanent truth.
- aiagentwithdhruv pan-3d-transition: https://github.com/aiagentwithdhruv/skills/tree/main/pan-3d-transition
  - Generalized into the broader programmatic-video subsystem instead of copying one swivel transition.
- Remotion: https://github.com/remotion-dev/remotion
  - Adopted as an optional adapter target for frame-deterministic code-driven compositions, reusable motion design, captions, and programmatic video.
  - Remotion is not bundled. Its current license is external to this MIT package and must be reviewed before install/render use.
- davila7 content-creator: https://github.com/davila7/claude-code-templates/tree/main/cli-tool/components/skills/business-marketing/content-creator
  - Adopted in original form: durable brand voice, content repurposing/lineage, campaign consistency, and content-calendar thinking.
  - Not adopted as fixed rules: keyword-density targets, posting-time claims, content-length formulas, or platform algorithm assumptions that may be stale or campaign-specific.
- Anthropic XLSX skill: https://github.com/anthropics/skills/tree/main/skills/xlsx
- Anthropic DOCX skill: https://github.com/anthropics/skills/tree/main/skills/docx
- Anthropic PDF skill: https://github.com/anthropics/skills/tree/main/skills/pdf
- Anthropic canvas-design skill: https://github.com/anthropics/skills/tree/main/skills/canvas-design
  - These skills are proprietary. Only high-level production ideas were independently implemented: formula preservation, output verification, professional editable/fixed-layout production documents, visual review, and a reusable visual design philosophy/system before campaign variants. No proprietary skill text or source code is bundled.
- MuPDF: https://github.com/ArtifexSoftware/mupdf
  - Useful optional operations include document rendering, conversion, inspection, text search, resource extraction, clean/rewrite, merge, and poster workflows.
  - MuPDF is AGPL with commercial licensing options. Badgids does not bundle it or make it a required dependency; `mutool` is used only when independently installed and appropriate.



## v0.0.9 user-provided project review

- User-provided `Comfy-Media-Director-Pi-v3.2.55-Full-Suite.zip`
  - reviewed specifically for Pi pipeline todo UX, progress state, checkpoint/recovery, pause/resume, validation gating, and bounded retry concepts
  - no source code from the older project is required at runtime by Story-Film Skills
  - v0.0.9 implements an original reduced progress system suited to this standalone project

## Creative planning and resource-safe generation for v0.0.10

Reviewed from `mattpocock/skills`:

- https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md
- https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md
- https://github.com/mattpocock/skills/blob/main/skills/engineering/to-spec/SKILL.md
- https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md
- https://github.com/mattpocock/skills/blob/main/skills/engineering/implement/SKILL.md
- https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md
- https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md
- https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md
- https://github.com/mattpocock/skills/blob/main/skills/engineering/wizard/SKILL.md

Adopted only as high-level interaction concepts: decision frontiers, breadth/dependency-aware questioning, synthesis from already-settled context, blocked work slices, a large-effort decision map, compact handoff, and guided human-only procedures. Skill names, source prose, software-engineering issue/commit mechanics, and code-development assumptions were not copied into Story-Film-Skills.

ComfyUI server source:

- https://github.com/Comfy-Org/ComfyUI/blob/master/server.py
  - Confirmed native queue/status surfaces and the public POST `/free` operation with `unload_models` and `free_memory` flags used by the deterministic post-batch cleanup path.

## Repository packaging and licensing for v0.0.11

- Apache Software Foundation, Apache License Version 2.0 and official application guidance.
  - Used for the repository `LICENSE`, `NOTICE`, attribution behavior, and short SPDX/copyright source headers.
  - Story-Film Skills does not add a second restriction that changes Apache-2.0.
- `vercel-labs/skills`
  - Reviewed the current `npx skills add` source formats and `--skill`, `--global`, and non-interactive options.
  - Story-Film Skills uses a self-contained `story-film-suite` directory because a selected Agent Skill must not depend on files that might not be installed with it.
- Pi Agent skills documentation
  - Confirmed recursive `SKILL.md` discovery in Pi skill locations and the standard self-contained skill structure.
