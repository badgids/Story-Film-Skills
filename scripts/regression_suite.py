#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_FILE = ROOT / 'tests/test_validators.py'


def run(label: str, argv: list[str], timeout: float | None = None) -> int:
    print(f'== {label} ==', flush=True)
    try:
        return subprocess.run(argv, cwd=ROOT, timeout=timeout).returncode
    except subprocess.TimeoutExpired:
        print(f'TIMEOUT: {label}', flush=True)
        return 124


def test_names() -> list[str]:
    tree = ast.parse(TEST_FILE.read_text(encoding='utf-8'))
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == 'Tests':
            return [x.name for x in node.body if isinstance(x, ast.FunctionDef) and x.name.startswith('test_')]
    return []


def partitions(names: list[str]) -> list[tuple[str, list[str]]]:
    groups = {'core': [], 'comfyui-http': [], 'media-docs': [], 'feature-resource': []}
    for name in names:
        if 'comfyui_' in name and 'resource' not in name:
            groups['comfyui-http'].append(name)
        elif any(token in name for token in ('real_', 'media_toolkit', 'editor_project', 'production_document', 'pdf_toolkit', 'motion_graphics', 'edit_assist')):
            groups['media-docs'].append(name)
        elif any(token in name for token in ('feature_', 'sequence', 'context_shard', 'production_health', 'long_range', 'generation_scheduler', 'recovery_', 'batch_recovery', 'completeness', 'resource_', 'npx_bundle', 'documentation_', 'apache_')):
            groups['feature-resource'].append(name)
        else:
            groups['core'].append(name)
    return [(label, values) for label, values in groups.items() if values]


def main() -> int:
    ap = argparse.ArgumentParser(description='Run Story-Film deterministic regression gates and optional local-model smoke cases.')
    ap.add_argument('--local-smoke', action='store_true')
    ap.add_argument('--llm-url')
    ap.add_argument('--llm-model')
    args = ap.parse_args()
    failures: list[str] = []

    gates = [
        ('skill validation', [sys.executable, str(ROOT / 'scripts/validate_skills.py')]),
        ('standalone validation', [sys.executable, str(ROOT / 'scripts/validate_standalone.py')]),
        ('documentation links', [sys.executable, str(ROOT / 'scripts/check_docs.py')]),
        ('example prompt catalog', [sys.executable, str(ROOT / 'scripts/validate_examples.py')]),
        ('managed official Comfy runtime', [sys.executable, '-m', 'unittest', 'tests.test_comfy_official_runtime']),
        ('Comfy workflow schema runtime', [sys.executable, '-m', 'unittest', 'tests.test_comfy_workflow_runtime']),
        ('bounded Comfy workflow pipeline', [sys.executable, '-m', 'unittest', 'tests.test_comfy_workflow_pipeline']),
        ('character profile contracts', [sys.executable, '-m', 'unittest', 'tests.test_character_profiles']),
        ('visible dialogue sync contracts', [sys.executable, '-m', 'unittest', 'tests.test_dialogue_sync']),
        ('v0.0.28 production integrity', [sys.executable, '-m', 'unittest', 'tests.test_v0028_production_integrity']),
        ('v0.0.31 workflow selection', [sys.executable, '-m', 'unittest', 'tests.test_v0031_workflow_selection']),
        ('v0.0.32 preflight and LLM lifecycle', [sys.executable, '-m', 'unittest', 'tests.test_v0032_preflight_lifecycle_workflows']),
        ('post-v0.0.32 ComfyUI style exemption', [sys.executable, '-m', 'unittest', 'tests.test_v0033_comfyui_style_exemption']),
        ('static eval definitions', [sys.executable, str(ROOT / 'scripts/run_evals.py'), '--definitions-only']),
    ]
    for label, cmd in gates:
        if run(label, cmd):
            failures.append(label)

    names = test_names()
    if not names:
        failures.append('test discovery')
    else:
        for index, name in enumerate(names, 1):
            cmd = [sys.executable, '-m', 'unittest', f'tests.test_validators.Tests.{name}']
            label = f'deterministic test {index}/{len(names)}: {name}'
            if run(label, cmd, timeout=300):
                failures.append(label)

    if args.local_smoke:
        cmd = [sys.executable, str(ROOT / 'scripts/local_smoke.py')]
        if args.llm_url:
            cmd += ['--url', args.llm_url]
        if args.llm_model:
            cmd += ['--model', args.llm_model]
        if run('local-model smoke cases', cmd):
            failures.append('local-model smoke cases')

    if failures:
        print('FAILED:', ', '.join(failures))
        return 1
    print(f'PASS: regression gates completed; {len(names)} deterministic tests')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
