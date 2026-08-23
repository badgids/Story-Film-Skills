# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_evals
from style_policy import is_comfyui_workflow_json


EM_DASH = chr(0x2014)


class Tests(unittest.TestCase):
    def write_json(self, path: Path, obj: object) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(obj, ensure_ascii=False)
        path.write_text(text, encoding='utf-8')
        return text

    def test_known_story_film_workflow_paths_are_exempt(self):
        samples = [
            Path('comfyui_workflows/video/model/workflow.json'),
            Path('skills/story-film-suite/bundle/comfyui_workflows/image/model/workflow.json'),
            Path('04_generation/comfyui/default_workflows/video/model/workflow.json'),
            Path('04_generation/comfyui/workflows/user/workflow.json'),
            Path('04_generation/comfyui/templates/selected/video/workflow.json'),
        ]
        text = json.dumps({'title': f'Workflow {EM_DASH} preserved'}, ensure_ascii=False)
        for path in samples:
            with self.subTest(path=path):
                self.assertTrue(is_comfyui_workflow_json(path, text))

    def test_comfyui_structure_is_detected_outside_known_paths(self):
        ui_graph = {
            'nodes': [{'id': 1, 'type': 'MarkdownNote'}],
            'links': [],
            'version': 0.4,
        }
        api_graph = {
            '1': {
                'class_type': 'KSampler',
                'inputs': {'seed': 42},
            },
        }
        ui_text = json.dumps(ui_graph)
        api_text = json.dumps(api_graph)
        self.assertTrue(is_comfyui_workflow_json(Path('vendor/custom.json'), ui_text))
        self.assertTrue(is_comfyui_workflow_json(Path('external/prompt.json'), api_text))
        self.assertFalse(
            is_comfyui_workflow_json(
                Path('00_project/resource_policy.json'),
                json.dumps({'nodes': 'not-a-list', 'links': []}),
            )
        )

    def test_check_style_ignores_only_workflow_em_dashes(self):
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            workflow = work / 'comfyui_workflows/video/model/workflow.json'
            self.write_json(workflow, {'title': f'Workflow {EM_DASH} preserved'})

            proc = subprocess.run(
                [sys.executable, str(ROOT / 'scripts/check_style.py'), str(work)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout)

            ordinary = work / '00_project/resource_policy.json'
            self.write_json(ordinary, {'note': f'Ordinary prose {EM_DASH} rejected'})
            proc = subprocess.run(
                [sys.executable, str(ROOT / 'scripts/check_style.py'), str(work)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            self.assertIn('em dash', proc.stdout)

    def test_eval_scoring_uses_same_workflow_exemption(self):
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            workflow = work / '04_generation/comfyui/templates/selected/video/workflow.json'
            self.write_json(workflow, {'title': f'Workflow {EM_DASH} preserved'})
            case = {'id': 'workflow-em-dash-exemption', 'suite': 'unit'}

            result = run_evals.score_case(case, work)
            self.assertTrue(result.passed, result.failures)

            ordinary = work / 'notes.md'
            ordinary.write_text(f'Ordinary prose {EM_DASH} rejected\n', encoding='utf-8')
            result = run_evals.score_case(case, work)
            self.assertFalse(result.passed)
            self.assertTrue(any('notes.md' in failure for failure in result.failures))

    def test_other_style_warnings_still_apply_inside_workflows(self):
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            workflow = work / 'comfyui_workflows/video/model/workflow.json'
            self.write_json(
                workflow,
                {'note': f'same as before {EM_DASH} workflow punctuation is allowed'},
            )
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / 'scripts/check_style.py'),
                    str(work),
                    '--strict-warnings',
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            self.assertNotIn('ERROR', proc.stdout)
            self.assertIn('same as before shortcut', proc.stdout)


if __name__ == '__main__':
    unittest.main()
