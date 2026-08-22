#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_EXT = {'.md', '.txt', '.py', '.sh', '.ts', '.json', '.jsonl', '.csv'}

# These patterns indicate a required capability is being delegated to another skill pack.
FORBIDDEN = [
    re.compile(r'if (?:an? )?(?:compatible|installed) .*skill', re.I),
    re.compile(r'when .*skills? are installed', re.I),
    re.compile(r'hand (?:it|off|the .*brief) to .*skill', re.I),
    re.compile(r'requires? ComfyUI-Pi-Agent', re.I),
    re.compile(r'ComfyUI-Pi-Agent skills are installed', re.I),
]

ALLOW_SOURCE_FILES = {'SOURCES.md', 'CHANGELOG.md', 'validate_standalone.py'}


def main() -> int:
    errors = []
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip() if (ROOT / 'VERSION').exists() else ''
    if not re.fullmatch(r'\d{2}\.\d{2}\.\d{2}', version):
        errors.append(f'invalid VERSION {version!r}; expected 00.00.00')

    for p in ROOT.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in TEXT_EXT:
            continue
        if p.name in ALLOW_SOURCE_FILES or 'evals/cases' in str(p.relative_to(ROOT)):
            continue
        text = p.read_text(encoding='utf-8', errors='ignore')
        for rx in FORBIDDEN:
            if rx.search(text):
                errors.append(f'{p.relative_to(ROOT)}: external-skill dependency wording matches {rx.pattern!r}')

    required = [
        'references/STANDALONE_CONTRACT.md',
        'references/PREVIZ_SCHEMA.md',
        'references/EDITORIAL_PACKAGE.md',
        'skills/reference-assets/SKILL.md',
        'skills/previz-plan/SKILL.md',
        'skills/visual-bible/SKILL.md',
        'skills/editorial-package/SKILL.md',
        'skills/comfyui-handoff/SKILL.md',
        'references/COMFYUI_OPERATIONS.md',
        'references/COMFYUI_NATIVE_API.md',
        'references/COMFYUI_WORKFLOWS.md',
        'references/COMFYUI_CLI.md',
        'references/COMFYUI_MCP.md',
        'references/COMFYUI_MANAGED_RUNTIME.md',
        'references/COMFY_API_V2.md',
        'references/COMFYUI_SECURITY.md',
        'skills/comfyui/SKILL.md',
        'skills/comfyui-discover/SKILL.md',
        'skills/comfyui-workflow/SKILL.md',
        'skills/comfyui-run/SKILL.md',
        'skills/comfyui-assets/SKILL.md',
        'skills/comfyui-cli/SKILL.md',
        'skills/comfyui-mcp/SKILL.md',
        'skills/comfyui-api-v2/SKILL.md',
        'skills/comfyui-troubleshoot/SKILL.md',
        'scripts/comfyui_control.py',
        'scripts/comfyui_workflow.py',
        'scripts/comfyui_cli_bridge.py',
        'scripts/comfy_api_v2.py',
        'scripts/comfy_official_runtime.py',
        'scripts/comfy_workflow_runtime.py',
        'references/HIERARCHICAL_PRODUCTION_PLANNING.md',
        'references/CHARACTER_PROFILE.md',
        'references/PRODUCTION_CAPABILITIES.md',
        'references/PERFORMANCE_BLOCKING.md',
        'references/VISIBLE_DIALOGUE_SYNC.md',
        'references/SHOOTING_SCRIPT.md',
        'references/PRODUCTION_COVERAGE.md',
        'references/MEDIA_QC.md',
        'skills/production-capabilities/SKILL.md',
        'skills/performance-blocking/SKILL.md',
        'skills/shooting-script/SKILL.md',
        'skills/production-coverage/SKILL.md',
        'skills/media-qc/SKILL.md',
        'scripts/character_profiles.py',
        'scripts/dialogue_sync.py',
        'scripts/production_coverage.py',
        'references/MEDIA_REGISTRY.md',
        'references/AUDIO_MASTERING.md',
        'references/VIDEO_FINISHING.md',
        'references/EXECUTABLE_TIMELINE.md',
        'references/FILM_MASTERING.md',
        'references/TRAILER_SYSTEM.md',
        'references/SOCIAL_CAMPAIGN.md',
        'references/RELEASE_DELIVERY.md',
        'references/MLT_EXPORT.md',
        'skills/asset-approval/SKILL.md',
        'skills/audio-master/SKILL.md',
        'skills/video-finishing/SKILL.md',
        'skills/timeline-assembly/SKILL.md',
        'skills/film-master/SKILL.md',
        'skills/mlt-export/SKILL.md',
        'skills/delivery-qc/SKILL.md',
        'skills/trailer-plan/SKILL.md',
        'skills/trailer-assets/SKILL.md',
        'skills/trailer-edit/SKILL.md',
        'skills/trailer-master/SKILL.md',
        'skills/social-campaign/SKILL.md',
        'skills/social-cutdown/SKILL.md',
        'skills/social-reframe/SKILL.md',
        'skills/social-copy/SKILL.md',
        'skills/marketing-art/SKILL.md',
        'skills/campaign-delivery/SKILL.md',
        'skills/release-package/SKILL.md',
        'scripts/media_runtime.py',
        'scripts/media_registry.py',
        'scripts/audio_master.py',
        'scripts/video_finish.py',
        'scripts/render_timeline.py',
        'scripts/social_reframe.py',
        'scripts/delivery_qc.py',
        'scripts/mlt_export.py',
        'scripts/promo_validate.py',
        'scripts/promo_delivery.py',
        'scripts/release_package.py',
        'scripts/film_master.py',
        'scripts/render_promos.py',
        'references/FFMPEG_TOOLKIT.md',
        'references/MLT_TOOLKIT.md',
        'references/IMAGEMAGICK_TOOLKIT.md',
        'references/EDITOR_PROJECT_EXPORT.md',
        'skills/media-toolkit/SKILL.md',
        'skills/ffmpeg/SKILL.md',
        'skills/mlt/SKILL.md',
        'skills/imagemagick/SKILL.md',
        'skills/editor-project-export/SKILL.md',
        'skills/kdenlive-export/SKILL.md',
        'skills/shotcut-export/SKILL.md',
        'scripts/media_toolkit.py',
        'scripts/editor_project_export.py',
        'references/PIPELINE_PROGRESS.md',
        'skills/pipeline-progress/SKILL.md',
        'scripts/pipeline_progress.py',
        'scripts/version_display.py',
        'extensions/story-film-progress/index.ts',
        'extensions/story-film-comfy/index.ts',
        'references/FEATURE_SCALE_PRODUCTION.md',
        'references/SEQUENCE_MANAGEMENT.md',
        'references/CONTEXT_SHARDS.md',
        'references/PRODUCTION_HEALTH.md',
        'references/LONG_RANGE_CONTINUITY.md',
        'references/GENERATION_BUDGETING.md',
        'references/REBOOT_RECOVERY.md',
        'references/PARTIAL_BATCH_RECOVERY.md',
        'references/FEATURE_EDITORIAL_RECONCILIATION.md',
        'references/FILM_COMPLETENESS_AUDIT.md',
        'skills/sequence-production/SKILL.md',
        'skills/context-shards/SKILL.md',
        'skills/production-health/SKILL.md',
        'skills/long-range-continuity/SKILL.md',
        'skills/generation-budget/SKILL.md',
        'skills/reboot-recovery/SKILL.md',
        'skills/batch-recovery/SKILL.md',
        'skills/editorial-reconciliation/SKILL.md',
        'skills/film-completeness/SKILL.md',
        'scripts/feature_common.py',
        'scripts/sequence_manager.py',
        'scripts/context_shards.py',
        'scripts/production_health.py',
        'scripts/long_range_continuity.py',
        'scripts/generation_scheduler.py',
        'scripts/recovery_checkpoint.py',
        'scripts/batch_recovery.py',
        'scripts/editorial_reconcile.py',
        'scripts/completeness_audit.py',
        'scripts/regression_suite.py',
        'scripts/local_smoke.py',
        'scripts/check_docs.py',
        'scripts/build_npx_bundle.py',
        'scripts/install_pi_extension.py',
        'docs/README.md',
        'LICENSE',
        'NOTICE',
        'AUTHORS.md',
        'ATTRIBUTION.md',
        'CONTRIBUTING.md',
        'SECURITY.md',
        'CITATION.cff',
        'skills/story-film-suite/SKILL.md',
    ]
    for rel in required:
        if not (ROOT / rel).is_file():
            errors.append(f'missing standalone capability: {rel}')

    if errors:
        for e in errors:
            print('ERROR', e)
        return 1
    print(f'OK standalone contract: version {version}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
