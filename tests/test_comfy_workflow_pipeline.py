import importlib.util
import json
import sys
import types
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
if SCRIPTS.is_dir() and str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

# The real repository provides these modules. Lightweight fallbacks keep this
# test file runnable in an isolated patch-verification harness too.
def ensure_stub(name):
    if importlib.util.find_spec(name) is not None:
        return
    mod = types.ModuleType(name)
    if name == 'comfyui_control':
        class Client:
            def __init__(self, *args, **kwargs): pass
            def object_info(self): return {}
        mod.Client = Client
        mod.resolve_url = lambda value=None: value or 'http://127.0.0.1:8188'
    elif name == 'comfy_workflow_runtime':
        mod._workflow_nodes = lambda wf: {str(k): v for k, v in wf.items() if isinstance(v, dict) and isinstance(v.get('class_type'), str)}
        mod.workflow_catalog = lambda *a, **k: {'workflows': [], 'warnings': []}
        mod.workflow_fetch = lambda *a, **k: {}
        mod.workflow_validate = lambda *a, **k: {'verdict': {'valid': True, 'errors': []}}
    elif name == 'model_inventory':
        mod.scan = lambda *a, **k: {'folders': {}, 'node_choices': []}
        mod.inventory_summary = lambda obj: {'resource_count': 0}
        mod.json_path = lambda root: Path(root) / '00_project/comfyui_model_inventory.json'
    elif name == 'comfyui_batch':
        mod.validate = lambda *a, **k: []
    elif name == 'resource_handoff':
        mod.arm = lambda *a, **k: {'phase': 'waiting-for-agent-end', 'message': 'armed'}
    sys.modules[name] = mod

for _name in ('comfyui_batch', 'comfyui_control', 'comfy_workflow_runtime', 'model_inventory', 'resource_handoff'):
    ensure_stub(_name)

SPEC = importlib.util.spec_from_file_location('comfy_workflow_pipeline', SCRIPTS / 'comfy_workflow_pipeline.py')
pipeline = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(pipeline)


class FakeClient:
    def __init__(self, *args, **kwargs):
        pass

    def object_info(self):
        return {
            'UnetLoaderGGUF': {
                'input': {'required': {'unet_name': [['qwen-image-2512-Q4_K_M.gguf']]}},
                'output': ['MODEL'],
            },
            'PromptNode': {
                'input': {'required': {'text': ['STRING']}},
                'output': ['CONDITIONING'],
            },
            'OutputNode': {
                'input': {'required': {'filename_prefix': ['STRING']}},
                'output': [],
                'output_node': True,
            },
        }

    def validate_workflow(self, workflow):
        return {'format': 'api', 'valid': True, 'errors': [], 'warnings': []}


class Tests(unittest.TestCase):
    def project(self, td):
        root = Path(td) / 'film'
        (root / '00_project').mkdir(parents=True)
        (root / '04_generation/comfyui/workflows').mkdir(parents=True)
        (root / '04_generation/comfyui/templates').mkdir(parents=True)
        (root / '04_generation/comfyui/candidates').mkdir(parents=True)
        records = [
            {'image_id': 'IMG-001', 'shot_id': 'SHOT-001', 'subject_description': 'watch on bench', 'lighting': 'warm lamp', 'generation_instructions': {'avoid': 'blur'}},
            {'shot_id': 'SHOT-002', 'subject_description': 'clockmaker at bench', 'continuity_constraints': 'same wardrobe'},
        ]
        (root / '04_generation/image_briefs.jsonl').write_text('\n'.join(json.dumps(x) for x in records) + '\n', encoding='utf-8')
        prompt_dir = root / '04_generation/prompts/qwen-image-2512'
        prompt_dir.mkdir(parents=True)
        (prompt_dir / 'IMG-001.md').write_text(
            'SOURCE_ID: IMG-001\nMODEL: qwen-image-2512\nPROMPT:\nApproved production prompt for the watch.\nCONSTRAINTS:\n- preserve canon\n',
            encoding='utf-8',
        )
        return root

    def test_prepare_uses_extension_workflow_catalog(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.project(td)
            catalog = {
                'ok': True,
                'workflows': [{'source': 'built-in', 'name': 'image_qwen_Image_2512.json', 'path': 'comfyui_workflows/image/Qwen-Image-2512/image_qwen_Image_2512.json'}],
                'warnings': [],
            }
            fetched = root / '04_generation/comfyui/recovery/sources/01-user-User-Qwen-image_qwen_Image_2512.json'
            def fake_fetch(project, url, *, source, name, module='', out_path=''):
                self.assertEqual(source, 'built-in')
                self.assertEqual(name, 'comfyui_workflows/image/Qwen-Image-2512/image_qwen_Image_2512.json')
                path = root / out_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps({'1': {'class_type': 'PromptNode', 'inputs': {'text': 'source'}}}), encoding='utf-8')
                return {'path': out_path, 'format': 'api'}

            with patch.object(pipeline.comfyui_control, 'Client', FakeClient), \
                 patch.object(pipeline.model_inventory, 'scan', return_value={'folders': {}, 'node_choices': []}), \
                 patch.object(pipeline.model_inventory, 'inventory_summary', return_value={'resource_count': 1}), \
                 patch.object(pipeline.comfy_workflow_runtime, 'workflow_catalog', return_value=catalog), \
                 patch.object(pipeline.comfy_workflow_runtime, 'workflow_fetch', side_effect=fake_fetch), \
                 patch.object(pipeline.comfy_workflow_runtime, 'workflow_validate', return_value={'verdict': {'valid': True, 'errors': []}}):
                with patch.object(pipeline.model_inventory, 'json_path', return_value=root / '00_project/comfyui_model_inventory.json'):
                    (root / '00_project/comfyui_model_inventory.json').write_text('{}\n')
                    out = pipeline.prepare(root, 'http://127.0.0.1:8188', query='qwen image 2512 gguf')
            self.assertEqual(out['status'], 'llm-candidate-required')
            self.assertTrue((root / out['contract']).is_file())
            self.assertTrue((root / out['live_node_schemas']).is_file())
            self.assertEqual(out['source_candidates'][0]['name'], 'image_qwen_Image_2512.json')

    def test_prepare_does_not_scan_project_or_user_workflow_sources(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.project(td)
            rows = [{"source": "built-in", "name": "image_qwen_Image_2512.json", "path": "comfyui_workflows/image/Qwen-Image-2512/image_qwen_Image_2512.json"}]
            fetched_names = []

            def fake_validate(project, url, *, workflow_path):
                return {"verdict": {"valid": False, "errors": ["stale project graph"]}}

            def fake_fetch(project, url, *, source, name, module='', out_path=''):
                fetched_names.append((source, name))
                path = root / out_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps({"1": {"class_type": "PromptNode", "inputs": {"text": "source"}}}), encoding='utf-8')
                return {"path": out_path, "format": "api"}

            with patch.object(pipeline.comfyui_control, 'Client', FakeClient), \
                 patch.object(pipeline.model_inventory, 'scan', return_value={'folders': {}, 'node_choices': []}), \
                 patch.object(pipeline.model_inventory, 'inventory_summary', return_value={'resource_count': 1}), \
                 patch.object(pipeline.comfy_workflow_runtime, 'workflow_catalog', return_value={'workflows': rows, 'warnings': []}), \
                 patch.object(pipeline.comfy_workflow_runtime, 'workflow_fetch', side_effect=fake_fetch), \
                 patch.object(pipeline.comfy_workflow_runtime, 'workflow_validate', side_effect=fake_validate), \
                 patch.object(pipeline.model_inventory, 'json_path', return_value=root / '00_project/comfyui_model_inventory.json'):
                (root / '00_project/comfyui_model_inventory.json').write_text('{}\n')
                out = pipeline.prepare(root, 'http://127.0.0.1:8188', query='qwen image 2512 gguf', source_limit=2)

            self.assertIn(('built-in', 'comfyui_workflows/image/Qwen-Image-2512/image_qwen_Image_2512.json'), fetched_names)
            self.assertEqual(out['source_counts'], {'built-in': 1})

    def test_finalize_accepts_one_llm_graph_then_script_fans_out_and_builds_batch(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.project(td)
            contract = {
                'schema_version': 1,
                'media_type': 'image',
                'records_path': '04_generation/image_briefs.jsonl',
                'candidate_path': pipeline.DEFAULT_CANDIDATE_REL,
                'canonical_path': pipeline.DEFAULT_CANONICAL_REL,
                'offline_batch_path': pipeline.DEFAULT_BATCH_REL,
                'direct_finalizable_sources': [],
            }
            path = root / pipeline.CONTRACT_REL
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(contract), encoding='utf-8')
            old = root / '04_generation/comfyui/workflows/SHOT-001.json'
            old.write_text(json.dumps({'1': {'class_type': 'OldBadNode', 'inputs': {}}}), encoding='utf-8')
            candidate = {
                '1': {'class_type': 'PromptNode', 'inputs': {'text': pipeline.PROMPT_MARKER}},
                '2': {'class_type': 'PromptNode', 'inputs': {'text': pipeline.NEGATIVE_MARKER}},
                '3': {'class_type': 'OutputNode', 'inputs': {'filename_prefix': pipeline.FILENAME_MARKER}},
            }
            with patch.object(pipeline.comfyui_control, 'Client', FakeClient), \
                 patch.object(pipeline.comfy_workflow_runtime, 'workflow_validate', return_value={'verdict': {'valid': True, 'errors': []}}), \
                 patch.object(pipeline.comfyui_batch, 'validate', return_value=[]), \
                 patch.object(pipeline.resource_handoff, 'arm', return_value={'phase': 'waiting-for-agent-end', 'message': 'armed', 'runner_pid': 123}) as arm:
                out = pipeline.finalize(root, 'http://127.0.0.1:8188', workflow=candidate)
                arm.assert_called_once()
            self.assertEqual(out['workflow_count'], 2)
            self.assertTrue(out['live_validated'])
            self.assertEqual(out['status'], 'waiting-for-agent-end')
            self.assertTrue(out['resource_handoff']['armed'])
            one = json.loads((root / '04_generation/comfyui/workflows/SHOT-001.json').read_text())
            self.assertEqual(one['1']['inputs']['text'], 'Approved production prompt for the watch.')
            self.assertEqual(out['prompt_sources']['SHOT-001'], '04_generation/prompts/qwen-image-2512/IMG-001.md')
            self.assertEqual(one['2']['inputs']['text'], 'blur')
            self.assertEqual(one['3']['inputs']['filename_prefix'], 'story-film/SHOT-001')
            batch = json.loads((root / '04_generation/comfyui/offline_batch.json').read_text())
            self.assertEqual(len(batch['jobs']), 2)
            self.assertTrue(out['quarantine'])
            self.assertTrue((root / out['quarantine'] / 'SHOT-001.json').is_file())

    def test_finalize_rejects_invalid_candidate_before_touching_runnable_workflows(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.project(td)
            contract = {
                'schema_version': 1,
                'media_type': 'image',
                'records_path': '04_generation/image_briefs.jsonl',
                'candidate_path': pipeline.DEFAULT_CANDIDATE_REL,
                'canonical_path': pipeline.DEFAULT_CANONICAL_REL,
                'offline_batch_path': pipeline.DEFAULT_BATCH_REL,
                'direct_finalizable_sources': [],
            }
            path = root / pipeline.CONTRACT_REL
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(contract), encoding='utf-8')
            existing = root / '04_generation/comfyui/workflows/SHOT-001.json'
            existing.write_text('{"old": true}\n', encoding='utf-8')
            candidate = {'1': {'class_type': 'HallucinatedNode', 'inputs': {'text': pipeline.PROMPT_MARKER}}}
            with patch.object(pipeline.comfy_workflow_runtime, 'workflow_validate', return_value={'verdict': {'valid': False, 'errors': ["class 'HallucinatedNode' is not installed"]}}):
                with self.assertRaises(pipeline.WorkflowPipelineError):
                    pipeline.finalize(root, 'http://127.0.0.1:8188', workflow=candidate)
            self.assertEqual(existing.read_text(encoding='utf-8'), '{"old": true}\n')

    def test_comfyui_userdata_fetch_is_disabled(self):
        path = ROOT / 'scripts/comfyui_control.py'
        if not path.is_file():
            self.skipTest('comfyui_control.py not present in isolated patch harness')
        source = path.read_text(encoding='utf-8')
        self.assertIn('ComfyUI userdata workflow fetching is disabled', source)


    def test_existing_offline_batch_is_authoritative_record_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.project(td)
            (root / '04_generation/image_briefs.jsonl').unlink()
            batch = {
                'schema_version': 1, 'batch_id': 'BATCH-007', 'status': 'prepared', 'sequential': True, 'uploads': [],
                'jobs': [
                    {'job_id': 'JOB-001', 'source_ids': ['IMG-001', 'SHOT-001'], 'workflow': '04_generation/comfyui/workflows/SHOT-001.json', 'patches': [], 'blocked_by': [], 'output_dir': '04_generation/comfyui/outputs/SHOT-001', 'timeout_s': 900, 'max_transient_retries': 2},
                    {'job_id': 'JOB-002', 'source_ids': ['SHOT-002'], 'workflow': '04_generation/comfyui/workflows/SHOT-002.json', 'patches': [], 'blocked_by': ['JOB-001'], 'output_dir': '04_generation/comfyui/outputs/SHOT-002', 'timeout_s': 1200, 'max_transient_retries': 1},
                ],
            }
            (root / pipeline.DEFAULT_BATCH_REL).write_text(json.dumps(batch), encoding='utf-8')
            rows, origin = pipeline._discover_records(root, 'image', '')
            self.assertEqual(origin, pipeline.DEFAULT_BATCH_REL)
            self.assertEqual([r['shot_id'] for r in rows], ['SHOT-001', 'SHOT-002'])
            self.assertEqual(rows[0]['source_ids'], ['IMG-001', 'SHOT-001'])
            self.assertEqual(pipeline._record_source_ids(rows[0], 1), ['IMG-001', 'SHOT-001'])
            prompt, prompt_path = pipeline._prepared_prompt(root, rows[0], 1, 'qwen image 2512')
            self.assertEqual(prompt, 'Approved production prompt for the watch.')
            self.assertEqual(prompt_path, '04_generation/prompts/qwen-image-2512/IMG-001.md')
            self.assertEqual(rows[1]['_story_film_job']['blocked_by'], ['JOB-001'])

    def test_pi_extension_uses_bounded_prepare_finalize_contract(self):
        extension = ROOT / 'extensions/story-film-comfy-workflow/index.ts'
        if not extension.is_file():
            self.skipTest('repository extension file not present in prototype harness')
        text = extension.read_text(encoding='utf-8')
        self.assertIn('Type.Literal("prepare")', text)
        self.assertIn('Type.Literal("finalize")', text)
        self.assertIn('story_comfy_workflow', text)
        self.assertIn('exactly ONE canonical', text)
        self.assertIn('offline_batch.json', text)


if __name__ == '__main__':
    unittest.main()
