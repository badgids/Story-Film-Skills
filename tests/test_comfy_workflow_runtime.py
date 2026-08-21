import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('comfy_workflow_runtime', ROOT / 'scripts/comfy_workflow_runtime.py')
workflow = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(workflow)


class FakeClient:
    def __init__(self):
        self.live = {
            'UnetLoaderGGUF': {
                'input': {'required': {'unet_name': [['qwen-image-2512-Q4_K_M.gguf']]}},
                'output': ['MODEL'], 'output_name': ['MODEL'], 'category': 'loaders', 'output_node': False,
            },
            'CLIPTextEncode': {
                'input': {'required': {'clip': ['CLIP'], 'text': ['STRING']}},
                'output': ['CONDITIONING'], 'category': 'conditioning', 'output_node': False,
            },
            'KSampler': {
                'input': {'required': {'model': ['MODEL'], 'positive': ['CONDITIONING'], 'latent_image': ['LATENT']}},
                'output': ['LATENT'], 'category': 'sampling', 'output_node': False,
            },
            'VAEDecode': {
                'input': {'required': {'samples': ['LATENT'], 'vae': ['VAE']}},
                'output': ['IMAGE'], 'category': 'latent', 'output_node': False,
            },
            'SaveImage': {
                'input': {'required': {'images': ['IMAGE'], 'filename_prefix': ['STRING']}},
                'output': [], 'category': 'image', 'output_node': True,
            },
        }

    def workflow_catalog(self, project, source=None):
        return {'workflows': [
            {'source': 'project-workflow', 'name': 'bad-old.json', 'path': '04_generation/comfyui/workflows/bad-old.json'},
            {'source': 'user', 'name': 'Qwen Image GGUF.json', 'path': 'workflows/Qwen Image GGUF.json'},
            {'source': 'core', 'name': 'flux-image', 'title': 'Flux Image'},
        ], 'warnings': []}

    def fetch_workflow_source(self, source, name, module=None):
        return {'1': {'class_type': 'UnetLoaderGGUF', 'inputs': {'unet_name': 'qwen-image-2512-Q4_K_M.gguf'}}}

    def object_info(self, node_class=None):
        if node_class:
            return {node_class: self.live[node_class]} if node_class in self.live else {}
        return self.live

    def validate_workflow(self, wf):
        errors = []
        for node_id, node in wf.items():
            if node.get('class_type') not in self.live:
                errors.append(f"node {node_id}: class {node.get('class_type')!r} is not installed on the live server")
        return {'format': 'api', 'valid': not errors, 'errors': errors, 'warnings': []}

    def probe(self):
        return {'reachable': True, 'server': 'http://127.0.0.1:8188'}


class Tests(unittest.TestCase):
    def project(self, td):
        root = Path(td) / 'film'
        (root / '00_project').mkdir(parents=True)
        (root / '04_generation/comfyui/candidates').mkdir(parents=True)
        (root / '04_generation/comfyui/workflows').mkdir(parents=True)
        (root / '04_generation/comfyui/templates').mkdir(parents=True)
        return root

    def test_catalog_searches_workflow_content_not_mcp_tool_names(self):
        with tempfile.TemporaryDirectory() as td, patch.object(workflow, '_client', return_value=FakeClient()):
            root = self.project(td)
            out = workflow.workflow_catalog(root, 'http://127.0.0.1:8188', query='qwen image 2512 local')
            self.assertEqual(out['count'], 1)
            self.assertEqual(out['workflows'][0]['source'], 'user')
            self.assertIn('live-validate', out['workflows'][0]['runnable_state'])

    def test_node_search_and_path_use_only_live_installed_nodes(self):
        with patch.object(workflow, '_client', return_value=FakeClient()):
            found = workflow.node_search('http://127.0.0.1:8188', query='gguf loader')
            self.assertEqual(found['nodes'][0]['class_type'], 'UnetLoaderGGUF')
            path = workflow.node_path('http://127.0.0.1:8188', from_type='MODEL', to_type='IMAGE', max_depth=4)
            self.assertTrue(any(any(step['class_type'] == 'KSampler' for step in candidate) for candidate in path['paths']))
            with self.assertRaises(workflow.WorkflowRuntimeError):
                workflow.node_info('http://127.0.0.1:8188', class_type='HallucinatedMagicNode')

    def test_promote_rejects_hallucinated_node_and_bad_wiring(self):
        with tempfile.TemporaryDirectory() as td, patch.object(workflow, '_client', return_value=FakeClient()):
            root = self.project(td)
            bad = root / '04_generation/comfyui/candidates/bad.json'
            bad.write_text(json.dumps({'1': {'class_type': 'HallucinatedMagicNode', 'inputs': {}}}))
            with self.assertRaises(workflow.WorkflowRuntimeError):
                workflow.workflow_promote(root, 'http://127.0.0.1:8188', workflow_path='04_generation/comfyui/candidates/bad.json', out_path='04_generation/comfyui/workflows/bad.json')

            wrong = {
                '1': {'class_type': 'UnetLoaderGGUF', 'inputs': {'unet_name': 'qwen-image-2512-Q4_K_M.gguf'}},
                '2': {'class_type': 'SaveImage', 'inputs': {'images': ['1', 0], 'filename_prefix': 'test'}},
            }
            p = root / '04_generation/comfyui/candidates/wrong.json'
            p.write_text(json.dumps(wrong))
            verdict = workflow.workflow_validate(root, 'http://127.0.0.1:8188', workflow_path='04_generation/comfyui/candidates/wrong.json')
            self.assertFalse(verdict['verdict']['valid'])
            self.assertTrue(any('expects IMAGE' in e and 'is MODEL' in e for e in verdict['verdict']['errors']))

    def test_fetch_cannot_bypass_promotion_into_runnable_directory(self):
        with tempfile.TemporaryDirectory() as td, patch.object(workflow, '_client', return_value=FakeClient()):
            root = self.project(td)
            with self.assertRaises(workflow.WorkflowRuntimeError):
                workflow.workflow_fetch(root, 'http://127.0.0.1:8188', source='user', name='Qwen Image GGUF.json', out_path='04_generation/comfyui/workflows/direct.json')
            out = workflow.workflow_fetch(root, 'http://127.0.0.1:8188', source='user', name='Qwen Image GGUF.json')
            self.assertTrue((root / out['path']).is_file())


if __name__ == '__main__':
    unittest.main()
