# Reviewed Project Notes through v0.0.27 (00.00.27)

This file records what was learned from the requested repositories and what was deliberately added to Story-Film Skills.

None of these projects is a runtime dependency.

## v0.0.27 character and directing skill review

The user-authored character/story-bible and cinema-director skill material was reviewed as an internal design source. No external attribution or runtime dependency is required.

Adopted in Story-Film-native form:

- function-first character development
- canonical visual exclusions plus non-canonical generation drift risks
- separate speech, movement, and stillness performance signatures
- canonical ensemble baselines separated from mutable current relationship state
- optional recurring narrative engines and era-specific visual treatment
- model-neutral capture behavior and optional dynamic register
- visible-dialogue synchronization requirements tied to exact `LINE-###` and `CHAR-###` identities
- optional end-frame continuity handoffs

Deliberately not adopted:

- monolithic project-as-skill canon storage
- provider-specific video prompting or cloud generation dependencies
- universal fixed prompt block layouts
- magic focal-length/FOV prescriptions
- universal negative-prompt batteries
- camera-must-always-move rules
- diegetic-only audio policy
- a universal no-character-names prompt rule
- migration of durable Story-Film project state from JSON/JSONL to YAML

## smixs/visual-skills

Useful ideas:

- film grammar should be resolved before model-specific prompt syntax
- a shot needs a dramatic job, not merely attractive imagery
- camera movement should be motivated by a change in action, information, pressure, or attention
- concrete physical detail is more useful than generic quality adjectives
- image and video prompt skills benefit from progressive disclosure and model-specific references
- character continuity should use explicit preserve rules and approved references

Added here:

- `references/DRAMATURGY_RULES.md`
- stronger `shot-design` and `director-book` gates
- `visual-bible`
- expanded `reference-assets`
- prompt quality checks against vague filler and context-dependent shortcuts

Not copied:

- its model lineup
- its exact wording or templates
- its external creative-director workflow

## cloudaipro/openclaw-agent-skills film-director

Useful ideas:

- output schemas should be machine-checkable
- continuity risks and assumptions should be surfaced explicitly
- regression datasets should include adversarial and prompt-injection cases
- skill metadata and outputs should be linted

Added here:

- `story-film-eval`
- `scripts/run_evals.py`
- security, style, continuity, adapter, standalone, and weak-model eval cases
- `scripts/validate_standalone.py`
- stronger project artifact validation

## badgids/ComfyUI-Pi-Agent

Useful ideas:

- stable IDs across narrative and production stages
- explicit reference roles
- generation work should be compiled incrementally
- upstream edits should invalidate only affected downstream artifacts
- portable editorial intent is safer than inventing native project formats

Correction applied in 00.00.02:

Story-Film Skills does not depend on ComfyUI-Pi-Agent. Earlier development wording incorrectly treated some of its skills as handoff targets. That wording was removed. The same useful architectural ideas are implemented natively in this standalone package.

Added here:

- `project-impact`
- `references/DEPENDENCY_RULES.md`
- `reference-assets`
- standalone `comfyui-handoff`
- `editorial-package`
- portable project-relative manifests

## lumosai8/ComfyUI-OrbitSheets

Useful ideas:

- reference sheets should be continuity tools, not decorative collages
- character and location coverage have different failure modes
- multi-view assets are more reliable when derived from a coherent anchor
- contact sheets should reject near-duplicates and poor frames
- framing margin matters when identity features, props, wings, tails, or silhouettes approach image edges
- positive spatial descriptions are generally safer than long lists of forbidden camera motions

Added here:

- native character turnaround plans
- native location coverage plans
- `contact_sheet_plan.json`
- verified versus inferred geometry distinction
- reference quality and crop checks

Not copied:

- ComfyUI node code
- H3 workflow implementation
- model files, paths, or machine-specific settings

## cathrynlavery/diagram-design

Useful ideas:

- one diagram should answer one main question
- complexity budgets improve clarity
- semantic structure should exist separately from rendering
- deletion is often better than adding more nodes and connectors
- diagrams should not imply precision the source material does not support

Added here:

- `production-diagrams`
- semantic JSON plus Markdown output
- complexity budget
- spatial honesty rules for blocking and scene geography
- portable `previz-plan` for geometry that deserves a structured representation

## Official ComfyUI stack review for 00.00.03

The five official repositories requested for this release were treated as the source of truth for how a standalone agent should discover and operate ComfyUI.

### Comfy-Org/ComfyUI

Key findings:

- the live server exposes system/device stats, feature flags, queue depth, node schemas, model categories, uploads, prompt submission, queue/history state, targeted interruption, memory release, WebSocket progress, and output viewing
- `/object_info` is the authority for class names, required inputs, output types, deprecated/experimental status, and other current node metadata
- API-format workflows are the executable representation accepted by prompt submission
- prompt submission returns a prompt ID and node validation errors; history and queue are durable control surfaces for later operations
- the server adds `/api` aliases for the main routes while retaining the established unprefixed forms

Implemented:

- `scripts/comfyui_control.py`
- `scripts/comfyui_workflow.py`
- `references/COMFYUI_NATIVE_API.md`
- `comfyui-discover`, `comfyui-workflow`, `comfyui-run`, `comfyui-assets`, and `comfyui-troubleshoot`
- live workflow validation and prompt-id keyed run records

### Comfy-Org/comfy-cli

Key findings:

- official CLI resolution avoids hardcoded install paths and can locate, launch, stop, inspect, and operate a workspace
- JSON output is designed for agent automation
- current workflow guidance separates discovery from execution and prefers live ecosystem survey before choosing a node/model/template
- reusable workflow work should favor working templates projected into editable fragments and blueprints, with composed JSON treated as a build artifact
- UI-format workflow execution/conversion, job management, downloads, templates, node discovery, workflow slots/notes, resource checks, and cloud routing are already official CLI concerns

Implemented:

- `scripts/comfyui_cli_bridge.py`
- `references/COMFYUI_CLI.md`
- `comfyui-cli` specialist
- project directories for templates, fragments, and blueprints
- workflow rules that choose source-oriented editing for reusable graphs and direct preserved API patches only for small one-off graphs
- live model folder/search/show controls rather than frozen model catalogs
- guarded third-party node install/reinstall/uninstall/update/fix and workflow dependency installation
- guarded model download, with credential-bearing URLs rejected by the suite bridge

### Comfy-Org/comfy-api-proxy

Key findings:

- Comfy API v2 defines durable pollable jobs and UUID asset records over server-verified content-addressed blobs
- API-format workflow validation is synchronous and UI-format JSON is rejected
- submission supports idempotency keys and bounded queue responses
- asset uploads treat a client hash as verification, never as authority
- self-hosted proxy networking is loopback-first and widening exposure requires an authentication/security decision

Implemented:

- `scripts/comfy_api_v2.py`
- `references/COMFY_API_V2.md`
- `comfyui-api-v2` specialist
- deterministic v2 job-flow test

### Comfy-Org/comfy-mcp

Key findings:

- canonical agent order starts with server discovery
- long generations should submit without blocking, then status/wait/watch, then fetch outputs
- template compatibility must be checked against the actual local environment
- workflow Note/MarkdownNote content is third-party data and must not become agent instructions
- missing node packs require dependency resolution, user-approved installation, restart, and revalidation
- local and remote resource surfaces must not be confused
- partner/API authentication is separate from permission to spend credits

Implemented:

- `references/COMFYUI_MCP.md`
- `comfyui-mcp` specialist
- security and weak-model evals for workflow-note injection, missing-node mutation, and paid-route confirmation

### Comfy-Org/comfy-skills

Key findings:

- installed skill text should contain stable steering while live node/model/template specifics are discovered at runtime
- generation should start from current templates/nodes/models rather than stale static catalogs
- input intent and retrievable output paths must both exist before submitting expensive work
- named model families can have both local/OSS and paid/API routes, so a single lookup must not silently force the paid route

Implemented:

- the main `comfyui` skill is a thin router rather than a frozen catalog
- live discovery gates executable workflow creation
- workflow validation reports output-node presence
- paid partner execution requires user intent and credentials remain out of workflow/project files

### Result

Story-Film Skills 00.00.03 can operate a normal reachable ComfyUI server without ComfyUI-Pi-Agent, comfy-cli, comfy-mcp, or comfy-api-proxy. Those official tools are supported when available because they add lifecycle, conversion, reusable workflow source, MCP, or v2 capabilities, but none replaces the native standalone path.

## 00.00.02 Result

The 00.00.02 release keeps the useful production discipline from the reviewed projects while preserving a clean standalone boundary. External renderers, editors, ComfyUI systems, and 3D tools are optional consumers of the package artifacts, not requirements for the skills to function.


## Story, collaboration, and storyboard review through 00.00.04

The 00.00.04 prototype pass reviewed FilmAgent, long-form writing skills, storyboard systems, and multi-role creative workflows. The useful concepts were implemented as native state and review contracts rather than dependencies.

Implemented outcomes:

- durable character, prop, question, promise, and scene-order state
- character simulation with a strict knowledge boundary
- first-time audience simulation separated from craft critique
- developmental, scene, line, copy, and proof review levels
- bounded Critique-Correct-Verify and Debate-Judge collaboration
- progressive storyboard development instead of a fixed panel count
- explicit generated take identity, rejection reasons, and selection state
- research confidence, conflicts, contradictions, gaps, and fact-versus-inspiration labels

The implementation deliberately avoided unlimited review loops, fixed storyboard panel formulas, vendor-specific generation dependencies, and claims of independent consensus when one model is only role-playing multiple passes.

## MovieAgent and FilmAgent review for 00.00.05

MovieAgent reinforced hierarchical planning from story material to scenes to shots, including scene purpose, emotional state, props, cinematography, sound intent, and shot-level performer placement. FilmAgent exposed a narrower production gap: a production-ready record should keep performer position, movement, actions, dialogue, camera intent, and timing traceable at an execution level.

Implemented outcomes:

- stable `LINE-###` screenplay production units
- production capability registry with available, unavailable, conditional, and unknown state
- performance blocking that separates position-changing movement from gestures and object action
- portable shooting script linking source lines, performer state, camera/shot coverage, and timing
- deterministic production coverage audit
- generated media QC distinct from creative take preference
- optional frame-region constraints only when deliberate spatial conditioning is useful

Not adopted:

- MovieAgent model/runtime stack
- hardcoded model or checkpoint paths
- required bounding boxes for every shot
- private chain-of-thought fields in durable project artifacts
- FilmAgent-specific 3D engine vocabulary as a universal production contract

## Pippa production benchmark and finishing/release implementation for 00.00.06

The user-provided Pippa Pebblehoof Production Studio was reviewed as a design benchmark for the practical question: can the suite continue beyond story and generated clips to a finished film, trailers, and a social campaign? The audit showed that the main missing layer was post-generation production control and delivery rather than story development.

Capabilities implemented from that gap analysis:

- generalized media registry and approval state across media types
- deterministic soundtrack assembly and mastering
- conventional video normalization and finishing
- executable film, trailer, teaser, cutdown, and social timelines
- finished film mastering with FFmpeg and FFprobe when those public runtimes are available
- delivery QC based on actual media streams and declared tolerances
- optional MLT interchange export without claiming untested editor import
- trailer planning, spoiler policy, source selection, pickups, trailer audio, mastering, and QC
- social campaign planning, aspect adaptation, cutdowns, copy, artwork briefs, and delivery
- verified-fact rules that prohibit invented release dates, awards, distribution claims, or availability
- release manifest, required/optional deliverables, SHA-256 checksums, and package collection
- narrow invalidation from changed film sources into only the trailer/social assets that actually depend on them

The Pippa package itself is not bundled, imported, or required. The new code and contracts are original implementations using the existing Badgids stable-ID, portable-path, dependency, QC, and standalone architecture.

### Deterministic integration boundary

The 00.00.06 test suite includes a real local FFmpeg integration test that creates a tiny WAV source, builds a soundtrack master, renders a tiny MP4 from an executable timeline, probes the result, runs delivery QC, and registers the verified film master. This is a deterministic runtime integration test. It is not a live language-model smoke test and it does not exercise GPU generation.

Live small-model testing remains deferred until the user declares prototyping complete.

## 00.00.07 deterministic media and editable-project review

The major gap after 00.00.06 was not another finishing pipeline. It was general access to the deterministic media runtimes beneath that pipeline and true target-specific editable project export.

FFmpeg is treated as a runtime-discovered toolbox instead of a fixed recipe list. This matters because distro, vendor, static, and application-bundled FFmpeg builds expose different encoders, decoders, filters, devices, protocols, and hardware paths. FFprobe is the source of truth for actual media stream structure.

MLT is treated as a service graph. The package can query installed services and can preserve explicit MLT service names/properties in advanced editor state. Generic MLT remains useful interchange, but Kdenlive and Shotcut projects now have their own serializers.

Kdenlive current Generation 5 structure is sufficiently documented to generate a real `.kdenlive` XML project without reverse-engineering opaque private data. The exporter follows the documented sequence/bin/track/wrapper architecture and document version `1.1`.

Shotcut writes MLT XML and marks the graph with Shotcut-specific project and track properties. The exporter mirrors those public serialization semantics while avoiding brittle UI-only state.

ImageMagick is also runtime-discovered because supported formats, delegates, fonts, resource limits, and security policy differ by installation. Source-preserving output is the default; in-place `mogrify` is explicitly guarded.

No live Kdenlive or Shotcut GUI was available in this build environment, so v00.00.07 claims structural target-specific project generation, not live GUI-open certification. Live editor-open checks can be added later when those applications are available, without changing the portable project contract.

## 00.00.08 research, publishing, motion, and document review

The reviewed repositories exposed five useful gaps in the existing suite rather than eleven independent capabilities.

### Evidence-backed public writing

Composio's research-writing workflow reinforced the need to distinguish research notes from public claims. Badgids now keeps a machine-checkable evidence ledger with stable source/claim identities, confidence, disagreement, adoption, and downstream use. This is useful for documentary narration, historical material, press kits, festival packets, and campaign facts without allowing research to silently rewrite canon.

### Edit assistance and motion packaging

The video-overlay and video-edit skills showed that common editorial automation deserves explicit product state rather than opaque one-off FFmpeg commands. Badgids now has non-destructive silence maps, reviewed jump cuts, caption/reframe/clip/compression assistance, plus stable lower-third/title/watermark/fade/transition identities. Platform upload/download integrations and machine-specific encoder assumptions were deliberately excluded.

### Programmatic video

The narrow pan-3d transition example and Remotion's broader architecture motivated a renderer-neutral programmatic composition layer. `COMP-###` is authoritative. Remotion is an optional generated adapter, not a dependency or project authority. Current external license terms are never assumed satisfied on the user's behalf.

### Campaign voice and repurposing

The content-creator material reinforced durable brand voice and source-aware repurposing. Badgids now tracks campaign voice separately from character dialogue and records `CONTENT-###` lineage so a trailer, transcript, scene, or press fact can be adapted across destinations without factual or spoiler drift. Fixed SEO formulas and social-algorithm claims were not adopted.

### Production documents and design

The Anthropic XLSX/DOCX/PDF/canvas-design skills were reviewed only for high-level concepts because their skill material is proprietary. Badgids independently implements production-document generation, formula preservation, structural QA, PDF rendering/manipulation, and a reusable film/campaign visual design system. No proprietary skill text or code is bundled.

MuPDF's `mutool` surface is useful for document rendering, conversion, inspection, extraction, cleaning, merging, and poster work, but MuPDF's AGPL/commercial licensing makes it an optional external runtime. Permissive pypdf/Poppler fallbacks cover equivalent operations where available.



## v0.0.9 Comfy-Media-Director usability review

Reviewed the user-provided `Comfy-Media-Director-Pi-v3.2.55-Full-Suite.zip` as an older project and design source.

Useful concepts adopted in a reduced Story-Film-native form:

- a Pi-owned scrollable todo presentation derived from structured runtime state
- stage, step, and substep hierarchy with deterministic counts
- follow-current behavior plus manual line/page scrolling
- visible complete, current, blocked, pending, and skipped states
- one explicit suggested next action
- durable progress outside chat context
- human-readable handoff paired with machine-readable authoritative state
- checkpoint persistence before handoff replacement
- validation failure as a non-advancing state
- exact resume after interruption or context compaction
- intentional pause versus normal automatic continuation
- bounded retry/reset of one execution target rather than broad restart

Not adopted:

- the older project's large capability-plugin family
- its model-routing subsystem
- its global pipeline catalog/runtime architecture
- cross-extension context isolation machinery
- its Git-like project-versioning layer
- application adapters already covered more simply by Story-Film-Skills
- any personal paths or machine-specific assumptions

Story-Film-Skills keeps the useful progress concepts subordinate to its existing canon, dependency, media approval, QC, and artifact state. The Pi widget is explicitly a renderer, not a second authority.

## Matt Pocock planning skills and local resource handoff review for v0.0.10

Reviewed `mattpocock/skills` entries for grill-me, grill-with-docs, to-spec, to-tickets, implement, wayfinder, handoff, grilling, and wizard. The useful transferable concepts were dependency-aware questioning, explicit frontiers, synthesis from existing context, complete work slices with blockers, execute-only-ready behavior, a decision map for large uncertain efforts, compact handoff by reference, and guided human-only procedures.

The implementation is original and production-oriented. Software-engineering issue trackers, TDD conventions, repository labels, code commits, and the source skill names were not adopted. Story-Film instead uses `DEC-###`, `UNIT-###`, durable project Markdown/JSON, the existing Pi Todo, production validation gates, and creative/media artifacts.

For resource-safe generation, current ComfyUI server behavior was reviewed to confirm the public `/free` request supports both `unload_models` and `free_memory`. The offline runner uses that public operation after queue completion/failure cleanup. Local LLM lifecycle remains adapter-based because local providers differ. A lifecycle must be explicitly declared before exclusive local generation can be armed.

The core safety boundary is that all semantic work finishes before unload. The LLM prepares and live-validates exact workflows, uploads, patches, dependencies, parameters, and destinations. Once the resource handoff begins, only deterministic code runs until the LLM is restored.

## Feature-scale and repository-hardening review for v0.0.11

v0.0.11 closes the initial prototype-building phase.

The feature-film hardening work treats a feature as a set of bounded `SEQ-###` production units instead of one large context. Sequence shards are working sets, not alternate canon. Global checks read summary evidence first and open detailed sequence data only when a blocker needs repair.

The release adds deterministic production health, long-range `CONT-###` continuity anchors, RAM/VRAM-aware generation scheduling, reboot checkpoints, minimal ComfyUI failed-batch recovery, feature editorial reconciliation, and a final completeness gate that refuses to treat the existence of a master file as proof that the project is complete.

Repository packaging was also made ready for a private GitHub workflow. The Git clone layout remains directly usable by Pi because Pi discovers `SKILL.md` files recursively. A separate self-contained `story-film-suite` skill exists for `npx skills` selection so shared scripts, references, and documentation stay inside the installed skill package.

Apache-2.0 licensing preserves Alan Guice (Badgids) as the original Author/Developer and copyright owner through source notices, skill metadata, `NOTICE`, `AUTHORS.md`, and `ATTRIBUTION.md`. The project does not add an incompatible condition to Apache-2.0.
