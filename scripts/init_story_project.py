#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import argparse, json
from pathlib import Path
from datetime import datetime, timezone
from model_preferences import default_preferences

DIRS = [
    '00_project', '00_project/reviews', '00_project/wizards', '00_project/shards', '00_project/recovery', '01_story', '01_story/chapters', '01_story/simulations', '01_story/research', '02_screenplay',
    '03_preproduction/scene_breakdowns',
    '03_preproduction/continuity',
    '03_preproduction/documents',
    '03_preproduction/references/character',
    '03_preproduction/references/location',
    '03_preproduction/references/props',
    '03_preproduction/references/style',
    '03_preproduction/references/voice',
    '03_preproduction/references/music',
    '03_preproduction/diagrams',
    '03_preproduction/previz',
    '03_preproduction/storyboards/sequence_boards',
    '04_generation/prompts/qwen-image-2512',
    '04_generation/prompts/qwen-image-edit-2511',
    '04_generation/prompts/krea-2',
    '04_generation/prompts/minimax-h3',
    '04_generation/prompts/ltx-2-5',
    '04_generation/prompts/qwen3-tts',
    '04_generation/prompts/ace-step-xl',
    '04_generation/prompts/minimax-music-3',
    '04_generation/prompts/stable-audio-3',
    '04_generation/comfyui/default_workflows',
    '04_generation/comfyui/workflows',
    '04_generation/comfyui/templates',
    '04_generation/comfyui/fragments',
    '04_generation/comfyui/blueprints',
    '04_generation/comfyui/inputs',
    '04_generation/comfyui/runs',
    '04_generation/comfyui/outputs',
    '04_generation/comfyui/offline',
    '05_post',
    '05_post/finished',
    '05_post/masters',
    '05_post/qc',
    '05_post/render_reports',
    '05_post/editorial',
    '05_post/editorial/kdenlive',
    '05_post/editorial/shotcut',
    '05_post/tool_runs',
    '05_post/edit_assist',
    '05_post/graphics',
    '05_post/programmatic',
    '05_post/programmatic/remotion',
    '06_release',
    '06_release/trailers',
    '06_release/social',
    '06_release/social/masters',
    '06_release/social/qc',
    '06_release/artwork',
    '06_release/documents',
    '06_release/package',
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project_dir')
    ap.add_argument('--title', default='Untitled')
    ap.add_argument('--format', default='short-film')
    args = ap.parse_args()
    root = Path(args.project_dir).expanduser().resolve()
    for d in DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)
    state = root / '00_project/state.json'
    canon = root / '00_project/canon.json'
    brief = root / '00_project/brief.md'
    dependencies = root / '00_project/dependencies.json'
    ref_manifest = root / '03_preproduction/references/reference_manifest.json'
    story_state = root / '01_story/story_state.json'
    selections = root / '04_generation/selections.json'
    capabilities = root / '03_preproduction/production_capabilities.json'
    media_registry = root / '00_project/media_registry.jsonl'
    media_approvals = root / '00_project/media_approvals.json'
    delivery_specs = root / '06_release/delivery_specs.json'
    tool_capabilities = root / '00_project/tool_capabilities.json'
    document_manifest = root / '00_project/document_manifest.json'
    claim_ledger = root / '01_story/research/claims.jsonl'
    content_lineage = root / '06_release/social/content_lineage.jsonl'
    pipeline_progress = root / '00_project/pipeline_progress.json'
    progress_events = root / '00_project/progress_events.jsonl'
    handoff = root / '00_project/HANDOFF.md'
    creative_decisions = root / '00_project/creative_decisions.jsonl'
    work_units = root / '00_project/work_units.json'
    work_units_md = root / '00_project/work_units.md'
    decision_map = root / '00_project/decision_map.json'
    decision_map_md = root / '00_project/decision_map.md'
    resource_policy = root / '00_project/resource_policy.json'
    model_preferences = root / '00_project/model_preferences.json'
    workflow_preferences = root / '00_project/workflow_preferences.json'
    workflow_sources = root / '00_project/workflow_sources.json'
    workflow_catalog = root / '00_project/comfyui_workflow_catalog.json'
    resource_handoff = root / '00_project/resource_handoff.json'
    resource_events = root / '00_project/resource_events.jsonl'
    sequence_manifest = root / '00_project/sequence_manifest.json'
    sequence_manifest_md = root / '00_project/sequence_manifest.md'
    shard_index = root / '00_project/shards/index.json'
    shard_index_md = root / '00_project/shards/index.md'
    recovery_checkpoint = root / '00_project/recovery/checkpoint.json'
    recovery_journal = root / '00_project/recovery/journal.jsonl'
    continuity_anchors = root / '03_preproduction/continuity/anchors.jsonl'
    continuity_observations = root / '03_preproduction/continuity/observations.jsonl'
    generation_resources = root / '04_generation/generation_resources.json'
    if not state.exists():
        state.write_text(json.dumps({
            'schema_version': 1,
            'project_title': args.title,
            'format': args.format,
            'phase': 'brief',
            'artifacts': {},
            'open_decisions': [],
            'last_updated': datetime.now(timezone.utc).isoformat(),
        }, indent=2) + '\n', encoding='utf-8')
    if not canon.exists():
        canon.write_text(json.dumps({
            'schema_version': 1,
            'characters': {},
            'locations': {},
            'props': {},
            'relationship_baselines': {},
            'world_rules': [],
            'visual_rules': [],
            'audio_rules': [],
            'locked_facts': [],
        }, indent=2) + '\n', encoding='utf-8')
    if not dependencies.exists():
        template = Path(__file__).resolve().parents[1] / 'references/default_dependencies.json'
        dependencies.write_text(template.read_text(encoding='utf-8'), encoding='utf-8')
    if not ref_manifest.exists():
        ref_manifest.write_text(json.dumps({
            'schema_version': 1,
            'references': []
        }, indent=2) + '\n', encoding='utf-8')
    if not story_state.exists():
        story_state.write_text(json.dumps({
            'schema_version': 1,
            'scene_order': [],
            'characters': {},
            'props': {},
            'questions': {},
            'promises': {},
            'events': [],
        }, indent=2) + '\n', encoding='utf-8')
    if not capabilities.exists():
        capabilities.write_text(json.dumps({
            'schema_version': 1,
            'source': 'declared',
            'locations': {},
            'blocking_anchors': {},
            'actions': {},
            'camera_behaviors': {},
            'audio': {},
            'generation': {},
            'constraints': [],
            'unknowns': [],
        }, indent=2) + '\n', encoding='utf-8')
    if not media_registry.exists():
        media_registry.write_text('', encoding='utf-8')
    if not media_approvals.exists():
        media_approvals.write_text(json.dumps({
            'schema_version': 1,
            'groups': {},
        }, indent=2) + '\n', encoding='utf-8')
    if not tool_capabilities.exists():
        tool_capabilities.write_text(json.dumps({
            'schema_version': 1,
            'captured_at': '',
            'tools': {},
            'status': 'not-discovered',
        }, indent=2) + '\n', encoding='utf-8')
    if not document_manifest.exists():
        document_manifest.write_text(json.dumps({
            'schema_version': 1,
            'documents': [],
        }, indent=2) + '\n', encoding='utf-8')
    if not claim_ledger.exists():
        claim_ledger.write_text('', encoding='utf-8')
    if not content_lineage.exists():
        content_lineage.write_text('', encoding='utf-8')
    if not pipeline_progress.exists():
        pipeline_progress.write_text(json.dumps({
            'schema_version': 1,
            'owner': 'story-film-skills',
            'pipeline_id': '',
            'label': '',
            'source_playbook': '',
            'status': 'inactive',
            'stages': [],
            'cursor': {},
            'next_action': '',
            'blocker': '',
            'last_completed': '',
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }, indent=2) + '\n', encoding='utf-8')
    if not progress_events.exists():
        progress_events.write_text('', encoding='utf-8')
    if not creative_decisions.exists():
        creative_decisions.write_text('', encoding='utf-8')
    if not work_units.exists():
        work_units.write_text(json.dumps({'schema_version': 1, 'units': [], 'updated_at': ''}, indent=2) + '\n', encoding='utf-8')
    if not work_units_md.exists():
        work_units_md.write_text('# Production Work Units\n\nNo work units have been defined.\n', encoding='utf-8')
    if not decision_map.exists():
        decision_map.write_text(json.dumps({'schema_version': 1, 'destination': '', 'notes': [], 'decisions': [], 'not_yet_specified': [], 'out_of_scope': [], 'updated_at': ''}, indent=2) + '\n', encoding='utf-8')
    if not decision_map_md.exists():
        decision_map_md.write_text('# Production Compass\n\nDestination: not set\n', encoding='utf-8')
    if not model_preferences.exists():
        model_preferences.write_text(json.dumps(default_preferences(), indent=2) + '\n', encoding='utf-8')
    if not workflow_preferences.exists():
        workflow_preferences.write_text(json.dumps({'schema_version': 1, 'selections': {}, 'updated_at': ''}, indent=2) + '\n', encoding='utf-8')
    if not workflow_sources.exists():
        workflow_sources.write_text(json.dumps({'schema_version': 1, 'sources': []}, indent=2) + '\n', encoding='utf-8')
    if not workflow_catalog.exists():
        workflow_catalog.write_text(json.dumps({
            'schema_version': 1, 'generated_at': '', 'category': '', 'query': '',
            'comfyui_url': '', 'count': 0, 'workflows': [], 'warnings': []
        }, indent=2) + '\n', encoding='utf-8')
    if not resource_policy.exists():
        resource_policy.write_text(json.dumps({
            'schema_version': 1,
            'local_llm': {
                'adapter': 'unconfigured',
                'runtime_location': 'unknown',
                'endpoint': '',
                'location_evidence': [],
                'unload_command': [],
                'reload_command': [],
                'health_command': [],
                'health_url': '',
                'unload_timeout_s': 120,
                'reload_timeout_s': 300,
                'health_timeout_s': 300,
            },
            'comfyui': {
                'url': 'http://127.0.0.1:8188',
                'request_timeout_s': 30,
                'queue_drain_timeout_s': 120,
                'free_settle_s': 2,
            },
            'exclusive_generation': {
                'release_timeout_s': 900,
            },
        }, indent=2) + '\n', encoding='utf-8')
    if not resource_handoff.exists():
        resource_handoff.write_text(json.dumps({
            'schema_version': 1, 'phase': 'idle', 'message': 'No resource handoff is active.',
            'job_index': 0, 'job_total': 0, 'current_job_id': '', 'llm_state': 'unknown',
            'comfyui_state': 'unknown', 'outputs': [], 'error': '',
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }, indent=2) + '\n', encoding='utf-8')
    if not resource_events.exists():
        resource_events.write_text('', encoding='utf-8')
    if not sequence_manifest.exists():
        sequence_manifest.write_text(json.dumps({
            'schema_version': 1, 'project_title': args.title, 'sequence_size_hint': 5,
            'sequences': [], 'status': 'not-initialized', 'updated_at': datetime.now(timezone.utc).isoformat(),
        }, indent=2) + '\n', encoding='utf-8')
    if not sequence_manifest_md.exists():
        sequence_manifest_md.write_text('# Feature Sequence Plan\n\nNo `SEQ-###` records exist yet. Run `sequence_manager.py init` after the scene manifest is ready.\n', encoding='utf-8')
    if not shard_index.exists():
        shard_index.write_text(json.dumps({'schema_version': 1, 'generated_at': '', 'shards': []}, indent=2) + '\n', encoding='utf-8')
    if not shard_index_md.exists():
        shard_index_md.write_text('# Context Shard Index\n\nNo sequence shards exist yet.\n', encoding='utf-8')
    if not recovery_checkpoint.exists():
        recovery_checkpoint.write_text(json.dumps({'schema_version': 1, 'status': 'none'}, indent=2) + '\n', encoding='utf-8')
    if not recovery_journal.exists():
        recovery_journal.write_text('', encoding='utf-8')
    if not continuity_anchors.exists():
        continuity_anchors.write_text('', encoding='utf-8')
    if not continuity_observations.exists():
        continuity_observations.write_text('', encoding='utf-8')
    if not generation_resources.exists():
        generation_resources.write_text(json.dumps({
            'schema_version': 1,
            'machine': {'status': 'unconfigured', 'vram_gib': None, 'ram_gib': None, 'vram_reserve_gib': 1.0, 'ram_reserve_gib': 4.0},
            'profiles': {
                'image': {'vram_gib': 12.0, 'ram_gib': 8.0, 'exclusive_gpu': True, 'estimated_seconds_per_job': 30.0, 'resident_group': 'image'},
                'video': {'vram_gib': 22.0, 'ram_gib': 20.0, 'exclusive_gpu': True, 'estimated_seconds_per_job': 180.0, 'resident_group': 'video'},
                'audio': {'vram_gib': 10.0, 'ram_gib': 8.0, 'exclusive_gpu': True, 'estimated_seconds_per_job': 45.0, 'resident_group': 'audio'},
                'cpu': {'vram_gib': 0.0, 'ram_gib': 4.0, 'exclusive_gpu': False, 'estimated_seconds_per_job': 30.0, 'resident_group': 'cpu'}
            }
        }, indent=2) + '\n', encoding='utf-8')
    if not handoff.exists():
        handoff.write_text(
            '# Story-Film Pipeline Handoff\n\n'
            'Pipeline: none\nStatus: inactive\nCurrent target: none\n'
            'Next action: Select a Story-Film playbook, then initialize pipeline progress.\n',
            encoding='utf-8',
        )
    if not delivery_specs.exists():
        delivery_specs.write_text(json.dumps({
            'schema_version': 1,
            'deliverables': [],
        }, indent=2) + '\n', encoding='utf-8')
    if not selections.exists():
        selections.write_text(json.dumps({
            'schema_version': 1,
            'shots': {},
        }, indent=2) + '\n', encoding='utf-8')
    if not brief.exists():
        brief.write_text(f'# Creative Brief\n\nTitle: {args.title}\nFormat: {args.format}\nTarget length:\nAudience:\nPremise:\nCore dramatic question:\nGenre:\nTone:\nPoint of view:\nMust include:\nMust avoid:\nProduction constraints:\nOpen decisions:\n', encoding='utf-8')
    print(root)

if __name__ == '__main__':
    main()
