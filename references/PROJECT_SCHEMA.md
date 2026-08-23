# Project Schema

A Story-Film Skills project uses this layout.

```text
00_project/
  brief.md
  state.json
  canon.json
  dependencies.json
  pipeline_progress.json            durable playbook execution cursor
  progress_events.jsonl             append-only progress transitions
  HANDOFF.md                         compact recovery pointer
  creative_decisions.jsonl           DEC-### creative/production decision ledger
  creative_production_spec.md        synthesized durable production specification
  work_units.json                     UNIT-### dependency-aware execution plan
  work_units.md                       human-readable work-unit companion
  decision_map.json                   large-project decision compass
  decision_map.md                     human-readable compass companion
  resource_policy.json                local LLM and ComfyUI lifecycle policy
  llm_model_snapshot.json              temporary exact local-model restore snapshot during handoff
  workflow_preferences.json           selected complete ComfyUI workflows by task
  workflow_sources.json               user-registered external workflow files/directories
  comfyui_workflow_catalog.json       latest numbered workflow-choice snapshot
  workflow_preflight.json             playbook-entry required/selected/missing workflow categories
  model_preferences.json              legacy model-selection compatibility/debug state
  comfyui_model_inventory.json         latest model folders and choices reported by the active ComfyUI server
  comfyui_model_inventory.md           human-readable ComfyUI model inventory
  resource_handoff.json               model-free runtime handoff status
  resource_events.jsonl               append-only resource transition events
  RESOURCE_RESUME.md                  post-generation resume pointer
  wizards/                            WIZ-### human-only procedures and Markdown guides
  artifact_hashes.json              optional checkpoint hashes
  media_registry.jsonl              generalized concrete media candidates
  media_approvals.json              current primary/alternate decisions by group
  tool_capabilities.json             discovered FFmpeg/MLT/ImageMagick/editor runtime facts
  reviews/
01_story/
  logline.md
  story_bible.md
  characters.md
  world.md
  beat_sheet.md
  scene_outline.md
  story.md
  book_plan.md
  chapter_state.json
  story_state.json
  research/
  simulations/
  chapters/
    CH-001.md
02_screenplay/
  screenplay.fountain
  scene_manifest.json
  line_manifest.jsonl
03_preproduction/
  continuity.md
  director_book.md
  production_capabilities.json
  performance_blocking.jsonl
  shooting_script.json
  production_coverage.json
  production_coverage.md
  visual_bible.md
  storyboard_plan.md
  storyboards/
    anchors.jsonl
    beat_board.jsonl
    sequence_boards/
    motion_handoff.jsonl
  shot_list.csv
  scene_breakdowns/
  references/
    reference_manifest.json
    reference_briefs.jsonl
    moodboard_briefs.jsonl
    contact_sheet_plan.json
    character/
    location/
    props/
    style/
    voice/
    music/
  diagrams/
  previz/
    SCN-001.json
    SCN-001.md
04_generation/
  shot_briefs.jsonl
  image_briefs.jsonl
  voice_cues.jsonl
  music_cues.jsonl
  sfx_cues.jsonl
  take_manifest.jsonl
  take_qc.jsonl
  selections.json
  comfyui_handoff.json
  comfyui/
    server_snapshot.json
    default_workflows/                 project-owned default workflows by task/model
    offline_batch.json                BATCH-### fully prepared model-free execution batch
    offline_batch_result.json         completed JOB-### results
    offline/                           optional prepared batch fragments/assets
    run_index.jsonl
    workflows/
    templates/
    fragments/
    blueprints/
    inputs/
    runs/
    outputs/
  prompts/
    qwen-image-2512/
    qwen-image-edit-2511/
    krea-2/
    minimax-h3/
    ltx-2-5/
    qwen3-tts/
    ace-step-xl/
    minimax-music-3/
    stable-audio-3/
05_post/
  edit_plan.md
  editorial_manifest.json
  subtitles.srt
  cue_sheet.csv
  video_finish.jsonl
  audio_mix.json
  timeline.json
  finished/
  masters/
    film_audio_master.wav
    film_master.mp4
  qc/
    film_master.json
  render_reports/
  tool_runs/
  editorial/
    editor_project.json              optional advanced multitrack editable-project state
    film_timeline.mlt                generic MLT interchange
    kdenlive/
      film_project.kdenlive
    shotcut/
      film_project.mlt
06_release/
  delivery_specs.json
  delivery_qc.json
  release_manifest.json
  SHA256SUMS.txt
  trailers/
    trailer_manifest.json
    assets.jsonl
    delivery_report.json
    TRL-001/
      timeline.json
      audio_mix.json
      subtitles.srt
      master.mp4
      qc.json
  social/
    campaign.json
    deliverables.jsonl
    copy.jsonl
    delivery_report.json
    calendar.csv
    art_briefs.jsonl
    SOC-001/
      timeline.json
      audio_mix.json
    masters/
    qc/
  artwork/
  package/
```

Not every creative artifact is required for every project. State, canon, dependencies, reference identity, media approval state, and the manifests needed by the requested endpoint form the durable control layer.


## `pipeline_progress.json`

This file records execution position for multi-step playbooks. It is separate from creative/project truth in `state.json`, canon, dependency records, and media registries. See `PIPELINE_PROGRESS.md`.

The optional Pi widget reads this file directly. The project remains resumable when the extension is not installed.

`progress_events.jsonl` records transitions. `HANDOFF.md` points a fresh session at the smallest current scope and is written last during checkpoints.

## Creative decisions, specifications, and work units

Use `CREATIVE_DECISION_PROTOCOL.md`, `CREATIVE_PRODUCTION_SPEC.md`, `PRODUCTION_WORK_UNITS.md`, and `PRODUCTION_COMPASS.md`. `DEC-###` records capture decision-relevant answers without private reasoning. `UNIT-###` records are executable creative/production slices with explicit blockers and acceptance criteria. For uncertain multi-session work, `decision_map.json` keeps the destination, resolved decisions, current frontier, not-yet-specifiable fog, and out-of-scope boundary.

## Resource-safe generation

Use `RESOURCE_SAFE_GENERATION.md` and `COMFYUI_OFFLINE_BATCH.md`. A `BATCH-###` must contain complete `JOB-###` workflows and `UP-###` inputs before the local LLM is unloaded. `resource_handoff.json` is runtime state only. The Pi progress extension may render it without invoking a model. ComfyUI outputs are authoritative only after the deterministic batch runner records them and cleanup has attempted model unload/free-memory.

## Rich-document Markdown companions

Use `DOCUMENT_COMPANIONS.md`. Every generated PDF, DOCX/DOTX, XLSX/XLSM/XLTX, PPTX/PPTM, ODT, ODS, or ODP requires a meaningful Markdown file with the same basename beside it.

## `state.json`

Minimum shape:

```json
{
  "schema_version": 1,
  "project_title": "Untitled",
  "format": "short-film",
  "phase": "brief",
  "artifacts": {},
  "open_decisions": [],
  "last_updated": ""
}
```

An artifact entry may be a status string or an explicit record containing `status` and `path`. Supported statuses are `missing`, `draft`, `approved`, `stale`, and `retired`.

## `canon.json`

Minimum shape:

```json
{
  "schema_version": 1,
  "characters": {},
  "locations": {},
  "props": {},
  "relationship_baselines": {},
  "world_rules": [],
  "visual_rules": [],
  "audio_rules": [],
  "locked_facts": []
}
```

Dictionary keys are stable IDs. Put the human-readable name inside each object.

`characters` may contain the richer optional identity and performance fields defined by `CHARACTER_PROFILE.md`. `relationship_baselines` stores canonical pair behavior only. Current relationship state belongs in `01_story/story_state.json`.

## Narrative and production execution

Use `NARRATIVE_STATE.md`, `CHARACTER_PROFILE.md`, `HIERARCHICAL_PRODUCTION_PLANNING.md`, `PRODUCTION_CAPABILITIES.md`, `PERFORMANCE_BLOCKING.md`, `VISIBLE_DIALOGUE_SYNC.md`, `SHOOTING_SCRIPT.md`, and `PRODUCTION_COVERAGE.md`. `LINE-###` records keep exact screenplay events traceable through voice, blocking, shots, generation, and postproduction.

## Generated media and approval

Use `TAKE_SELECTION.md`, `MEDIA_QC.md`, and `MEDIA_REGISTRY.md`.

- `TAKE-###` remains the creative identity of a generated shot candidate.
- `MEDIA-###` identifies a concrete file in the generalized registry.
- `00_project/media_approvals.json` is authoritative for current primary/alternate selection across all media classes.

## Postproduction

Use `AUDIO_MASTERING.md`, `VIDEO_FINISHING.md`, `EXECUTABLE_TIMELINE.md`, and `FILM_MASTERING.md`.

The portable editorial manifest describes editorial intent. The executable timeline and audio mix are machine-renderable contracts. A final master is complete only after the output file exists and passes its delivery gate.

## Deterministic media tools and editable projects

Use `FFMPEG_TOOLKIT.md`, `MLT_TOOLKIT.md`, `IMAGEMAGICK_TOOLKIT.md`, and `EDITOR_PROJECT_EXPORT.md`.

`00_project/tool_capabilities.json` is a runtime snapshot, not canon. Refresh it when the execution environment changes. `05_post/tool_runs/` holds reproducible `TOOL-###` operation manifests and reports. `05_post/editorial/editor_project.json` is the optional advanced multitrack source for Kdenlive/Shotcut export and uses stable `CLIP-###` source IDs plus `EDIT-###` placement IDs.

Generic `film_timeline.mlt` remains interchange. Target-specific `.kdenlive` and Shotcut `.mlt` outputs are generated by `scripts/editor_project_export.py` and must not be conflated with generic MLT XML.

## Promotional release work

Use `TRAILER_SYSTEM.md`, `SOCIAL_CAMPAIGN.md`, and `RELEASE_DELIVERY.md`.

Trailers and social video cutdowns reuse the same executable timeline and audio mix schemas as the film. Their source IDs remain connected to film shots, trailer pickups, copy, and campaign records so invalidation can stay narrow.

## `dependencies.json`

The dependency file records artifact edges and scope. Fine-grained projects may add keys such as `screenplay:SCN-014`, `shots:SCN-014`, `media:SHOT-014`, `trailer:TRL-001`, or `social:SOC-004`.

## Staleness rule

When an approved upstream artifact changes, calculate downstream impact first. Mark only affected outputs stale. A changed shot may invalidate its film edit entry and only the trailer/social deliverables that actually use it.

## Runtime execution state

ComfyUI execution remains optional for planning. FFmpeg/FFprobe, MLT/melt, and ImageMagick are transparent local runtimes for deterministic media work. Their absence does not invalidate portable project manifests, but an operation that requires a missing runtime cannot be claimed as executed. Kdenlive and Shotcut applications are not required to generate their project files, but target-version GUI import success must not be claimed unless actually tested.

## Evidence and public claims

Use `EVIDENCE_RESEARCH.md`. `01_story/research/claims.jsonl` stores `CLAIM-###` records separately from canon. Public-facing factual copy may reference only claims whose evidence status permits public use. Research never silently changes canon.

## Edit assist, motion graphics, and programmatic compositions

Use `EDIT_ASSIST.md`, `MOTION_GRAPHICS.md`, and `PROGRAMMATIC_VIDEO.md`.

- `05_post/edit_assist/` stores analysis maps and non-destructive derivative edits.
- `05_post/graphics/graphics.json` stores `GFX-###` overlays, titles, lower thirds, watermarks, mattes, fades, and transitions.
- `05_post/programmatic/compositions.json` stores portable `COMP-###` compositions.
- `05_post/programmatic/remotion/` is an optional generated Remotion adapter project. Remotion is never bundled or required.

## Campaign brand and content lineage

Use `CAMPAIGN_BRAND.md`. `06_release/social/brand_voice.json` defines project-approved voice constraints. `06_release/social/content_lineage.jsonl` uses `CONTENT-###` IDs to record what source material became each public content item, what transformation occurred, which `COPY-###` it uses, and which `CLAIM-###` records support factual statements.

## Production documents and PDFs

Use `PRODUCTION_DOCUMENTS.md`, `PDF_TOOLKIT.md`, and `DESIGN_SYSTEM.md`.

- `00_project/document_manifest.json` tracks requested `DOC-###` deliverables.
- `03_preproduction/documents/` stores working production documents.
- `06_release/documents/` stores approved release-facing documents.
- `06_release/artwork/design_system.json` stores reusable visual design rules for posters, one-sheets, title cards, social artwork, and motion graphics.
- MuPDF `mutool` may be used when installed and license-compatible, but it is optional and never bundled.



## Feature-scale production state

Use `FEATURE_SCALE_PRODUCTION.md` for long films.

- `00_project/sequence_manifest.json` and `.md` define `SEQ-###` production boundaries.
- `00_project/shards/` stores per-sequence context shards and an index. Sequence shards include only relevant canon and current story-state subsets instead of copying the full project state.
- `00_project/health_report.json` and `.md` summarize deterministic production health.
- `03_preproduction/continuity/anchors.jsonl` stores `CONT-###` long-range continuity anchors.
- `03_preproduction/continuity/observations.jsonl` stores continuity observations.
- `04_generation/generation_resources.json` declares machine and workload memory profiles.
- `04_generation/generation_schedule.json` and `.md` store the RAM/VRAM-aware job schedule.
- `00_project/recovery/` stores reboot checkpoints, journal events, and resume reports.
- `04_generation/comfyui/recovery_batch.json` and `.md` store minimal partial-batch retries.
- `05_post/editorial/reconciliation.json` and `.md` reconcile selected shots with the feature timeline.
- `06_release/completeness_audit.json` and `.md` are the final deterministic feature completion gate.

A sequence or context shard is not a second canon. Authoritative project files remain authoritative.

## Human-readable document rule

Every generated rich document format covered by `DOCUMENT_COMPANIONS.md` must have a meaningful same-basename Markdown companion. The project validator treats missing companions as blockers.
