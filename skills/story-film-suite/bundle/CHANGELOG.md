# Changelog

## v0.0.24 (00.00.24) - 2026-08-20

- Added native `story_comfy` `model-inventory` and `model-search` actions backed by Story-Film's deterministic live ComfyUI model registry scan.
- Model discovery now enumerates every folder returned by ComfyUI `/models`, including `unet`, `diffusion_models`, `checkpoints`, `diffusers`, and model choices exposed by installed loader nodes.
- Added `unet` and `diffusers` as first-class image, image-edit, and video resource locations instead of treating `checkpoints` as the only local model-weight folder.
- Fixed multi-word `search-tools` queries so weak models can find relevant official comfy-mcp tools instead of requiring one exact literal description match.
- Strengthened Pi runtime steering so an agent must run the complete live model inventory before claiming that a local image or video model is missing.
- Improved managed-runtime process errors so cancellation or signal termination is reported explicitly instead of `managed runtime exited null`.
- Added regression coverage for Qwen weights in `unet`, MiniMax/LTX-style weights in `diffusion_models`, node-exposed model choices, and multi-word tool discovery.

## v0.0.23 (00.00.23) - 2026-08-20

- Added a Pi-native `story_comfy` tool so Story-Film controls the user's existing ComfyUI without requiring a separately configured generic MCP extension.
- Added a Story-Film-managed external Python runtime that automatically installs official `comfy-cli>=1.14.0`, `comfy-mcp`, and `comfy-api-proxy` packages on first Comfy use while preserving their upstream licenses.
- Made ComfyUI itself and the user's chosen model collection the only Comfy-side components the end user is expected to install independently; managed bootstrap never runs ComfyUI installation or model/custom-node downloads.
- Added direct MCP stdio bridging to the official `comfy-mcp` server, including server discovery, live tool search, generic official MCP tool calls, and explicit approval gates for third-party code, version changes, model downloads, and paid-partner execution.
- Added managed `comfy-api-proxy` lifecycle and generic `/api/v2/` request support on loopback for workflows that need the v2 contract.
- Added a dedicated runtime steering guard so Pi uses `story_comfy` instead of falling back to permission-gated bash, raw HTTP clients, or a missing generic MCP server during normal interactive ComfyUI work.
- Kept the existing Story-Film workflow catalog, live validation/promotion, deterministic offline batch, native HTTP fallback, and resource-handoff machinery underneath the managed official control surface.
- Added deterministic regression coverage for managed-package scope, project ComfyUI URL routing, MCP action routing, and Pi tool registration.

## v0.0.22 (00.00.22) - 2026-08-20

- Removed the non-working `Ctrl+Alt+T` and `Ctrl+Alt+Shift+T` Story-Film Todo shortcuts completely instead of retaining dead compatibility bindings.
- Added `Ctrl+Alt+End` as the single compact/expanded Todo keyboard toggle; `Ctrl+Alt+Home` continues to focus/follow the current item.
- Added native ComfyUI workflow discovery across project workflows/templates, ComfyUI user workflows, official core templates, and installed custom-node example workflows.
- Added native workflow fetch and live-validated promotion commands so executable project workflows are sourced or validated before they enter `04_generation/comfyui/workflows/`.
- Hardened the Pi runtime guard against raw `/prompt`, `/history`, `/object_info`, workflow-template/userdata HTTP loops, and direct writes of guessed executable `class_type` graphs.
- Made existing validated workflows/templates the required first choice before new graph construction.
- Clarified that model prompt adapters such as `qwen-image-2512` describe prompt grammar and do not imply any same-named ComfyUI node, API node, checkpoint, or runtime.
- Added deterministic coverage for workflow catalog/fetch behavior and for removal of the broken Todo key chords.

## v0.0.21 (00.00.21) - 2026-08-20

- Fixed Story-Film Todo keyboard handling with a raw terminal-input fallback that uses Pi's own key parser when normal extension shortcut dispatch is unavailable or unreliable.
- Kept the normal `pi.registerShortcut` path and made the raw fallback consume handled Story-Film keys so the same action cannot fire twice.
- Restored the complete Todo control legend in both compact and expanded views: toggle, fallback toggle, row scroll, page scroll, focus-current, and help.
- Split the control legend across short lines so terminal-width truncation cannot silently hide the navigation controls.
- Strengthened regression coverage so the Pi extension contract requires the terminal fallback and all visible navigation controls.

## v0.0.20 (00.00.20) - 2026-08-20

- Added portable ImageMagick 6 and ImageMagick 7 command resolution to the media toolkit.
- Kept `magick` as Story-Film's logical tool name while falling back to ImageMagick 6 `convert`, `identify`, `mogrify`, and related executables when the ImageMagick 7 launcher is unavailable.
- Removed the regression test's direct dependency on a `magick` executable and added deterministic coverage for legacy ImageMagick command resolution.
- Documented ImageMagick 6/7 runtime compatibility.

## v0.0.19 (00.00.19) - 2026-08-20

- Fixed Story-Film Todo shortcut packaging so the checked-in `story-film-suite` bundle cannot silently lag behind the source extension.
- Kept `Ctrl+Alt+T` as the primary compact/expanded toggle and added `Ctrl+Alt+Shift+T` as a fallback for terminals or host environments that intercept the primary chord.
- Made `scripts/build_npx_bundle.py --check` a real read-only drift check instead of rebuilding the bundle and masking stale generated files.
- Added bundle drift coverage to the existing regression path and updated Todo control documentation/evals.

## v0.0.18 (00.00.18) - 2026-08-20

- Restored reliable Story-Film Todo hotkeys with `Ctrl+Alt` bindings that use fewer terminal modifiers.
- Added a visible Todo control hint in both compact and expanded views.
- Added `/story-todo help` and `/story-todo keys` so controls remain discoverable without documentation.
- Hardened ComfyUI model discovery so the agent cannot bypass `model_inventory.py` with raw `curl`, `wget`, inline Python HTTP parsers, filesystem model scans, or helper scripts.
- Clarified that `/models` and `/models/{folder}` remain the authoritative ComfyUI server APIs, but Story-Film agents must access them through the bundled inventory tool during production.

## v0.0.17 (00.00.17) - 2026-08-20

- Fixed ComfyUI model discovery for installations that use `extra_model_paths.yaml` or other server-registered external model directories. Story-Film now treats ComfyUI's `/models` and `/models/{folder}` registry as authoritative instead of assuming models live under the ComfyUI application directory.
- Hardened generation setup so agents must use `scripts/model_inventory.py scan` for model discovery. Ad hoc `/object_info` parsers and filesystem-wide `find` scans are forbidden for deciding which ComfyUI models are installed.
- Documented the current ComfyUI node schema correctly: node input definitions are under `input.required` and `input.optional`; `/object_info` is for node schemas and is only a secondary source for model-like dropdown choices.
- Added a deterministic Pi runtime guard that blocks filesystem-wide model scans during an active Story-Film pipeline and redirects the agent to the ComfyUI model inventory.
- Added explicit handling for empty model inventory results. An empty or inconsistent registry is a blocker to diagnose, not proof that the user owns no models, not permission to download models, and not permission to create mock generated media.
- Added regression definitions and deterministic coverage for external ComfyUI model directories and the no-filesystem-scan rule.

## v0.0.16 (00.00.16) - 2026-08-20

- Added a project-generic Fountain screenplay consistency verifier. It derives dialogue speaker identities from `00_project/canon.json` and never hardcodes story-specific character names.
- Integrated screenplay consistency into the main project validator, screenplay-writing skill, and screenplay-revision skill.
- Added exact checks for dialogue count, dialogue order, dialogue text, and `CHAR-###` speaker identity between `screenplay.fountain` and `line_manifest.jsonl`.
- Added typo diagnostics with canonical-name suggestions so a misspelled cue such as `EILIAS` is reported directly instead of causing repeated ad hoc debugging.
- Added regression coverage proving the verifier accepts arbitrary character names and immediately catches the `ELIAS` versus `EILIAS` failure class.

## v0.0.15 (00.00.15) - 2026-08-19

- Made the Story-Film Pi Todo compact by default with three visible pipeline rows while preserving a ten-row expanded view.
- Added `/story-todo toggle`, `/story-todo expand`, `/story-todo collapse`, and `Ctrl+Alt+Shift+T`. Compact and expanded modes both support scrolling and current-target follow mode.
- Added a per-turn runtime prompt guard that tells the active model the exact authoritative Story-Film target from `pipeline_progress.json`.
- Added a deterministic future-specialist read guard. When a specialist exists only in a later pending pipeline target, the Pi extension blocks opening that specialist until the current target is validated and checkpointed.
- Strengthened pipeline rules so the agent cannot intentionally work ahead and then leave the Todo cursor behind. File existence still never proves completion.
- Added a host-Todo mirror rule: if Pi provides its own generic Todo, Story-Film work uses at most three mirrored items there: current target, immediate next target, and requested endpoint. Compatible generic Todo initialization calls with more than three items are blocked. The host Todo remains secondary to `pipeline_progress.json`.
- Documented the boundary that Story-Film cannot portably force a host-owned Todo panel's row count or expansion state through the public extension API.

## v0.0.14 (00.00.14) - 2026-08-19

- Added user-controlled generation configuration for image generation, image editing, video generation, TTS, music, SFX/Foley, image upscaling, video upscaling, and frame interpolation.
- Added live ComfyUI model inventory polling through the public `/models`, `/models/{folder}`, and `/object_info` APIs. Story-Film Skills now records exact server-reported model folders and model-like node choices before model-specific generation.
- Expanded `00_project/model_preferences.json` to schema version 2 with per-process, per-adapter profiles. A profile can preserve exact checkpoints, diffusion models, VAEs, text encoders, LoRAs, audio encoders, upscalers, frame-interpolation models, custom model folders, and node-provided model choices.
- MiniMax H3 remains the default video adapter only. The default no longer implies any checkpoint, VAE, text encoder, LoRA, or other concrete ComfyUI resource. Other generation processes have no forced adapter default and require a user selection or explicit delegation before model-specific generation.
- Added `scripts/model_inventory.py` and the `generation-model-setup` skill. Pi must show the user the installed choices for each required production process and record the exact selections instead of choosing from file order or model availability.
- Added backward-compatible migration from the v0.0.13 video-only model preference schema and kept `set-video` and `reset-video` command aliases.
- Added deterministic tests for live inventory polling, model-specific VAE/text-encoder profiles, LoRA strengths, per-process selection, inactive profile preservation, missing-resource blocking, and v1-to-v2 preference migration.

## v0.0.13 (00.00.13) - 2026-08-19

- Fixed video-generation model selection. The user owns the video-model choice; Story-Film Skills no longer chooses LTX or another adapter merely because it appears to fit the shot.
- MiniMax H3 (`minimax-h3`) is now the explicit default video-generation model when the user has not chosen another model.
- Added `00_project/model_preferences.json`, `scripts/model_preferences.py`, and `references/MODEL_SELECTION.md` for durable model choice, user/delegated overrides, and a no-silent-substitution rule.
- If the selected video model is unavailable, Story-Film Skills must report a blocker and available alternatives instead of silently switching models.
- Added model-selection documentation and deterministic regression coverage.

## v0.0.12 (00.00.12) - 2026-08-19

- Fixed local LLM runtime classification. Story-Film Skills must not infer that Pi uses a cloud or external model from OpenAI-compatible API behavior, provider naming, or missing environment variables.
- Added `scripts/llm_runtime.py`. Loopback endpoints such as `127.0.0.1`, `localhost`, and `::1`, plus local-interface endpoints and Unix-domain sockets, are classified as local. Other endpoints remain unknown until direct evidence proves they are external.
- Hardened resource handoff policy. The `external` lifecycle adapter now requires explicit external runtime location evidence and is rejected when the configured endpoint is local.
- Added regression and local-smoke coverage for Pi using a local `llama-server` endpoint on `127.0.0.1`.
- Hardened `scripts/validate_skills.py` to parse YAML frontmatter with PyYAML when available, with a dependency-free unsafe-scalar fallback, so malformed skill metadata is caught before Pi loads it.

## v0.0.11 (00.00.11) - 2026-08-19

- Added nine documented example/test prompts without changing the v0.0.11 version: three approximately 5-minute videos, three approximately 20-minute short films, and three feature-movie prompts requiring at least 90 minutes. The set covers narrative, factual, dialogue-heavy, mystery, science-fiction, ensemble comedy/fantasy, grounded feature drama, resource-heavy feature science fiction, and animated family fantasy production shapes.
- Added planning-only, generation-ready, and full-production test instructions, a linked examples documentation section, a machine-readable prompt catalog, and deterministic catalog validation. The self-contained `npx skills` bundle now includes the examples.
- Made native `pi install` the preferred Pi installation method. Added a `pi` package manifest and `pi-package` metadata to `package.json` so Pi can load the direct Story-Film skills and the Todo/resource-status extension from the repository without requiring `install.sh`.
- Added a Pi manifest exclusion for `skills/story-film-suite` so native Pi installation does not recursively discover the duplicated specialist skills inside the self-contained `npx skills` bundle.
- Added documented project-only beta installation with `pi install -l`, local-checkout testing, one-process `pi -e` testing, pinned Git revisions, project-local removal, and team sharing through `.pi/settings.json`. `install.sh` remains as a fallback.
- Kept the release version unchanged at canonical `00.00.11`, display `v0.0.11`, because this is an installation/documentation refinement to the same prototype-complete release.
- Renamed the product to **Story-Film Skills** and made `00.00.11` the canonical version with human display version `v0.0.11`.
- Marked v0.0.11 as the end of the initial prototype-building phase. Added a deterministic regression runner and an OpenAI-compatible local-model smoke-test harness for the next testing phase.
- Added `sequence-production`, `scripts/sequence_manager.py`, and paired JSON/Markdown sequence manifests using stable `SEQ-###` IDs. Feature-film scenes can now be managed as bounded production sequences instead of one giant project object.
- Added `context-shards` and `scripts/context_shards.py` for per-sequence working sets. Shards preserve source hashes and related stable IDs so an agent can work on one feature sequence without loading the complete project state.
- Added `production-health` and `scripts/production_health.py` for deterministic health reports covering blocked pipeline state, stale artifacts, sequence state, generation failures, resource handoff state, coverage, editorial reconciliation, continuity, and rich-document companions.
- Added `long-range-continuity`, `CONT-###`, continuity anchors, observations, and distant-sequence conflict reporting.
- Added `generation-budget` and `scripts/generation_scheduler.py` for declared RAM/VRAM limits, resource profiles, dependency-safe scheduling, resident model groups, model-swap reduction, and preflight rejection when a job profile exceeds usable memory.
- Added `reboot-recovery` and `scripts/recovery_checkpoint.py` for durable control-file hashes, exact/dirty/resource-interrupted resume modes, recovery journals, and human-readable restart instructions.
- Added `batch-recovery` and `scripts/batch_recovery.py`. Partial ComfyUI failures preserve completed independent jobs and rebuild only failed, unfinished, or affected downstream work.
- Updated the offline ComfyUI runner so partial results are persisted during execution and hard failures record the failed job before returning control.
- Added `editorial-reconciliation` and `scripts/editorial_reconcile.py` to compare selected shots with the main feature timeline, detect missing selections, duplicate events, repeated placements, sequence-order problems, and per-sequence duration.
- Added `film-completeness` and `scripts/completeness_audit.py` as the final feature-film gate. A master file alone cannot make a project complete.
- Added `references/FEATURE_SCALE_PRODUCTION.md` and the `feature-scale-production` playbook. Integrated feature-scale gates into `feature-film`, `full-pipeline`, and resource-safe ComfyUI workflows.
- Added feature-scale initialization state and dependency-graph entries for sequences, shards, health, continuity, generation schedules, reboot recovery, partial batch recovery, editorial reconciliation, and completeness.
- Added a full linked Markdown documentation manual under `docs/`, now with 44 linked pages after the installation and example/test documentation refinements. The manual uses controlled simple English based on important ASD-STE100 principles and ELI5 teaching goals, with top navigation, tables of contents, parent links, related links, a glossary, and command reference.
- Added `scripts/check_docs.py` to validate documentation navigation, relative links, required page structure, the GitHub README header contract, and the no-em-dash rule. It also reports controlled-English readability warnings without claiming official ASD-STE100 certification.
- Added Apache License 2.0 repository licensing with `LICENSE`, `NOTICE`, `AUTHORS.md`, `ATTRIBUTION.md`, source SPDX/copyright headers, and Author/Developer metadata for Alan Guice (Badgids).
- Added GitHub-ready repository files: `.gitignore`, `.gitattributes`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CITATION.cff`, issue templates, pull-request template, `requirements-dev.txt`, `package.json`, and a validation GitHub Actions workflow.
- Reworked `install.sh` for the Story-Film Skills name, configurable Pi paths, optional `--skills-only`, new `story-film-progress.ts` extension name, and cleanup of known legacy install paths.
- Added `scripts/install_pi_extension.py` for users who install the skill bundle separately and want the optional Pi Todo/resource-status extension.
- Added the self-contained `story-film-suite` Agent Skill and `scripts/build_npx_bundle.py`. The bundle carries the router, specialist skills, shared scripts, references, docs, tests, extension source, and license files so a single selected skill can be installed with `npx skills` without losing root-level dependencies.
- Expanded stable IDs with `SEQ-###` for feature production sequences and `CONT-###` for long-range continuity anchors.
- Expanded regression definitions from 90 to 102 cases and deterministic tests from 44 to 57 tests after the installation and example-prompt regression additions.
- Verified all 36 Story-Film playbooks compile into deterministic Todo trees.
- No live local-model smoke tests are part of the v0.0.11 build verification. The harness and cases are included so regression and local smoke testing can begin after this prototype-complete release.

## v0.0.10 (00.00.10) - 2026-08-19

- Reviewed nine Matt Pocock planning/productivity skills and independently adapted the useful interaction patterns for story, book, image, audio, video, film, and release production without copying names or engineering-specific workflows.
- Added `decision-tree-interview`, `creative-pressure-test`, and `documented-creative-discovery` for dependency-aware creative questioning, facts-versus-decisions separation, durable `DEC-###` records, and decision documentation without storing private chain-of-thought.
- Added `creative-production-spec` and `00_project/creative_production_spec.md` to synthesize already-known project intent, audience experience, canon, creative requirements, production requirements, acceptance decisions, validation strategy, scope boundaries, and unresolved decisions without forcing a redundant interview.
- Added `production-work-units`, `scripts/work_units.py`, `UNIT-###`, and paired `work_units.json`/`work_units.md` for complete production slices with blockers, acceptance criteria, ready-frontier execution, and deterministic status.
- Added `production-executor` for executing only ready production work, validating at declared gates, preserving failed work as blocked, and checkpointing the Pi Todo only after acceptance criteria pass.
- Added `production-compass`, `scripts/decision_map.py`, and paired `decision_map.json`/`decision_map.md` for multi-session creative efforts whose full route is not yet visible. The map distinguishes resolved decisions, current frontier, not-yet-specifiable fog, and out-of-scope work.
- Added `session-bridge` and `references/SESSION_BRIDGE.md` for compact session continuation that references existing durable artifacts instead of duplicating them.
- Added `guided-production-wizard`, `scripts/guided_wizard.py`, and paired shell/Markdown outputs for human-only production procedures with stage counts, verification instructions, and irreversible-action confirmation.
- Added a global rich-document companion contract. Every generated PDF, DOCX/DOTX, XLSX/XLSM/XLTX, PPTX/PPTM, ODT/ODS/ODP must have a meaningful same-basename Markdown equivalent. `scripts/document_companions.py`, production-document rendering, PDF transformations, project initialization, and project validation enforce this rule.
- Added `resource-safe-generation`, `comfyui-offline-batch`, `references/RESOURCE_SAFE_GENERATION.md`, `references/COMFYUI_OFFLINE_BATCH.md`, `scripts/comfyui_batch.py`, and `scripts/resource_handoff.py` for machines where a local Pi LLM and ComfyUI generation models cannot safely coexist in RAM/VRAM.
- Offline ComfyUI handoff now stages declared inputs while the LLM is still loaded, patches exact ComfyUI-returned input identities, and live-validates every final workflow before arming the batch. After handoff, the deterministic runner contains no LLM calls and cannot make semantic/creative decisions.
- Added explicit local-model lifecycle adapters using shell-free argv arrays or an `external` model mode. Exclusive local generation refuses to arm when unload/reload behavior is unconfigured.
- Added model-free resource runtime state in `resource_handoff.json`, append-only `resource_events.jsonl`, a release signal, detached runner log, and `RESOURCE_RESUME.md`. The Pi extension renders this state and phase-change notifications on a timer without consuming model context.
- The Pi extension now releases the deterministic runner from `agent_end`, after the active response completes, and intercepts user input while the LLM is unavailable so status can be shown without invoking the model. Added `/story-resource`.
- After the prepared ComfyUI queue finishes or fails, the runner waits for queue drain where possible, calls ComfyUI's public memory-release endpoint with both model-unload and free-memory requests, then reloads and health-checks the configured local LLM before returning control.
- Added two playbooks: `creative-planning-and-execution` and `resource-safe-comfyui`, integrated them into the main router and ComfyUI generation route, and expanded the portable project schema/dependency graph.
- Expanded future live-model regression definitions from 78 to 90 for planning-frontier behavior, decision/spec synthesis, work-unit blockers, fog preservation, compact handoff, wizard boundaries, rich-document companions, offline-batch completeness, local-model lifecycle truthfulness, model-free Pi status, and semantic-failure restoration.
- Expanded deterministic coverage from 39 to 44 tests, including real project companion enforcement and a fake-live-ComfyUI full resource handoff with deterministic unload/reload commands and verified ComfyUI memory-release request.
- Live small-model smoke testing remains intentionally deferred while prototype development continues.

## v0.0.9 (00.00.09) - 2026-08-19

- Added `pipeline-progress`, `references/PIPELINE_PROGRESS.md`, and `scripts/pipeline_progress.py` for durable multi-step Story-Film execution state derived from numbered playbooks.
- Added a bounded three-level stage -> step -> substep progress model with deterministic counts from playbook files rather than model-estimated progress.
- Added `00_project/pipeline_progress.json`, append-only `progress_events.jsonl`, and `HANDOFF.md` to new projects so long pipelines can resume after Pi restart, model change, or context compaction without reconstructing progress from chat history.
- Added atomic checkpoint behavior that writes canonical progress first, appends the transition event, and replaces the human-readable handoff last.
- Added non-advancing blocked checkpoints. Validation failure keeps the same leaf blocked/current until correction and does not silently move to the next production step.
- Added intentional pause/resume, reason-required conditional skips, and selective execution-target reset without treating a bounded retry as a full project restart. Artifact invalidation remains owned by `project-impact` and the dependency graph.
- Added an optional Pi extension that renders the authoritative pipeline ledger as a scrollable todo viewport above the editor, follows the current item, pins the next action, exposes compact status lines, and never owns completion state.
- Added `/story-todo status|up|down|page-up|page-down|current` plus non-conflicting `Ctrl+Alt+Shift` scrolling/follow shortcuts.
- Updated `install.sh` to install both the Agent Skills package and the optional Pi progress extension using configurable Pi skill/extension roots rather than personal paths.
- Adopted a split version policy: canonical releases remain fixed-width `00.00.00`, while user-facing display uses `v0.0.9` style with leading zeroes removed per numeric field. Added `scripts/version_display.py` and canonical/display regression coverage.
- Reviewed the user-provided Comfy-Media-Director v3.2.55 Full-Suite. Adopted only the focused usability concepts useful to Story-Film-Skills: authoritative progress state, scrollable Pi todo presentation, exact recovery cursor, atomic handoff, non-advancing validation, intentional pause/resume, and bounded retry. The older project's broad plugin/runtime/model-routing architecture is not imported or required.
- Expanded deterministic coverage from 36 to 39 tests and future live-model regression definitions from 72 to 78 with pipeline initialization, recovery, blocked-validation, conditional-skip, selective-retry, and UI-authority cases.
- Live small-model smoke testing remains intentionally deferred while prototype development continues.

## 00.00.08 - 2026-08-19

- Added `evidence-research` with stable `SRC-###` source identities and `CLAIM-###` public-claim records for documentary, historical, technical, educational, press, festival, and campaign facts.
- Added `scripts/claim_ledger.py` and public-use evidence gates for verified/supported/project-decision claims while preserving contested, anecdotal, inspirational, and unresolved material without flattening uncertainty.
- Added `campaign-brand`, `content-repurpose`, `brand_voice.json`, and `CONTENT-###` lineage so campaign variants preserve voice, source identity, spoiler policy, exact naming, factual claims, and transformation history.
- Added `scripts/campaign_content.py` to validate campaign voice structure, copy linkage, content lineage, and public `CLAIM-###` references.
- Added `edit-assist` and `scripts/edit_assist.py` for non-destructive FFmpeg silence maps, reviewed jump-cut rendering, exact clips, subtitle burn-in, optional faster-whisper transcription, focus-aware reframing, and delivery compression presets.
- Added the rule that silence detection is editorial evidence rather than automatic permission to remove dramatic pauses, reactions, room tone, or music.
- Added `motion-graphics` with stable `GFX-###` identities and deterministic FFmpeg title, lower-third, watermark/text, framing, fade, and transition operations.
- Added `programmatic-video` with portable `COMP-###` composition manifests and an optional Remotion adapter for data-driven/code-driven motion work.
- Remotion is not bundled or required. Its generated adapter code is preserved across later scaffolds unless explicitly forced, and install/render operations require explicit license acknowledgement.
- Added `design-system` for durable campaign/title/poster/lower-third visual grammar, safe areas, typography roles, palette behavior, image treatment, motion behavior, accessibility, exact text, and reference identities.
- Added `production-documents` and `scripts/production_documents.py` for traceable `DOC-###` XLSX, DOCX, and PDF outputs such as trackers, schedules, budgets, cue sheets, director books, press kits, festival packets, and campaign documents.
- Added formula-preserving XLSX generation plus structural document QC; DOCX and PDF outputs are generated with local open formats/libraries rather than importing proprietary skill implementations.
- Added `pdf-toolkit` and `scripts/pdf_toolkit.py` for PDF inspection, text extraction, page rendering, merge, split, rotate, search, and optional MuPDF repair. MuPDF remains an optional external runtime and is never bundled.
- Added runtime discovery for Node/npm/npx, MuPDF `mutool`, Poppler PDF tools, and LibreOffice alongside the existing deterministic media capability snapshot.
- Added four playbooks: `evidence-backed-project`, `edit-assist-and-motion-graphics`, `programmatic-video`, and `production-documents`, with integration into story research, film finishing, media editing, social campaigns, marketing art, and release packaging.
- Expanded project initialization, project schema, dependency invalidation, output templates, stable IDs, and validators for evidence, graphics, compositions, campaign lineage, design systems, and production documents.
- Expanded deterministic coverage from 29 to 36 tests, including real FFmpeg silence/jump-cut and lower-third renders, real XLSX/DOCX/PDF creation, real PDF merge/render fallback tests, evidence/campaign validation, programmatic composition validation, and Remotion license guards.
- Expanded future live-model regression definitions from 60 to 72 with evidence, claim drift, campaign voice, content lineage, dramatic-silence preservation, transcription truthfulness, graphics identity, programmatic-video portability, Remotion licensing, formula preservation, and MuPDF fallback cases.
- Reviewed Composio content-research-writer, wells1137 video-overlay, aiagentwithdhruv video-edit and pan-3d-transition, Remotion, davila7 content-creator, Anthropic XLSX/DOCX/PDF/canvas-design skills, and MuPDF. Implementations are original and the reviewed repositories are not runtime dependencies.
- Live small-model smoke testing remains intentionally deferred while prototype development continues.

## 00.00.07 - 2026-08-19

- Added first-class `media-toolkit`, `ffmpeg`, `mlt`, and `imagemagick` skills with runtime capability discovery instead of frozen assumptions about installed codecs, filters, formats, delegates, devices, MLT modules, or hardware acceleration.
- Added `scripts/media_toolkit.py` for version discovery, deep capability snapshots, FFmpeg/MLT/ImageMagick queries, shell-free raw argv execution, and portable multi-step `TOOL-###` manifests.
- Added overwrite guards for FFmpeg `-y` and ImageMagick `mogrify`; reusable operation manifests require explicit project-relative inputs and outputs.
- Added comprehensive FFmpeg guidance for video, audio, subtitle, stream, codec, container, filter-graph, metadata, capture, analysis, QC, hardware, bitstream-filter, image-sequence, and network operations through the installed runtime surface.
- Added comprehensive MLT guidance for producers, chains, playlists, tractors, multitracks, filters, transitions, links, consumers, profiles, XML serialization, playback, and headless rendering through installed MLT services.
- Added comprehensive ImageMagick 7 guidance for conversion, geometry, composition, masks, alpha, color, profiles, drawing, text, montage, image sequences, analysis, morphology, distortion, animation, metadata, batch work, and security-policy-aware processing.
- Added a canonical advanced `editor_project.json` model with `CLIP-###` bin identities, `EDIT-###` timeline placements, multiple V/A tracks, source trims, gaps, MLT filters, cross-track transitions, subtitles, track state, and notes.
- Added `scripts/editor_project_export.py` plus `editor-project-export`, `kdenlive-export`, and `shotcut-export` skills.
- Added direct Kdenlive Generation 5 `.kdenlive` export using documented `main_bin`, document version `1.1`, sequence UUID tractor, two internal playlists per track, sequence tracks, and final `kdenlive:projectTractor` wrapper.
- Added direct Shotcut `.mlt` project export using MLT XML plus `main_bin`, `shotcut:projectAudioChannels`, named timeline playlists, track type metadata, background track, main `shotcut=1` tractor, automatic audio mixing, filters, and transitions.
- Kept generic `mlt-export` as a distinct interchange output so it is no longer mislabeled as a target-specific Kdenlive or Shotcut project.
- Added project directories and dependency nodes for tool capability snapshots, advanced editor state, Kdenlive projects, and Shotcut projects with narrow downstream invalidation.
- Added `media-editing-and-project-export` routing and integrated target-specific editor export into the film-finishing path.
- Expanded deterministic coverage from 26 to 29 tests, including a real ImageMagick execution test and target-specific Kdenlive/Shotcut structural export tests with multitrack filter/transition preservation.
- Expanded future live-model regression definitions from 52 to 60 with media-runtime discovery, source-preservation, MLT service verification, Kdenlive/Shotcut export, portability, and generic-vs-native project cases.
- Live small-model smoke testing remains intentionally deferred while prototype development continues.

## 00.00.06 - 2026-08-19

- Added a generalized `MEDIA-###` registry and approval state for images, video, voice, dialogue, music, SFX, masters, trailers, social outputs, and other generated media. Primary, alternate, rejected, superseded, and retired states are explicit, and newest output never wins automatically.
- Added QC-aware media promotion. A failed candidate cannot become primary without an explicit override and concrete reason.
- Added deterministic `audio-master` planning and `scripts/audio_master.py` for exact timeline placement, trims, gain, pan, fades, resampling, mixing, loudness normalization, peak control, full-program silence padding, stale-source rebuilds, and final 48 kHz master WAV production through FFmpeg.
- Added `video-finishing` and `scripts/video_finish.py` for conventional resolution, frame-rate, aspect, pixel-format, and H.264 normalization while keeping generative upscaling as an explicit model workflow rather than pretending scale is AI enhancement.
- Added an executable `EVT-###` timeline contract and `scripts/render_timeline.py` for hard-cut film, trailer, teaser, cutdown, and social timelines with deterministic video normalization, concatenation, audio-master muxing, and explicit `none` / `sidecar` / `muxed` subtitle policy. Delivery QC can require and verify a muxed subtitle stream.
- Added `film-master` and `scripts/film_master.py` to orchestrate missing audio-master construction, strict source validation, picture rendering, delivery QC, and verified `MASTER-001` registration.
- Added real delivery probing with FFprobe through `delivery-qc`, including stream presence, codec, dimensions, frame rate, duration tolerance, audio sample rate/channels, and SHA-256 evidence. Optional FFmpeg black-frame and freeze-frame detectors can add warning or blocking evidence when requested.
- Added optional standards-based MLT interchange export. The rendered master remains authoritative and the package does not claim a specific editor import succeeded unless that environment was actually tested.
- Added a complete trailer subsystem: trailer plan, trailer assets, trailer edit, trailer master, spoiler policy, trailer-specific structure, target duration/tolerance, pickup tracking, trailer sound/music, QC, and delivery.
- Added a complete social campaign subsystem: campaign planning, `SOC-###` deliverables, cutdowns, deterministic aspect-ratio reframing, title-safe intent, `COPY-###` records, marketing artwork briefs, verified-fact rules, QC, and campaign delivery.
- Added `scripts/render_promos.py` so configured trailers and social video deliverables can use the same executable timeline, audio-master, QC, and media-approval contracts as the main film.
- Added deterministic trailer/social delivery reconciliation through `scripts/promo_delivery.py`; required promotional outputs become ready only when rendered media, primary approval paths, non-blocking QC, and referenced social copy agree. Optional omissions are recorded explicitly as `optional-missing`.
- Added release delivery manifests, `DELIV-###` records, required/optional deliverable state, checksum generation, and deterministic package collection through `scripts/release_package.py`.
- Added project schema and dependency nodes for media approval, audio masters, video finishing, executable timelines, film masters, trailer assets/masters, social campaigns/deliverables, delivery QC, and release packages with narrow downstream invalidation.
- Added four release-oriented playbooks: `film-finishing`, `trailer-campaign`, `social-campaign`, and `film-release-campaign`, and extended the main short-film, feature-film, screenplay-to-film, full-pipeline, and ComfyUI generation routes through actual finished-media state.
- Expanded the project initializer, project validator, standalone validator, output templates, core ID contract, editorial contract, and playbook reference validation for the release layer.
- Expanded deterministic coverage from 17 to 26 tests, including real local FFmpeg integration tests that build and verify a film master, a trailer master, a vertical social master, and a deterministic 16:9-to-9:16 reframe. These are deterministic media tests, not model smoke tests.
- Expanded future live-model regression definitions from 40 to 52 with finishing/release cases for approval, QC override, audio timing, master completion, trailers, social aspect adaptation, marketing fact discipline, narrow invalidation, release packaging, and MLT secondary-output behavior.
- Used the user-provided Pippa Pebblehoof Production Studio as a capability benchmark for complete-film, trailer, and social-campaign output. The implementation is original and does not bundle or require that studio.
- Live small-model smoke testing remains intentionally deferred while prototype development continues.

## 00.00.05 - 2026-08-19

- Added stable `LINE-###` screenplay production-unit identities and `02_screenplay/line_manifest.jsonl` so exact dialogue, action, movement, and transitions remain traceable through production.
- Added `production-capabilities` with a tool-neutral registry for available, unavailable, conditional, and unknown locations, actions, camera behaviors, audio features, and generation constraints.
- Added `performance-blocking` to separate position-changing movement from gestures, object interactions, posture, and other playable performer action.
- Added a portable `shooting-script` compiler contract linking source lines, current positions, moves, actions, shot IDs, and timing without replacing the Fountain screenplay.
- Added deterministic `production-coverage` with `scripts/production_coverage.py` to detect silently skipped lines, missing voice, missing blocking, missing shot coverage, text drift, unresolved shots, and timing conflicts.
- Added `media-qc` and `04_generation/take_qc.jsonl` for observable script-faithfulness, identity, background, spatial, action, motion, physical, artifact, dialogue-sync, and subtitle-sync checks before creative selection.
- Added a validator rule that prevents QC-failed takes from being selected unless an explicit `qc_override` and reason are recorded.
- Added the `executable-production-plan` playbook and integrated capability constraints, blocking, shooting-script compilation, coverage auditing, and media QC into short-film, feature-film, screenplay-to-film, and ComfyUI generation paths.
- Expanded the project validator for line manifests, production capabilities, performance blocking, shooting scripts, media QC, exact dialogue preservation, and cross-ID resolution.
- Added optional semantic/normalized frame-region constraints to model-neutral shot briefs for deliberate multi-subject composition without making bounding boxes a universal requirement.
- Added deterministic tests for executable production coverage and QC override behavior, plus new future weak-model regression cases. No local-model smoke tests were run.
- Reviewed MovieAgent and FilmAgent again for hierarchical planning, production-state annotations, capability-constrained execution, and separated automated versus creative media evaluation. Private chain-of-thought fields from research systems were deliberately not adopted.

## 00.00.04 - 2026-08-19

- Added durable narrative-state tracking for scene order, character life/location/knowledge state, props, `QST-###` questions, `PROM-###` setups/payoffs, and chronology-sensitive appearances.
- Added `character-sim`, `audience-sim`, `story-review`, and bounded `crew-review` with Critique-Correct-Verify and Debate-Judge protocols.
- Added progressive storyboard planning from narrative anchors through visual boards, sequence boards, and motion handoff.
- Added `TAKE-###` candidate tracking and explicit take selection rather than treating the newest render as approved.
- Expanded source-aware story research and revision verification, and added deterministic narrative-state and take-selection tests.
- Kept live small-model smoke testing explicitly deferred while the package remains in prototype development.

## 00.00.03 - 2026-08-19

- Added first-class standalone ComfyUI operation with a discoverable `comfyui` router and eight specialist skills for discovery, workflows, execution, assets, official CLI integration, MCP interoperability, Comfy API v2, and troubleshooting.
- Added a dependency-free native ComfyUI HTTP controller for server probing, live node/model discovery, API-workflow validation, submission, history polling, queue inspection, targeted cancellation, input image and mask upload, output extraction/download, and ComfyUI memory release.
- Added durable ComfyUI project state under `04_generation/comfyui/`, including capability snapshots, preserved workflows, templates, fragments, blueprints, inputs, prompt-id keyed run records, and collected outputs.
- Added API/UI workflow detection and safe API-input patching without opaque widget-index edits.
- Added live validation for installed class types, required inputs, live enum choices, links, deprecated/experimental status, and output-node presence.
- Added an optional official comfy-cli bridge for workspace/lifecycle commands, template and node discovery, workflow slots/notes, decompose/compose, execution, jobs, download, resource inspection, and memory release.
- Expanded the comfy-cli bridge with live model catalog queries, workflow dependency reports, guarded custom-node install/reinstall/uninstall/update/fix operations, guarded workflow dependency installation, and guarded model downloads. Broad `all` mutations and credential-bearing model URLs are refused.
- Added an append-only ComfyUI run index that maps stable story-film item IDs to submit, completion, cancellation, and download events so resubmits never erase prior prompt identity.
- Added optional comfy-mcp operational guidance based on its canonical asynchronous job, template compatibility, dependency, remote-target, VRAM, authentication, and spend-consent flows.
- Added a small Comfy API v2 client for durable jobs, cancellation, asset upload/metadata/download, idempotency keys, and proxy/cloud-compatible operation.
- Added ComfyUI security rules for untrusted workflow notes, third-party custom-node installation, credential separation, paid partner execution, network exposure, model files, and destructive actions.
- Added three ComfyUI story-film playbooks: operate, generate, and troubleshoot.
- Expanded the weak-model eval suite from 17 to 27 cases with ComfyUI-specific regressions.
- Expanded deterministic tests from 5 to 13, including a fake live ComfyUI server and fake API v2 job surface.
- Adopted current official comfy-cli source-oriented workflow guidance: reusable work prefers templates, fragments, blueprints, and composition; small one-off API graphs may still use preserved direct patches.

## 00.00.02 - 2026-08-19

- Established Badgids-Story-Film-Skills as a standalone product and removed assumptions that ComfyUI-Pi-Agent or any other external skill pack is installed.
- Added a standalone contract and validation that rejects required-capability delegation to external skills.
- Added native visual-bible and moodboard planning.
- Added native portable previz planning for scene geometry, blocking, actor paths, eyelines, camera positions, and cut intent.
- Expanded reference-asset planning with native character, location, prop, style, voice, and contact-sheet specifications.
- Reworked ComfyUI handoff into a self-contained portable generation package rather than an external-skill dependency.
- Reworked production diagrams so the suite always emits its own semantic JSON and Markdown or Mermaid representation when appropriate.
- Added a portable editorial package with timeline, subtitles, stems, cue mapping, missing-media tracking, and interchange-ready records.
- Added version enforcement using the `00.00.00` scheme and exact patch increments of one.
- Expanded the weak-model evaluation suite with standalone-product regression cases and static dependency checks.
- Retained dramaturgy gates, dependency invalidation, untrusted-input handling, style checks, and model-specific adapters from the prior development pass.

## 00.00.01 - 2026-08-19

- Initial standalone story, book, screenplay, directing, continuity, production, prompt, audio, and post-production skill suite.
- Added long-form book and feature-film playbooks with file-backed batching for small models.
- Added prompt adapters for Qwen Image 2512, Qwen Image Edit 2511, Krea 2, MiniMax H3, LTX 2.5, Qwen3 TTS, ACE-Step 1.5 XL, MiniMax Music 3, and Stable Audio 3.
- Added project initialization and validation scripts.
- Added hard style checks for em dash characters and common prompt shortcuts.
