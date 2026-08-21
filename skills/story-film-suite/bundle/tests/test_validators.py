import json
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import threading
import math
import wave
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import comfyui_control
import comfyui_workflow
import comfy_api_v2
import comfyui_cli_bridge
import audio_master
import media_registry
import render_timeline
import social_reframe
import promo_validate
import release_package
import mlt_export
import delivery_qc
import media_toolkit
import editor_project_export
import claim_ledger
import campaign_content
import production_documents
import pdf_toolkit
import edit_assist
import motion_graphics
import remotion_adapter
import pipeline_progress
import version_display
import model_preferences
import model_inventory
import work_units
import decision_map
import document_companions
import comfyui_batch
import resource_handoff
import llm_runtime
import sequence_manager
import context_shards
import production_health
import long_range_continuity
import generation_scheduler
import recovery_checkpoint
import batch_recovery
import editorial_reconcile
import completeness_audit
import validate_skills
import screenplay_consistency


class FakeComfyHandler(BaseHTTPRequestHandler):
    prompt_id = '11111111-1111-1111-1111-111111111111'
    free_requests = []
    upload_requests = []

    def log_message(self, fmt, *args):
        return

    def _json(self, obj, status=200):
        payload = json.dumps(obj).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path == '/system_stats':
            return self._json({'system': {'comfyui_version': 'test'}, 'devices': [{'name': 'Fake GPU', 'vram_total': 24 * 1024**3, 'vram_free': 20 * 1024**3}]})
        if path == '/features':
            return self._json({'test_feature': True})
        if path == '/prompt':
            return self._json({'exec_info': {'queue_remaining': 0}})
        if path == '/object_info':
            return self._json({
                'TestNode': {
                    'input': {'required': {'choice': [['a', 'b']], 'value': ['INT']}},
                    'output': ['TEST'], 'output_node': False, 'category': 'test'
                },
                'LoadTest': {
                    'input': {'required': {'image': [['uploaded.png']]}},
                    'output': ['TEST'], 'output_node': False, 'category': 'test'
                },
                'SaveTest': {
                    'input': {'required': {'data': ['TEST']}},
                    'output': [], 'output_node': True, 'category': 'test'
                },
                'CustomModelLoader': {
                    'input': {'required': {'model_name': [['custom-node-model.safetensors']]}},
                    'output': ['MODEL'], 'output_node': False, 'category': 'loaders'
                },
            })
        if path == '/models':
            return self._json(['checkpoints', 'diffusion_models', 'unet', 'vae', 'text_encoders', 'loras', 'audio_encoders', 'upscale_models', 'frame_interpolation'])
        model_folders = {
            '/models/checkpoints': ['model.safetensors'],
            '/models/diffusion_models': ['h3-video.safetensors', 'ltx-video.safetensors', 'qwen-image.safetensors'],
            '/models/unet': ['qwen-image-2512-Q4_K_M.gguf'],
            '/models/vae': ['h3-vae.safetensors', 'ltx-vae.safetensors', 'image-vae.safetensors'],
            '/models/text_encoders': ['clip-l.safetensors', 't5xxl.safetensors'],
            '/models/loras': ['camera-motion.safetensors', 'film-look.safetensors'],
            '/models/audio_encoders': ['audio-encoder.safetensors'],
            '/models/upscale_models': ['4x-upscaler.pth'],
            '/models/frame_interpolation': ['rife.pth'],
        }
        if path in model_folders:
            return self._json(model_folders[path])
        if path.startswith('/history/'):
            pid = path.rsplit('/', 1)[-1]
            return self._json({pid: {
                'status': {'completed': True, 'status_str': 'success'},
                'outputs': {
                    '2': {'images': [{'filename': 'frame.png', 'subfolder': '', 'type': 'output'}]},
                    '3': {'3d': [{'filename': 'mesh.glb', 'subfolder': '', 'type': 'output'}], 'text': ['done']},
                },
            }})
        if path == '/queue':
            return self._json({'queue_running': [], 'queue_pending': []})
        if path == '/view':
            payload = b'fake-output-bytes'
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if path == '/api/v2/health':
            return self._json({'ok': True})
        if path.startswith('/api/v2/jobs/'):
            jid = path.split('/')[4]
            return self._json({'id': jid, 'status': 'completed', 'outputs': []})
        return self._json({'error': 'not found'}, 404)

    def do_POST(self):
        path = self.path.split('?', 1)[0]
        length = int(self.headers.get('Content-Length', '0'))
        raw = self.rfile.read(length) if length else b''
        if path == '/prompt':
            body = json.loads(raw.decode('utf-8'))
            if 'prompt' not in body:
                return self._json({'error': 'no prompt'}, 400)
            return self._json({'prompt_id': self.prompt_id, 'number': 1, 'node_errors': {}})
        if path == f'/api/jobs/{self.prompt_id}/cancel':
            return self._json({'cancelled': True})
        if path == '/upload/image':
            type(self).upload_requests.append(len(raw))
            return self._json({'name': 'uploaded.png', 'subfolder': '', 'type': 'input'})
        if path == '/upload/mask':
            return self._json({'name': 'uploaded-mask.png', 'subfolder': '', 'type': 'input'})
        if path == '/free':
            body = json.loads(raw.decode('utf-8')) if raw else {}
            type(self).free_requests.append(body)
            return self._json({'ok': True})
        if path == '/api/v2/jobs':
            return self._json({'id': self.prompt_id, 'status': 'pending'}, 201)
        if path == f'/api/v2/jobs/{self.prompt_id}/cancel':
            return self._json({'id': self.prompt_id, 'status': 'cancelled'})
        return self._json({'ok': True})


class FakeComfyServer:
    def __enter__(self):
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), FakeComfyHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.server.server_address
        self.url = f'http://{host}:{port}'
        return self

    def __exit__(self, exc_type, exc, tb):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


class Tests(unittest.TestCase):
    def test_skill_validator(self):
        subprocess.run([sys.executable, str(ROOT / 'scripts/validate_skills.py')], check=True)

    def test_standalone_validator(self):
        subprocess.run([sys.executable, str(ROOT / 'scripts/validate_standalone.py')], check=True)

    def test_version_format_and_next(self):
        version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
        self.assertEqual(version, '00.00.26')
        self.assertEqual(version_display.display_version(version), 'v0.0.26')
        self.assertEqual(version_display.display_version('01.10.23'), 'v1.10.23')
        self.assertEqual(version_display.display_version('20.01.03'), 'v20.1.3')
        subprocess.run([sys.executable, str(ROOT / 'scripts/bump_version.py'), '--check-next', '00.00.27'], check=True)

    def test_project_init_and_validate(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project), '--title', 'Test'], check=True)
            subprocess.run([sys.executable, str(ROOT / 'scripts/validate_story_project.py'), str(project)], check=True)
            state = json.loads((project / '00_project/state.json').read_text())
            self.assertEqual(state['project_title'], 'Test')
            self.assertTrue((project / '03_preproduction/previz').is_dir())
            self.assertTrue((project / '03_preproduction/references/music').is_dir())
            self.assertTrue((project / '04_generation/comfyui/workflows').is_dir())
            self.assertTrue((project / '04_generation/comfyui/runs').is_dir())
            self.assertTrue((project / '00_project/reviews').is_dir())
            self.assertTrue((project / '03_preproduction/storyboards/sequence_boards').is_dir())
            story_state = json.loads((project / '01_story/story_state.json').read_text())
            self.assertEqual(story_state['schema_version'], 1)
            selections = json.loads((project / '04_generation/selections.json').read_text())
            self.assertEqual(selections['shots'], {})
            capabilities = json.loads((project / '03_preproduction/production_capabilities.json').read_text())
            self.assertEqual(capabilities['schema_version'], 1)
            self.assertEqual(capabilities['actions'], {})
            self.assertTrue((project / '05_post/masters').is_dir())
            self.assertTrue((project / '06_release/trailers').is_dir())
            self.assertTrue((project / '06_release/social/masters').is_dir())
            self.assertTrue((project / '05_post/editorial/kdenlive').is_dir())
            self.assertTrue((project / '05_post/editorial/shotcut').is_dir())
            self.assertTrue((project / '05_post/tool_runs').is_dir())
            self.assertTrue((project / '01_story/research').is_dir())
            self.assertTrue((project / '03_preproduction/documents').is_dir())
            self.assertTrue((project / '05_post/edit_assist').is_dir())
            self.assertTrue((project / '05_post/graphics').is_dir())
            self.assertTrue((project / '05_post/programmatic/remotion').is_dir())
            self.assertTrue((project / '06_release/documents').is_dir())
            self.assertTrue((project / '01_story/research/claims.jsonl').is_file())
            self.assertTrue((project / '06_release/social/content_lineage.jsonl').is_file())
            docs = json.loads((project / '00_project/document_manifest.json').read_text())
            self.assertEqual(docs['documents'], [])
            tool_caps = json.loads((project / '00_project/tool_capabilities.json').read_text())
            self.assertEqual(tool_caps['status'], 'not-discovered')
            approvals = json.loads((project / '00_project/media_approvals.json').read_text())
            self.assertEqual(approvals['groups'], {})
            self.assertTrue((project / '00_project/media_registry.jsonl').is_file())
            delivery = json.loads((project / '06_release/delivery_specs.json').read_text())
            self.assertEqual(delivery['deliverables'], [])
            progress = json.loads((project / '00_project/pipeline_progress.json').read_text())
            self.assertEqual(progress['owner'], 'story-film-skills')
            self.assertEqual(progress['status'], 'inactive')
            self.assertTrue((project / '00_project/progress_events.jsonl').is_file())
            self.assertTrue((project / '00_project/HANDOFF.md').is_file())
            self.assertTrue((project / '00_project/work_units.json').is_file())
            self.assertTrue((project / '00_project/work_units.md').is_file())
            self.assertTrue((project / '00_project/decision_map.json').is_file())
            self.assertTrue((project / '00_project/decision_map.md').is_file())
            self.assertTrue((project / '00_project/resource_policy.json').is_file())
            model_prefs = json.loads((project / '00_project/model_preferences.json').read_text())
            self.assertEqual(model_prefs['schema_version'], 2)
            self.assertEqual(model_prefs['processes']['video_generation']['default_adapter'], 'minimax-h3')
            self.assertEqual(model_prefs['processes']['video_generation']['selected_adapter'], 'minimax-h3')
            self.assertEqual(model_prefs['processes']['video_generation']['selection_source'], 'default')
            self.assertFalse(model_prefs['processes']['video_generation']['allow_agent_substitution'])
            self.assertIsNone(model_prefs['processes']['image_generation']['selected_adapter'])
            self.assertTrue((project / '00_project/resource_handoff.json').is_file())
            self.assertTrue((project / '00_project/resource_events.jsonl').is_file())
            self.assertTrue((project / '00_project/wizards').is_dir())
            self.assertTrue((project / '04_generation/comfyui/offline').is_dir())
            self.assertTrue((project / '00_project/shards').is_dir())
            self.assertTrue((project / '00_project/recovery').is_dir())
            self.assertTrue((project / '03_preproduction/continuity').is_dir())
            self.assertTrue((project / '00_project/sequence_manifest.json').is_file())
            self.assertTrue((project / '00_project/sequence_manifest.md').is_file())
            self.assertTrue((project / '04_generation/generation_resources.json').is_file())


    def test_pipeline_progress_checkpoint_block_resume_and_reset(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project), '--title', 'Progress Test'], check=True)
            subprocess.run([sys.executable, str(ROOT / 'scripts/pipeline_progress.py'), 'init', str(project), '--playbook', 'short-film'], check=True)
            value = json.loads((project / '00_project/pipeline_progress.json').read_text())
            self.assertEqual(value['pipeline_id'], 'short-film')
            self.assertEqual(len(value['stages']), 18)
            leaves = pipeline_progress.flatten_leaves(value)
            self.assertGreaterEqual(len(leaves), 18)
            first_id = value['cursor']['target_id']
            subprocess.run([sys.executable, str(ROOT / 'scripts/pipeline_progress.py'), 'checkpoint', str(project), '--status', 'completed', '--last-action', 'Finished first item', '--file', '00_project/brief.md'], check=True)
            value = json.loads((project / '00_project/pipeline_progress.json').read_text())
            second_id = value['cursor']['target_id']
            self.assertNotEqual(first_id, second_id)
            subprocess.run([sys.executable, str(ROOT / 'scripts/pipeline_progress.py'), 'checkpoint', str(project), '--status', 'blocked', '--blocker', 'Validation failed', '--next', 'Repair current item'], check=True)
            blocked = json.loads((project / '00_project/pipeline_progress.json').read_text())
            self.assertEqual(blocked['status'], 'blocked')
            self.assertEqual(blocked['cursor']['target_id'], second_id)
            subprocess.run([sys.executable, str(ROOT / 'scripts/pipeline_progress.py'), 'resume', str(project)], check=True)
            resumed = json.loads((project / '00_project/pipeline_progress.json').read_text())
            self.assertEqual(resumed['status'], 'active')
            self.assertEqual(resumed['cursor']['target_id'], second_id)
            subprocess.run([sys.executable, str(ROOT / 'scripts/pipeline_progress.py'), 'checkpoint', str(project), '--status', 'completed', '--last-action', 'Repaired and validated'], check=True)
            subprocess.run([sys.executable, str(ROOT / 'scripts/pipeline_progress.py'), 'reset', str(project), first_id, '--note', 'Selective retry'], check=True)
            reset = json.loads((project / '00_project/pipeline_progress.json').read_text())
            self.assertEqual(reset['cursor']['target_id'], first_id)
            self.assertIn('Selective retry', (project / '00_project/progress_events.jsonl').read_text())
            handoff = (project / '00_project/HANDOFF.md').read_text()
            self.assertIn(first_id, handoff)
            subprocess.run([sys.executable, str(ROOT / 'scripts/validate_story_project.py'), str(project)], check=True)

    def test_pipeline_progress_all_playbooks_compile(self):
        playbooks = sorted((ROOT / 'skills/story-film/playbooks').glob('*.md'))
        self.assertEqual(len(playbooks), 36)
        for path in playbooks:
            value = pipeline_progress.compile_pipeline(path, max_depth=3)
            pipeline_progress.validate_progress(value)
            self.assertEqual(value['source_playbook'], str(path.relative_to(ROOT)))
            self.assertTrue(value['stages'], path.name)
            self.assertTrue(pipeline_progress.flatten_leaves(value), path.name)

    def test_pi_native_package_manifest_and_project_local_docs(self):
        package = json.loads((ROOT / 'package.json').read_text(encoding='utf-8'))
        self.assertIn('pi-package', package.get('keywords', []))
        self.assertEqual(package.get('peerDependencies', {}).get('@earendil-works/pi-tui'), '*')
        manifest = package.get('pi', {})
        self.assertIn('./extensions/story-film-progress/index.ts', manifest.get('extensions', []))
        self.assertIn('./extensions/story-film-comfy-workflow/index.ts', manifest.get('extensions', []))
        skills = manifest.get('skills', [])
        self.assertIn('./skills/*/SKILL.md', skills)
        self.assertIn('!./skills/story-film-suite/SKILL.md', skills)
        install_doc = (ROOT / 'docs/getting-started/install.md').read_text(encoding='utf-8')
        pi_doc = (ROOT / 'docs/getting-started/pi-install.md').read_text(encoding='utf-8')
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        for token in ['pi install -l', 'pi -e', '.pi/settings.json']:
            self.assertIn(token, pi_doc)
        self.assertIn('pi install', install_doc)
        self.assertIn('Project-only Pi install', readme)

    def test_pi_progress_extension_contract(self):
        src = (ROOT / 'extensions/story-film-progress/index.ts').read_text(encoding='utf-8')
        for token in ['pipeline_progress.json', 'resource_handoff.json', 'story-todo', 'story-resource', 'agent_end', 'setInterval', 'setWidget', 'ctrl+alt+home', 'ctrl+alt+end', '/story-todo help', 'following current', 'COLLAPSED_ROWS = 3', 'EXPANDED_ROWS = 10', 'systemPromptAppend', 'tool_call', 'Do not work ahead', 'genericTodoBlockReason', 'at most three Story-Film mirror items', 'comfyModelFilesystemScanBlockReason', 'comfyWorkflowBypassBlockReason', 'workflow-catalog', 'extra_model_paths.yaml', 'model_inventory.py scan', 'rawRegistryEndpoint', 'write_file', '@earendil-works/pi-tui', 'matchesKey', 'onTerminalInput', 'terminalShortcutAction', 'consume: true']:
            self.assertIn(token, src)
        self.assertNotIn('ctrl+alt+t', src)
        self.assertNotIn('ctrl+alt+shift+t', src)
        for control in ['Toggle: Ctrl+Alt+End', 'Scroll: Ctrl+Alt+Up/Down', 'Page: Ctrl+Alt+PageUp/PageDown', 'Focus current: Ctrl+Alt+Home']:
            self.assertIn(control, src)
        install = (ROOT / 'install.sh').read_text(encoding='utf-8')
        self.assertIn('PI_EXTENSIONS_DIR', install)
        self.assertIn('story-film-progress.ts', install)

    def test_todo_docs_define_compact_and_checkpoint_sync_rules(self):
        pipeline_skill = (ROOT / 'skills/pipeline-progress/SKILL.md').read_text(encoding='utf-8')
        docs = (ROOT / 'docs/production/todo-and-progress.md').read_text(encoding='utf-8')
        router = (ROOT / 'skills/story-film/SKILL.md').read_text(encoding='utf-8')
        for token in ['three visible pipeline rows', '/story-todo toggle', 'Do not work ahead', 'at most three Story-Film items']:
            self.assertIn(token, pipeline_skill)
        for token in ['Compact mode shows three pipeline rows', 'Both compact and expanded modes show the full keyboard control legend', 'Why a Todo can look stale', 'at most three Story-Film items', 'Ctrl+Alt+End', 'Ctrl+Alt+PageUp/PageDown', 'Ctrl+Alt+Home', '/story-todo help']:
            self.assertIn(token, docs)
        self.assertNotIn('Ctrl+Alt+T', docs)
        self.assertNotIn('Ctrl+Alt+Shift+T', docs)
        self.assertIn('Do not start a later specialist or write a later artifact', router)

    def test_feature_sequence_and_context_shards(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            scenes = {'scenes': [{'scene_id': f'SCN-{i:03d}', 'title': f'Scene {i}'} for i in range(1, 7)]}
            (project / '02_screenplay/scene_manifest.json').write_text(json.dumps(scenes), encoding='utf-8')
            (project / '02_screenplay/line_manifest.jsonl').write_text('\n'.join(json.dumps({'line_id': f'LINE-{i:03d}', 'scene_id': f'SCN-{i:03d}', 'text': f'Line {i}'}) for i in range(1, 7))+'\n', encoding='utf-8')
            manifest = sequence_manager.init_manifest(project, 3, force=True)
            self.assertEqual([x['sequence_id'] for x in manifest['sequences']], ['SEQ-001', 'SEQ-002'])
            index = context_shards.build_all(project)
            self.assertEqual(len(index['shards']), 2)
            shard1 = json.loads((project / '00_project/shards/SEQ-001/context.json').read_text())
            shard2 = json.loads((project / '00_project/shards/SEQ-002/context.json').read_text())
            self.assertEqual(shard1['scene_ids'], ['SCN-001','SCN-002','SCN-003'])
            self.assertEqual(shard2['scene_ids'], ['SCN-004','SCN-005','SCN-006'])
            self.assertTrue(all(x['scene_id'] in shard1['scene_ids'] for x in shard1['records']['lines']))

    def test_production_health_reports_blocked_pipeline(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            progress = json.loads((project / '00_project/pipeline_progress.json').read_text())
            progress['status'] = 'blocked'; progress['blocker'] = 'Test blocker'
            (project / '00_project/pipeline_progress.json').write_text(json.dumps(progress), encoding='utf-8')
            report = production_health.write_report(project)
            self.assertEqual(report['status'], 'blocked')
            self.assertIn('Test blocker', json.dumps(report))
            self.assertTrue((project / '00_project/health_report.md').is_file())

    def test_long_range_continuity_detects_distant_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            seq = {'schema_version':1,'sequences':[
                {'sequence_id':'SEQ-001','order':1,'scene_ids':['SCN-001'],'status':'planned','shard_path':'00_project/shards/SEQ-001/context.json'},
                {'sequence_id':'SEQ-002','order':2,'scene_ids':['SCN-002'],'status':'planned','shard_path':'00_project/shards/SEQ-002/context.json'},
                {'sequence_id':'SEQ-003','order':3,'scene_ids':['SCN-003'],'status':'planned','shard_path':'00_project/shards/SEQ-003/context.json'}]}
            (project/'00_project/sequence_manifest.json').write_text(json.dumps(seq),encoding='utf-8')
            (project/'03_preproduction/continuity/anchors.jsonl').write_text(json.dumps({'anchor_id':'CONT-001','kind':'injury','subject_id':'CHAR-001','source_sequence':'SEQ-001','target_sequences':['SEQ-003'],'expected_state':'bandaged'})+'\n',encoding='utf-8')
            (project/'03_preproduction/continuity/observations.jsonl').write_text(json.dumps({'anchor_id':'CONT-001','sequence_id':'SEQ-003','observed_state':'uninjured','evidence':'shot brief'})+'\n',encoding='utf-8')
            report = long_range_continuity.audit(project)
            self.assertFalse(report['ready'])
            self.assertEqual(report['conflicts'][0]['sequence_distance'], 2)

    def test_generation_scheduler_respects_memory_and_model_groups(self):
        with tempfile.TemporaryDirectory() as td:
            project=Path(td)/'film'; subprocess.run([sys.executable,str(ROOT/'scripts/init_story_project.py'),str(project)],check=True,stdout=subprocess.DEVNULL)
            resources={'schema_version':1,'machine':{'vram_gib':24,'ram_gib':64,'vram_reserve_gib':2,'ram_reserve_gib':4},'profiles':{
                'image':{'vram_gib':10,'ram_gib':8,'exclusive_gpu':True,'estimated_seconds_per_job':10,'resident_group':'image'},
                'video':{'vram_gib':20,'ram_gib':16,'exclusive_gpu':True,'estimated_seconds_per_job':30,'resident_group':'video'}}}
            (project/'04_generation/generation_resources.json').write_text(json.dumps(resources),encoding='utf-8')
            batch={'schema_version':1,'batch_id':'BATCH-001','jobs':[
                {'job_id':'JOB-001','resource_profile':'image','blocked_by':[]},
                {'job_id':'JOB-002','resource_profile':'image','blocked_by':[]},
                {'job_id':'JOB-003','resource_profile':'video','blocked_by':['JOB-001']} ]}
            (project/'04_generation/comfyui/offline_batch.json').write_text(json.dumps(batch),encoding='utf-8')
            report=generation_scheduler.build(project)
            self.assertTrue(report['ready'])
            self.assertEqual(report['waves'][0]['resident_group'],'image')
            self.assertTrue(report['llm_unload_required'])
            resources['profiles']['video']['vram_gib']=23
            (project/'04_generation/generation_resources.json').write_text(json.dumps(resources),encoding='utf-8')
            self.assertFalse(generation_scheduler.build(project)['ready'])

    def test_recovery_checkpoint_exact_dirty_and_resource_interrupted(self):
        with tempfile.TemporaryDirectory() as td:
            project=Path(td)/'film'; subprocess.run([sys.executable,str(ROOT/'scripts/init_story_project.py'),str(project)],check=True,stdout=subprocess.DEVNULL)
            recovery_checkpoint.snapshot(project,'before restart')
            self.assertEqual(recovery_checkpoint.resume_report(project)['resume_mode'],'exact')
            state=json.loads((project/'00_project/state.json').read_text()); state['test_change']=1
            (project/'00_project/state.json').write_text(json.dumps(state),encoding='utf-8')
            self.assertEqual(recovery_checkpoint.resume_report(project)['resume_mode'],'dirty')
            resource=json.loads((project/'00_project/resource_handoff.json').read_text()); resource['phase']='running-comfyui'
            (project/'00_project/resource_handoff.json').write_text(json.dumps(resource),encoding='utf-8')
            self.assertEqual(recovery_checkpoint.resume_report(project)['resume_mode'],'resource-interrupted')

    def test_partial_batch_recovery_preserves_completed_jobs(self):
        with tempfile.TemporaryDirectory() as td:
            project=Path(td)/'film'; subprocess.run([sys.executable,str(ROOT/'scripts/init_story_project.py'),str(project)],check=True,stdout=subprocess.DEVNULL)
            batch={'schema_version':1,'batch_id':'BATCH-001','jobs':[
                {'job_id':'JOB-001','blocked_by':[]},{'job_id':'JOB-002','blocked_by':[]},{'job_id':'JOB-003','blocked_by':['JOB-002']}]}
            result={'schema_version':1,'batch_id':'BATCH-001','status':'failed','jobs':[
                {'job_id':'JOB-001','status':'complete'},{'job_id':'JOB-002','status':'failed'}]}
            (project/'04_generation/comfyui/offline_batch.json').write_text(json.dumps(batch),encoding='utf-8')
            (project/'04_generation/comfyui/offline_batch_result.json').write_text(json.dumps(result),encoding='utf-8')
            retry=batch_recovery.build_retry(project)
            ids=[x['job_id'] for x in retry['jobs']]
            self.assertNotIn('JOB-001',ids); self.assertIn('JOB-002',ids); self.assertIn('JOB-003',ids)

    def test_editorial_reconciliation_requires_selected_shots(self):
        with tempfile.TemporaryDirectory() as td:
            project=Path(td)/'film'; subprocess.run([sys.executable,str(ROOT/'scripts/init_story_project.py'),str(project)],check=True,stdout=subprocess.DEVNULL)
            seq={'schema_version':1,'sequences':[{'sequence_id':'SEQ-001','order':1,'scene_ids':['SCN-001'],'status':'approved','shard_path':'00_project/shards/SEQ-001/context.json'}]}
            (project/'00_project/sequence_manifest.json').write_text(json.dumps(seq),encoding='utf-8')
            (project/'04_generation/shot_briefs.jsonl').write_text('\n'.join([json.dumps({'shot_id':'SHOT-001','scene_id':'SCN-001'}),json.dumps({'shot_id':'SHOT-002','scene_id':'SCN-001'})])+'\n',encoding='utf-8')
            selections={'shots':{'SHOT-001':{'selected_take_id':'TAKE-001'},'SHOT-002':{'selected_take_id':'TAKE-002'}}}
            (project/'04_generation/selections.json').write_text(json.dumps(selections),encoding='utf-8')
            (project/'05_post/timeline.json').write_text(json.dumps({'timeline_id':'FILM','events':[{'event_id':'EVT-001','shot_id':'SHOT-001','duration':1.0}]}),encoding='utf-8')
            report=editorial_reconcile.reconcile(project)
            self.assertFalse(report['ready']); self.assertEqual(report['missing_selected_shots'],['SHOT-002'])

    def test_completeness_audit_does_not_accept_master_file_alone(self):
        with tempfile.TemporaryDirectory() as td:
            project=Path(td)/'film'; subprocess.run([sys.executable,str(ROOT/'scripts/init_story_project.py'),str(project)],check=True,stdout=subprocess.DEVNULL)
            master=project/'05_post/masters/film_master.mp4'; master.parent.mkdir(parents=True,exist_ok=True); master.write_bytes(b'not-a-complete-film')
            report=completeness_audit.audit(project)
            self.assertFalse(report['complete'])
            self.assertTrue(report['blockers'])

    def test_documentation_navigation_and_required_readme_header(self):
        subprocess.run([sys.executable,str(ROOT/'scripts/check_docs.py')],check=True)
        readme=(ROOT/'README.md').read_text(encoding='utf-8').splitlines()
        self.assertEqual(readme[0],'# Story-Film Skills')
        self.assertIn('Alan Guice (Badgids)',readme[2])
        self.assertIn('Apache License 2.0',readme[3])
        self.assertTrue(readme[4].startswith('*Copyright'))

    def test_apache_attribution_metadata(self):
        self.assertIn('Apache License', (ROOT/'LICENSE').read_text(encoding='utf-8'))
        notice=(ROOT/'NOTICE').read_text(encoding='utf-8')
        self.assertIn('Alan Guice (Badgids)', notice)
        for p in (ROOT/'skills').glob('*/SKILL.md'):
            text=p.read_text(encoding='utf-8')
            self.assertIn('author: Alan Guice (Badgids)',text,p.name)
            self.assertIn('license: Apache-2.0',text,p.name)

    def test_npx_bundle_is_self_contained(self):
        subprocess.run([sys.executable,str(ROOT/'scripts/build_npx_bundle.py'),'--check'],check=True,stdout=subprocess.DEVNULL)
        bundle=ROOT/'skills/story-film-suite/bundle'
        self.assertTrue((bundle/'skills/story-film/SKILL.md').is_file())
        self.assertTrue((bundle/'scripts/init_story_project.py').is_file())
        self.assertTrue((bundle/'references/CORE_CONTRACT.md').is_file())
        self.assertTrue((bundle/'docs/README.md').is_file())
        self.assertTrue((bundle/'examples/catalog.json').is_file())
        self.assertFalse((bundle/'skills/story-film-suite').exists())


    def test_example_prompt_catalog_has_three_per_production_level(self):
        subprocess.run([sys.executable,str(ROOT/'scripts/validate_examples.py')],check=True)
        data=json.loads((ROOT/'examples/catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(len(data['tiers']['video']),3)
        self.assertEqual(len(data['tiers']['short-film']),3)
        self.assertEqual(len(data['tiers']['movie']),3)
        self.assertTrue(all(x['target_minutes'] >= 90 for x in data['tiers']['movie']))

    def test_comfyui_workflow_detect_validate_and_patch(self):
        workflow = {
            '1': {'class_type': 'TestNode', 'inputs': {'choice': 'a', 'value': 3}},
            '2': {'class_type': 'SaveTest', 'inputs': {'data': ['1', 0]}},
        }
        self.assertEqual(comfyui_workflow.detect_format(workflow), 'api')
        self.assertEqual(comfyui_workflow.validate_offline(workflow), [])
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / 'wf.json'
            dst = Path(td) / 'patched.json'
            src.write_text(json.dumps(workflow), encoding='utf-8')
            subprocess.run([sys.executable, str(ROOT / 'scripts/comfyui_workflow.py'), 'patch', str(src), '--node', '1', '--input', 'choice', '--value', 'b', '--out', str(dst)], check=True)
            patched = json.loads(dst.read_text())
            self.assertEqual(patched['1']['inputs']['choice'], 'b')
            self.assertEqual(workflow['1']['inputs']['choice'], 'a')

    def test_comfyui_native_live_validation_and_outputs(self):
        workflow = {
            '1': {'class_type': 'TestNode', 'inputs': {'choice': 'a', 'value': 3}},
            '2': {'class_type': 'SaveTest', 'inputs': {'data': ['1', 0]}},
        }
        with FakeComfyServer() as srv:
            client = comfyui_control.Client(srv.url)
            probe = client.probe()
            self.assertTrue(probe['reachable'])
            verdict = client.validate_workflow(workflow)
            self.assertTrue(verdict['valid'], verdict)
            self.assertEqual(verdict['output_nodes'], ['2'])
            bad = json.loads(json.dumps(workflow))
            bad['1']['inputs']['choice'] = 'not-live'
            verdict = client.validate_workflow(bad)
            self.assertFalse(verdict['valid'])
            record = client.wait(FakeComfyHandler.prompt_id, timeout=2, poll_interval=0.01)
            files, text = client.output_entries(record)
            self.assertEqual({x['filename'] for x in files}, {'frame.png', 'mesh.glb'})
            self.assertEqual(text['3'], ['done'])

    def test_comfyui_native_run_records_and_download(self):
        workflow = {
            '1': {'class_type': 'TestNode', 'inputs': {'choice': 'a', 'value': 3}},
            '2': {'class_type': 'SaveTest', 'inputs': {'data': ['1', 0]}},
        }
        with tempfile.TemporaryDirectory() as td, FakeComfyServer() as srv:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            wf = project / '04_generation/comfyui/workflows/test.json'
            wf.write_text(json.dumps(workflow), encoding='utf-8')
            base = [sys.executable, str(ROOT / 'scripts/comfyui_control.py'), '--url', srv.url, '--project', str(project)]
            subprocess.run(base + ['probe'], check=True, stdout=subprocess.DEVNULL)
            submitted = subprocess.run(base + ['submit', '--workflow', str(wf), '--item-id', 'SHOT-001'], check=True, text=True, stdout=subprocess.PIPE)
            pid = json.loads(submitted.stdout)['prompt_id']
            subprocess.run(base + ['wait', pid, '--wait-timeout', '2', '--poll', '0.01'], check=True, stdout=subprocess.DEVNULL)
            out_dir = project / '04_generation/comfyui/outputs'
            subprocess.run(base + ['download', pid, '--out-dir', str(out_dir)], check=True, stdout=subprocess.DEVNULL)
            snapshot = json.loads((project / '04_generation/comfyui/server_snapshot.json').read_text())
            self.assertEqual(snapshot['server'], srv.url)
            rec = json.loads((project / f'04_generation/comfyui/runs/{pid}.json').read_text())
            self.assertEqual(rec['workflow_path'], '04_generation/comfyui/workflows/test.json')
            self.assertEqual(rec['item_id'], 'SHOT-001')
            self.assertEqual(rec['status'], 'success')
            self.assertEqual(len(rec['outputs']), 2)
            self.assertTrue((out_dir / 'frame.png').is_file())
            self.assertTrue((out_dir / 'mesh.glb').is_file())
            rows = [json.loads(x) for x in (project / '04_generation/comfyui/run_index.jsonl').read_text().splitlines() if x.strip()]
            self.assertEqual(rows[0]['item_id'], 'SHOT-001')
            self.assertEqual(rows[0]['event'], 'submit')

    def test_comfyui_upload_and_targeted_cancel(self):
        with tempfile.TemporaryDirectory() as td, FakeComfyServer() as srv:
            src = Path(td) / 'input.png'
            src.write_bytes(b'png-ish')
            client = comfyui_control.Client(srv.url)
            uploaded = client.upload_image(src, subfolder='refs')
            self.assertEqual(uploaded['name'], 'uploaded.png')
            self.assertEqual(uploaded['type'], 'input')
            masked = client.upload_mask(src, original_filename='frame.png', original_type='output')
            self.assertEqual(masked['name'], 'uploaded-mask.png')
            cancelled = client.cancel(FakeComfyHandler.prompt_id)
            self.assertTrue(cancelled['cancelled'])
            self.assertEqual(cancelled['method'], 'api_job_cancel')

    def test_comfyui_rejects_ui_format_for_native_submit(self):
        ui_workflow = {'nodes': [{'id': 1, 'type': 'TestNode'}], 'links': []}
        with FakeComfyServer() as srv:
            client = comfyui_control.Client(srv.url)
            with self.assertRaises(ValueError):
                client.submit(ui_workflow)
            self.assertEqual(comfyui_workflow.detect_format(ui_workflow), 'ui')

    def test_comfyui_url_rejects_embedded_credentials(self):
        with self.assertRaises(ValueError):
            comfyui_control.resolve_url('http://user:secret@127.0.0.1:8188')
        with self.assertRaises(ValueError):
            comfy_api_v2.resolve_url('http://token:secret@127.0.0.1:8189')

    def test_comfyui_cli_mutation_guards(self):
        with self.assertRaises(PermissionError):
            comfyui_cli_bridge.require_confirmation(False, 'Custom node install')
        comfyui_cli_bridge.require_confirmation(True, 'Custom node install')
        with self.assertRaises(ValueError):
            comfyui_cli_bridge.reject_all(['all'], 'Custom node update')
        with self.assertRaises(ValueError):
            comfyui_cli_bridge.safe_model_url('https://example.invalid/model.safetensors?token=secret')
        self.assertEqual(
            comfyui_cli_bridge.safe_model_url('https://example.invalid/model.safetensors'),
            'https://example.invalid/model.safetensors',
        )

    def test_comfy_api_v2_basic_job_flow(self):
        workflow = {'1': {'class_type': 'TestNode', 'inputs': {'choice': 'a', 'value': 3}}}
        with FakeComfyServer() as srv:
            client = comfy_api_v2.V2Client(srv.url, timeout=2)
            self.assertTrue(client.health()['ok'])
            created = client.submit(workflow, idempotency_key='case-1', api_key_env=None)
            self.assertEqual(created['id'], FakeComfyHandler.prompt_id)
            finished = client.wait(FakeComfyHandler.prompt_id, timeout=2, poll=0.01)
            self.assertEqual(finished['status'], 'completed')


    def test_narrative_state_ordering_and_posthumous_presence(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            state = {
                'schema_version': 1,
                'scene_order': ['SCN-001', 'SCN-002', 'SCN-003'],
                'characters': {
                    'CHAR-001': {'life_state': 'dead', 'death_scene': 'SCN-002'},
                },
                'props': {},
                'questions': {
                    'QST-001': {'text': 'Who called?', 'introduced_in': 'SCN-001', 'status': 'resolved', 'resolved_in': 'SCN-003'},
                },
                'promises': {
                    'PROM-001': {'text': 'The key will return.', 'setup_in': 'SCN-001', 'status': 'paid', 'payoff_in': 'SCN-003'},
                },
                'events': [
                    {'scene_id': 'SCN-003', 'order': 3, 'active_characters': [], 'mentions': ['CHAR-001'], 'flashback': False},
                ],
            }
            (project / '01_story/story_state.json').write_text(json.dumps(state, indent=2) + '\n')
            subprocess.run([sys.executable, str(ROOT / 'scripts/validate_story_project.py'), str(project)], check=True)
            state['questions']['QST-001']['introduced_in'] = 'SCN-003'
            state['questions']['QST-001']['resolved_in'] = 'SCN-001'
            state['promises']['PROM-001']['setup_in'] = 'SCN-003'
            state['promises']['PROM-001']['payoff_in'] = 'SCN-001'
            state['events'][0]['active_characters'] = ['CHAR-001']
            state['events'][0]['mentions'] = []
            (project / '01_story/story_state.json').write_text(json.dumps(state, indent=2) + '\n')
            proc = subprocess.run([sys.executable, str(ROOT / 'scripts/validate_story_project.py'), str(project)], text=True, stdout=subprocess.PIPE)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('resolves before introduction', proc.stdout)
            self.assertIn('pays off before setup', proc.stdout)
            self.assertIn('active appearance of CHAR-001 after death', proc.stdout)

    def test_take_selection_validation(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            (project / '04_generation/shot_briefs.jsonl').write_text(json.dumps({
                'shot_id': 'SHOT-001', 'scene_id': 'SCN-001', 'references': []
            }) + '\n')
            takes = project / '04_generation/take_manifest.jsonl'
            takes.write_text(json.dumps({
                'take_id': 'TAKE-001',
                'shot_id': 'SHOT-001',
                'path': '04_generation/comfyui/outputs/shot-1.mp4',
                'status': 'selected',
                'assessment': {'continuity': 'pass'},
            }) + '\n')
            (project / '04_generation/selections.json').write_text(json.dumps({
                'schema_version': 1,
                'shots': {'SHOT-001': {'selected_take_id': 'TAKE-001', 'reason': 'best cut fit', 'alternates': []}},
            }, indent=2) + '\n')
            subprocess.run([sys.executable, str(ROOT / 'scripts/validate_story_project.py'), str(project)], check=True)
            bad = {'schema_version': 1, 'shots': {'SHOT-002': {'selected_take_id': 'TAKE-001'}}}
            (project / '04_generation/selections.json').write_text(json.dumps(bad, indent=2) + '\n')
            proc = subprocess.run([sys.executable, str(ROOT / 'scripts/validate_story_project.py'), str(project)], text=True, stdout=subprocess.PIPE)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('belonging to SHOT-001', proc.stdout)

    def test_executable_production_plan_validation_and_coverage(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            (project / '02_screenplay/screenplay.fountain').write_text('INT. ROOM - DAY\n\nALICE\nHello.\n', encoding='utf-8')
            (project / '02_screenplay/line_manifest.jsonl').write_text(json.dumps({
                'line_id': 'LINE-001', 'scene_id': 'SCN-001', 'order': 1, 'kind': 'dialogue',
                'character_id': 'CHAR-001', 'text': 'Hello.', 'audible': True,
                'on_screen': True, 'blocking_required': True,
            }) + '\n', encoding='utf-8')
            (project / '04_generation/shot_briefs.jsonl').write_text(json.dumps({
                'shot_id': 'SHOT-001', 'scene_id': 'SCN-001', 'line_ids': ['LINE-001'], 'references': []
            }) + '\n', encoding='utf-8')
            (project / '04_generation/voice_cues.jsonl').write_text(json.dumps({
                'line_id': 'LINE-001', 'speaker': 'CHAR-001', 'text': 'Hello.', 'measured_duration_s': 1.0
            }) + '\n', encoding='utf-8')
            (project / '03_preproduction/performance_blocking.jsonl').write_text(json.dumps({
                'line_id': 'LINE-001', 'scene_id': 'SCN-001', 'character_ids': ['CHAR-001'],
                'initial_state': {'anchor': 'door'}, 'moves': [], 'actions': [],
                'end_state': {'anchor': 'door'}, 'timing': {'source': 'measured-speech', 'dialogue_duration_s': 1.0},
                'constraints': [],
            }) + '\n', encoding='utf-8')
            (project / '03_preproduction/shooting_script.json').write_text(json.dumps({
                'schema_version': 1, 'source_screenplay': '02_screenplay/screenplay.fountain',
                'line_manifest': '02_screenplay/line_manifest.jsonl',
                'scenes': [{'scene_id': 'SCN-001', 'location_id': 'LOC-001', 'initial_positions': [], 'units': [{
                    'line_id': 'LINE-001', 'kind': 'dialogue', 'speaker': 'CHAR-001', 'text': 'Hello.',
                    'current_positions': [], 'moves': [], 'actions': [], 'shot_ids': ['SHOT-001'],
                    'timing': {'source': 'measured-speech', 'speech_duration_s': 1.0, 'planned_duration_s': 2.0},
                    'constraints': [],
                }]}],
            }, indent=2) + '\n', encoding='utf-8')
            subprocess.run([sys.executable, str(ROOT / 'scripts/validate_story_project.py'), str(project)], check=True)
            subprocess.run([sys.executable, str(ROOT / 'scripts/production_coverage.py'), str(project), '--no-write'], check=True, stdout=subprocess.DEVNULL)
            (project / '04_generation/voice_cues.jsonl').unlink()
            proc = subprocess.run([sys.executable, str(ROOT / 'scripts/production_coverage.py'), str(project), '--no-write'], text=True, stdout=subprocess.PIPE)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('LINE-001', proc.stdout)
            self.assertIn('missing_voice', proc.stdout)

    def test_media_qc_failed_take_requires_explicit_override(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            (project / '04_generation/shot_briefs.jsonl').write_text(json.dumps({
                'shot_id': 'SHOT-001', 'scene_id': 'SCN-001', 'references': []
            }) + '\n', encoding='utf-8')
            (project / '04_generation/take_manifest.jsonl').write_text(json.dumps({
                'take_id': 'TAKE-001', 'shot_id': 'SHOT-001', 'path': '04_generation/outputs/shot.mp4', 'status': 'candidate'
            }) + '\n', encoding='utf-8')
            (project / '04_generation/take_qc.jsonl').write_text(json.dumps({
                'take_id': 'TAKE-001', 'shot_id': 'SHOT-001', 'overall': 'fail',
                'checks': {'script_faithfulness': {'status': 'fail', 'evidence': 'wrong action'}}, 'metrics': []
            }) + '\n', encoding='utf-8')
            (project / '04_generation/selections.json').write_text(json.dumps({
                'schema_version': 1, 'shots': {'SHOT-001': {'selected_take_id': 'TAKE-001', 'reason': 'preferred'}}
            }, indent=2) + '\n', encoding='utf-8')
            proc = subprocess.run([sys.executable, str(ROOT / 'scripts/validate_story_project.py'), str(project)], text=True, stdout=subprocess.PIPE)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('without qc_override', proc.stdout)
            (project / '04_generation/selections.json').write_text(json.dumps({
                'schema_version': 1, 'shots': {'SHOT-001': {
                    'selected_take_id': 'TAKE-001', 'reason': 'User explicitly accepts the known action mismatch', 'qc_override': True
                }}
            }, indent=2) + '\n', encoding='utf-8')
            subprocess.run([sys.executable, str(ROOT / 'scripts/validate_story_project.py'), str(project)], check=True)

    def test_project_impact_minimal_invalidation(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project), '--title', 'Impact'], check=True)
            deps = {
                'schema_version': 1,
                'artifacts': {
                    'scene-a': {'path': '01_story/a.md', 'depends_on': []},
                    'shots-a': {'path': '03_preproduction/a.csv', 'depends_on': ['scene-a']},
                    'scene-b': {'path': '01_story/b.md', 'depends_on': []},
                    'shots-b': {'path': '03_preproduction/b.csv', 'depends_on': ['scene-b']},
                },
            }
            (project / '00_project/dependencies.json').write_text(json.dumps(deps, indent=2) + '\n')
            for rel in ['01_story/a.md', '01_story/b.md', '03_preproduction/a.csv', '03_preproduction/b.csv']:
                p = project / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(rel + '\n')
            state = json.loads((project / '00_project/state.json').read_text())
            state['artifacts'] = {
                'scene-a': {'status': 'approved'}, 'shots-a': {'status': 'approved'},
                'scene-b': {'status': 'approved'}, 'shots-b': {'status': 'approved'},
            }
            (project / '00_project/state.json').write_text(json.dumps(state, indent=2) + '\n')
            subprocess.run([sys.executable, str(ROOT / 'scripts/project_status.py'), str(project), '--changed', 'scene-a', '--apply'], check=True)
            state = json.loads((project / '00_project/state.json').read_text())
            self.assertEqual(state['artifacts']['shots-a']['status'], 'stale')
            self.assertEqual(state['artifacts']['shots-b']['status'], 'approved')


    def test_media_registry_primary_and_qc_override(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            first = subprocess.run([
                sys.executable, str(ROOT / 'scripts/media_registry.py'), str(project), 'add',
                '--kind', 'music', '--group-id', 'MUS-001', '--path', '04_generation/music/a.wav', '--qc-status', 'pass'
            ], check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
            second = subprocess.run([
                sys.executable, str(ROOT / 'scripts/media_registry.py'), str(project), 'add',
                '--kind', 'music', '--group-id', 'MUS-001', '--path', '04_generation/music/b.wav', '--qc-status', 'fail'
            ], check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
            subprocess.run([
                sys.executable, str(ROOT / 'scripts/media_registry.py'), str(project), 'select', first, '--reason', 'clean candidate'
            ], check=True, stdout=subprocess.DEVNULL)
            proc = subprocess.run([
                sys.executable, str(ROOT / 'scripts/media_registry.py'), str(project), 'select', second, '--reason', 'known defect'
            ], text=True, stdout=subprocess.PIPE)
            self.assertNotEqual(proc.returncode, 0)
            subprocess.run([
                sys.executable, str(ROOT / 'scripts/media_registry.py'), str(project), 'select', second,
                '--reason', 'user accepts known defect', '--qc-override'
            ], check=True, stdout=subprocess.DEVNULL)
            records = media_registry.load_records(project / '00_project/media_registry.jsonl')
            approvals = media_registry.load_approvals(project / '00_project/media_approvals.json')
            self.assertEqual(media_registry.validate(records, approvals), [])
            self.assertEqual(approvals['groups']['MUS-001']['primary_media_id'], second)
            statuses = {r['media_id']: r['status'] for r in records}
            self.assertEqual(statuses[first], 'alternate')
            self.assertEqual(statuses[second], 'primary')

    def test_audio_mix_validation_and_filter_command(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            source = project / '04_generation/audio/source.wav'
            source.parent.mkdir(parents=True, exist_ok=True)
            with wave.open(str(source), 'wb') as wf:
                wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(48000)
                samples = bytearray()
                for i in range(4800):
                    value = int(6000 * math.sin(2 * math.pi * 440 * i / 48000))
                    samples += int(value).to_bytes(2, 'little', signed=True)
                wf.writeframes(bytes(samples))
            mix = {
                'schema_version': 1, 'sample_rate': 48000, 'channels': 2,
                'target_lufs': -16.0, 'true_peak_db': -1.5,
                'output_path': '05_post/masters/test.wav',
                'tracks': [{
                    'event_id': 'AUD-001', 'kind': 'dialogue', 'source_id': 'VOICE-001',
                    'path': '04_generation/audio/source.wav', 'start': 0.25, 'source_in': 0.0,
                    'duration': 0.1, 'gain_db': -2.0, 'pan': 0.2, 'fade_in': 0.01, 'fade_out': 0.02
                }]
            }
            self.assertEqual(audio_master.validate_manifest(project, mix, require_sources=True), [])
            cmd = audio_master.build_command(project, mix)
            joined = ' '.join(cmd)
            self.assertIn('amix=inputs=1', joined)
            self.assertIn('loudnorm=I=-16.00', joined)
            self.assertIn('adelay=250|250', joined)
            bad = json.loads(json.dumps(mix))
            bad['tracks'][0]['path'] = '/absolute/source.wav'
            self.assertTrue(audio_master.validate_manifest(project, bad, require_sources=False))

    def test_timeline_validation_and_mlt_export(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            dummy = project / '04_generation/video/clip.mp4'
            dummy.parent.mkdir(parents=True, exist_ok=True)
            dummy.write_bytes(b'placeholder')
            timeline = {
                'schema_version': 1, 'timeline_id': 'MASTER-001', 'title': 'Test',
                'video': {'width': 640, 'height': 360, 'fps': 24.0, 'pixel_format': 'yuv420p'},
                'output_path': '05_post/masters/test.mp4',
                'events': [
                    {'event_id': 'EVT-001', 'kind': 'video', 'path': '04_generation/video/clip.mp4', 'source_in': 0.25, 'duration': 1.0},
                    {'event_id': 'EVT-002', 'kind': 'color', 'color': 'black', 'duration': 0.5},
                ]
            }
            self.assertEqual(render_timeline.validate_timeline(project, timeline, require_sources=True), [])
            tpath = project / '05_post/timeline.json'
            tpath.write_text(json.dumps(timeline, indent=2) + '\n')
            out = project / '05_post/editorial/test.mlt'
            mlt_export.export_mlt(project, timeline, out)
            text = out.read_text()
            self.assertIn('04_generation/video/clip.mp4', text)
            self.assertIn('playlist0', text)
            self.assertIn('producer id="producer1" in="6" out="29"', text)
            bad = json.loads(json.dumps(timeline))
            bad['events'][1]['event_id'] = 'BAD-001'
            self.assertTrue(render_timeline.validate_timeline(project, bad, require_sources=False))

    def test_social_reframe_crop_math(self):
        cw, ch, x, y = social_reframe.cover_crop(1920, 1080, 1080, 1920, 0.75, 0.5)
        self.assertEqual(ch, 1080)
        self.assertLess(cw, 1920)
        self.assertGreaterEqual(x, 0)
        self.assertLessEqual(x + cw, 1920)
        self.assertEqual(y, 0)

    def test_promo_validation_duration_and_social_ids(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            trailer_dir = project / '06_release/trailers/TRL-001'
            trailer_dir.mkdir(parents=True, exist_ok=True)
            timeline = {
                'schema_version': 1, 'timeline_id': 'TRL-001', 'title': 'Trailer',
                'video': {'width': 640, 'height': 360, 'fps': 24.0, 'pixel_format': 'yuv420p'},
                'output_path': '06_release/trailers/TRL-001/master.mp4',
                'events': [
                    {'event_id': 'EVT-001', 'kind': 'color', 'color': 'black', 'duration': 0.5},
                    {'event_id': 'EVT-002', 'kind': 'color', 'color': 'white', 'duration': 0.5},
                ]
            }
            (trailer_dir / 'timeline.json').write_text(json.dumps(timeline, indent=2) + '\n')
            manifest = {
                'schema_version': 1, 'campaign_id': 'CAMP-001',
                'trailers': [{
                    'trailer_id': 'TRL-001', 'type': 'teaser', 'target_duration': 1.0, 'duration_tolerance': 0.1,
                    'aspect_ratio': '16:9', 'spoiler_policy': 'Do not reveal ending',
                    'timeline_path': '06_release/trailers/TRL-001/timeline.json',
                    'audio_mix_path': '06_release/trailers/TRL-001/audio_mix.json',
                    'output_path': '06_release/trailers/TRL-001/master.mp4',
                    'structure': [{'role': 'hook', 'purpose': 'curiosity'}]
                }]
            }
            (project / '06_release/trailers/trailer_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
            self.assertEqual(promo_validate.validate_trailers(project), [])
            manifest['trailers'][0]['target_duration'] = 2.0
            (project / '06_release/trailers/trailer_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
            self.assertTrue(any('outside target' in e for e in promo_validate.validate_trailers(project)))
            campaign = {
                'schema_version': 1, 'campaign_id': 'CAMP-001', 'verified_release_facts': {},
                'unresolved_release_facts': {}, 'content_pillars': [], 'platforms': []
            }
            (project / '06_release/social/campaign.json').write_text(json.dumps(campaign, indent=2) + '\n')
            (project / '06_release/social/deliverables.jsonl').write_text(json.dumps({
                'schema_version': 1, 'social_id': 'SOC-001', 'platform': 'test', 'placement': 'short',
                'media_type': 'video', 'aspect_ratio': '9:16', 'target_duration': 1.0,
                'source_ids': ['TRL-001'], 'timeline_path': '06_release/social/SOC-001/timeline.json',
                'output_path': '06_release/social/masters/SOC-001.mp4', 'copy_id': 'COPY-001'
            }) + '\n')
            self.assertEqual(promo_validate.validate_social(project), [])

    def test_release_package_checksums_and_collection(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            film = project / '05_post/masters/film_master.mp4'
            film.write_bytes(b'finished-film-test')
            manifest = {
                'schema_version': 1,
                'deliverables': [{
                    'delivery_id': 'DELIV-001', 'kind': 'film-master',
                    'path': '05_post/masters/film_master.mp4', 'required': True, 'qc_status': 'pass', 'source_ids': ['MASTER-001']
                }]
            }
            (project / '06_release/release_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
            subprocess.run([sys.executable, str(ROOT / 'scripts/release_package.py'), str(project), '--validate', '--collect'], check=True, stdout=subprocess.DEVNULL)
            updated = json.loads((project / '06_release/release_manifest.json').read_text())
            self.assertEqual(len(updated['deliverables'][0]['sha256']), 64)
            self.assertTrue((project / '06_release/SHA256SUMS.txt').read_text().strip())
            self.assertTrue((project / '06_release/package/05_post/masters/film_master.mp4').is_file())
            bad_manifest = json.loads(json.dumps(updated))
            bad_manifest['deliverables'][0].pop('qc_status', None)
            errs, _ = release_package.validate_manifest(project, bad_manifest, require_files=True)
            self.assertTrue(any('missing completed QC state' in e for e in errs))

    def test_real_ffmpeg_film_master_pipeline(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            source = project / '04_generation/audio/source.wav'
            source.parent.mkdir(parents=True, exist_ok=True)
            frames = 48000
            with wave.open(str(source), 'wb') as wf:
                wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(48000)
                data = bytearray()
                for i in range(frames):
                    value = int(4000 * math.sin(2 * math.pi * 220 * i / 48000))
                    data += int(value).to_bytes(2, 'little', signed=True)
                wf.writeframes(bytes(data))
            mix = {
                'schema_version': 1, 'sample_rate': 48000, 'channels': 2,
                'target_lufs': -18.0, 'true_peak_db': -2.0,
                'output_path': '05_post/masters/film_audio_master.wav',
                'tracks': [{
                    'event_id': 'AUD-001', 'kind': 'score', 'source_id': 'MUS-001',
                    'path': '04_generation/audio/source.wav', 'start': 0.0, 'source_in': 0.0,
                    'duration': 1.0, 'gain_db': 0.0, 'pan': 0.0, 'fade_in': 0.01, 'fade_out': 0.01
                }]
            }
            (project / '05_post/audio_mix.json').write_text(json.dumps(mix, indent=2) + '\n')
            timeline = {
                'schema_version': 1, 'timeline_id': 'MASTER-001', 'title': 'Tiny Film',
                'video': {'width': 320, 'height': 180, 'fps': 10.0, 'pixel_format': 'yuv420p'},
                'audio_master_path': '05_post/masters/film_audio_master.wav',
                'subtitles_path': '05_post/subtitles.srt', 'subtitle_mode': 'muxed',
                'output_path': '05_post/masters/film_master.mp4',
                'events': [
                    {'event_id': 'EVT-001', 'kind': 'color', 'color': 'black', 'duration': 0.6},
                    {'event_id': 'EVT-002', 'kind': 'color', 'color': 'blue', 'duration': 0.6}
                ]
            }
            (project / '05_post/timeline.json').write_text(json.dumps(timeline, indent=2) + '\n')
            (project / '05_post/subtitles.srt').write_text(
                '1\n00:00:00,100 --> 00:00:00,500\nTiny Film\n', encoding='utf-8'
            )
            (project / '06_release/delivery_specs.json').write_text(json.dumps({
                'schema_version': 1, 'deliverables': [{
                    'delivery_id': 'DELIV-001', 'kind': 'trailer-master',
                    'path': '06_release/trailers/planned.mp4', 'required': False
                }]
            }, indent=2) + '\n')
            subprocess.run([sys.executable, str(ROOT / 'scripts/film_master.py'), str(project), '--dry-run'], check=True, stdout=subprocess.DEVNULL)
            self.assertNotIn('master_duration', json.loads((project / '05_post/audio_mix.json').read_text()))
            self.assertEqual(len(json.loads((project / '06_release/delivery_specs.json').read_text())['deliverables']), 1)
            self.assertFalse((project / '05_post/masters/film_audio_master.wav').exists())
            subprocess.run([sys.executable, str(ROOT / 'scripts/film_master.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            self.assertTrue((project / '05_post/masters/film_audio_master.wav').is_file())
            self.assertTrue((project / '05_post/masters/film_master.mp4').is_file())
            padded_audio_qc = delivery_qc.inspect_one(project, {
                'delivery_id': 'DELIV-098', 'kind': 'audio-master',
                'path': '05_post/masters/film_audio_master.wav', 'video_required': False,
                'duration': 1.2, 'duration_tolerance': 0.02, 'audio_sample_rate': 48000
            })
            self.assertEqual(padded_audio_qc['status'], 'pass')
            self.assertAlmostEqual(padded_audio_qc['observed']['duration'], 1.2, places=2)
            specs = json.loads((project / '06_release/delivery_specs.json').read_text())['deliverables']
            self.assertEqual(specs[0]['delivery_id'], 'DELIV-002')
            self.assertTrue(any(x.get('delivery_id') == 'DELIV-001' for x in specs))
            qc = json.loads((project / '05_post/qc/film_master.json').read_text())
            self.assertNotEqual(qc['status'], 'fail')
            self.assertTrue(any(x['name'] == 'subtitle_stream' and x['status'] == 'pass' for x in qc['checks']))
            self.assertEqual(qc['observed']['subtitle_codec'], 'mov_text')
            signal_qc = delivery_qc.inspect_one(project, {
                'delivery_id': 'DELIV-099', 'kind': 'film-master', 'path': '05_post/masters/film_master.mp4',
                'video_required': True,
                'black_frame_check': {'enabled': True, 'min_duration': 0.2, 'severity': 'warn'}
            })
            black_check = next(x for x in signal_qc['checks'] if x['name'] == 'black_frame_intervals')
            self.assertEqual(black_check['status'], 'warn')
            approvals = json.loads((project / '00_project/media_approvals.json').read_text())
            media_id = approvals['groups']['MASTER-001']['primary_media_id']
            self.assertTrue(media_id.startswith('MEDIA-'))
            subprocess.run([sys.executable, str(ROOT / 'scripts/validate_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)

    def test_real_ffmpeg_trailer_and_social_master_pipeline(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)

            source = project / '04_generation/audio/promo_source.wav'
            source.parent.mkdir(parents=True, exist_ok=True)
            with wave.open(str(source), 'wb') as wf:
                wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(48000)
                data = bytearray()
                for i in range(48000):
                    value = int(2500 * math.sin(2 * math.pi * 330 * i / 48000))
                    data += int(value).to_bytes(2, 'little', signed=True)
                wf.writeframes(bytes(data))

            trailer_dir = project / '06_release/trailers/TRL-001'
            trailer_dir.mkdir(parents=True, exist_ok=True)
            trailer_mix = {
                'schema_version': 1, 'sample_rate': 48000, 'channels': 2,
                'target_lufs': -18.0, 'true_peak_db': -2.0,
                'output_path': '06_release/trailers/TRL-001/audio_master.wav',
                'tracks': [{
                    'event_id': 'AUD-101', 'kind': 'score', 'source_id': 'MUS-001',
                    'path': '04_generation/audio/promo_source.wav', 'start': 0.0, 'source_in': 0.0,
                    'duration': 1.0, 'gain_db': 0.0, 'pan': 0.0, 'fade_in': 0.01, 'fade_out': 0.01
                }]
            }
            (trailer_dir / 'audio_mix.json').write_text(json.dumps(trailer_mix, indent=2) + '\n')
            trailer_timeline = {
                'schema_version': 1, 'timeline_id': 'TRL-001', 'title': 'Tiny Trailer',
                'video': {'width': 320, 'height': 180, 'fps': 10.0, 'pixel_format': 'yuv420p'},
                'audio_master_path': '06_release/trailers/TRL-001/audio_master.wav',
                'output_path': '06_release/trailers/TRL-001/trailer.mp4',
                'events': [{'event_id': 'EVT-101', 'kind': 'color', 'color': 'red', 'duration': 1.0}]
            }
            (trailer_dir / 'timeline.json').write_text(json.dumps(trailer_timeline, indent=2) + '\n')
            trailer_manifest = {
                'schema_version': 1, 'campaign_id': 'CAMP-001', 'trailers': [{
                    'trailer_id': 'TRL-001', 'type': 'official', 'target_duration': 1.0,
                    'duration_tolerance': 0.3, 'spoiler_policy': 'Do not reveal ending.',
                    'structure': ['hook', 'title'], 'source_ids': ['MASTER-001'],
                    'timeline_path': '06_release/trailers/TRL-001/timeline.json',
                    'audio_mix_path': '06_release/trailers/TRL-001/audio_mix.json',
                    'output_path': '06_release/trailers/TRL-001/trailer.mp4'
                }]
            }
            (project / '06_release/trailers/trailer_manifest.json').write_text(json.dumps(trailer_manifest, indent=2) + '\n')

            social_dir = project / '06_release/social/SOC-001'
            social_dir.mkdir(parents=True, exist_ok=True)
            social_timeline = {
                'schema_version': 1, 'timeline_id': 'SOC-001', 'title': 'Tiny Vertical',
                'video': {'width': 180, 'height': 320, 'fps': 10.0, 'pixel_format': 'yuv420p'},
                'output_path': '06_release/social/masters/SOC-001.mp4',
                'events': [{'event_id': 'EVT-201', 'kind': 'color', 'color': 'green', 'duration': 1.0}]
            }
            (social_dir / 'timeline.json').write_text(json.dumps(social_timeline, indent=2) + '\n')
            social_rec = {
                'schema_version': 1, 'social_id': 'SOC-001', 'campaign_id': 'CAMP-001',
                'media_type': 'video', 'aspect_ratio': '9:16', 'target_duration': 1.0,
                'duration_tolerance': 0.3, 'source_ids': ['MASTER-001'],
                'timeline_path': '06_release/social/SOC-001/timeline.json',
                'output_path': '06_release/social/masters/SOC-001.mp4'
            }
            (project / '06_release/social/deliverables.jsonl').write_text(json.dumps(social_rec) + '\n')
            (project / '06_release/social/campaign.json').write_text(json.dumps({
                'schema_version': 1, 'campaign_id': 'CAMP-001', 'verified_release_facts': {},
                'unresolved_release_facts': {}, 'content_pillars': [], 'platforms': []
            }, indent=2) + '\n')

            subprocess.run([sys.executable, str(ROOT / 'scripts/render_promos.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            self.assertTrue((trailer_dir / 'trailer.mp4').is_file())
            self.assertTrue((project / '06_release/social/masters/SOC-001.mp4').is_file())
            self.assertTrue((trailer_dir / 'qc.json').is_file())
            self.assertTrue((project / '06_release/social/qc/SOC-001.json').is_file())
            subprocess.run([
                sys.executable, str(ROOT / 'scripts/promo_delivery.py'), str(project), '--reconcile'
            ], check=True, stdout=subprocess.DEVNULL)
            trailer_delivery = json.loads((project / '06_release/trailers/delivery_report.json').read_text())
            social_delivery = json.loads((project / '06_release/social/delivery_report.json').read_text())
            self.assertTrue(trailer_delivery['ready'])
            self.assertTrue(social_delivery['ready'])
            reconciled_trailers = json.loads((project / '06_release/trailers/trailer_manifest.json').read_text())
            self.assertEqual(reconciled_trailers['trailers'][0]['delivery_status'], 'ready')
            reconciled_social = json.loads((project / '06_release/social/deliverables.jsonl').read_text().splitlines()[0])
            self.assertEqual(reconciled_social['delivery_status'], 'ready')
            reframe_rel = '06_release/social/masters/TRL-001-vertical.mp4'
            subprocess.run([
                sys.executable, str(ROOT / 'scripts/social_reframe.py'), str(project),
                '--input', '06_release/trailers/TRL-001/trailer.mp4', '--output', reframe_rel,
                '--width', '180', '--height', '320', '--mode', 'cover'
            ], check=True, stdout=subprocess.DEVNULL)
            self.assertEqual(social_reframe.source_dimensions(project / reframe_rel), (180, 320))
            approvals = json.loads((project / '00_project/media_approvals.json').read_text())
            self.assertTrue(approvals['groups']['TRL-001']['primary_media_id'].startswith('MEDIA-'))
            self.assertTrue(approvals['groups']['SOC-001']['primary_media_id'].startswith('MEDIA-'))

    def test_project_validator_rejects_new_nonportable_paths(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            bad_path = '/' + 'home' + '/example/private.mp4'
            (project / '00_project/media_registry.jsonl').write_text(json.dumps({
                'schema_version': 1, 'media_id': 'MEDIA-001', 'kind': 'video', 'group_id': 'SHOT-001',
                'source_ids': ['TAKE-001'], 'path': bad_path, 'status': 'candidate',
                'qc_status': 'not-checked', 'created_by': 'test', 'metadata': {}
            }) + '\n')
            proc = subprocess.run([sys.executable, str(ROOT / 'scripts/validate_story_project.py'), str(project)], text=True, stdout=subprocess.PIPE)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('path must be portable', proc.stdout)


    def test_media_toolkit_discovery_and_imagemagick_execution(self):
        data = media_toolkit.discover(deep=False)
        self.assertTrue(data['tools']['ffmpeg']['available'])
        self.assertTrue(data['tools']['ffprobe']['available'])
        self.assertIn('magick', data['tools'])
        self.assertTrue(data['tools']['magick']['available'])

        with patch.object(media_toolkit, 'which', side_effect=lambda name: {
            'convert': '/usr/bin/convert',
            'identify': '/usr/bin/identify',
        }.get(name)), patch.object(media_toolkit, 'is_imagemagick_executable', return_value=True):
            self.assertEqual(media_toolkit.tool_argv('magick', ['-version']), ['/usr/bin/convert', '-version'])
            self.assertEqual(media_toolkit.tool_argv('magick', ['identify', 'frame.png']), ['/usr/bin/identify', 'frame.png'])

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / 'result.png'
            rc = media_toolkit.raw_run('magick', ['-size', '64x64', 'xc:red', '-resize', '32x32', str(out)], root, False)
            self.assertEqual(rc, 0)
            self.assertTrue(out.is_file())
            png = out.read_bytes()
            self.assertGreaterEqual(len(png), 24)
            self.assertEqual(png[:8], b'\x89PNG\r\n\x1a\n')
            self.assertEqual(struct.unpack('>II', png[16:24]), (32, 32))
        with self.assertRaises(Exception):
            media_toolkit.guard_raw('magick', ['mogrify', '-resize', '10x10', 'a.png'], False)
        with self.assertRaises(Exception):
            media_toolkit.guard_raw('ffmpeg', ['-y', '-i', 'a.mp4', 'b.mp4'], False)

    def test_editor_project_kdenlive_and_shotcut_exports(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            timeline = {
                'schema_version': 1, 'timeline_id': 'MASTER-001', 'title': 'Editor Test',
                'video': {'width': 640, 'height': 360, 'fps': 24.0, 'pixel_format': 'yuv420p'},
                'audio_master_path': '05_post/masters/film_audio_master.wav',
                'output_path': '05_post/masters/film_master.mp4',
                'events': [
                    {'event_id': 'EVT-001', 'kind': 'video', 'path': '04_generation/video/one.mp4', 'source_in': 0.25, 'duration': 1.0},
                    {'event_id': 'EVT-002', 'kind': 'color', 'color': 'black', 'duration': 0.5},
                ],
            }
            editor = editor_project_export.derive_editor_project(timeline)
            self.assertEqual(editor_project_export.validate_editor_project(project, editor, require_sources=False), [])
            kout = project / '05_post/editorial/kdenlive/test.kdenlive'
            sout = project / '05_post/editorial/shotcut/test.mlt'
            editor_project_export.export_kdenlive(editor, kout)
            editor_project_export.export_shotcut(editor, sout)
            self.assertEqual(editor_project_export.validate_export(kout, 'kdenlive'), [])
            self.assertEqual(editor_project_export.validate_export(sout, 'shotcut'), [])
            kt = kout.read_text(encoding='utf-8')
            st = sout.read_text(encoding='utf-8')
            self.assertIn('kdenlive:docproperties.version', kt)
            self.assertIn('>1.1<', kt)
            self.assertIn('kdenlive:projectTractor', kt)
            self.assertIn('shotcut:projectAudioChannels', st)
            self.assertIn('shotcut:name', st)
            self.assertIn('>1<', st)

    def test_advanced_editor_project_preserves_mlt_filters_and_transitions(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            editor = {
                'schema_version': 1, 'project_title': 'Layered',
                'profile': {'width': 1920, 'height': 1080, 'fps': 24.0, 'progressive': True, 'colorspace': 709, 'audio_channels': 2},
                'bin': [
                    {'clip_id': 'CLIP-001', 'kind': 'video', 'path': '04_generation/video/a.mp4', 'name': 'A'},
                    {'clip_id': 'CLIP-002', 'kind': 'video', 'path': '04_generation/video/b.mp4', 'name': 'B'},
                ],
                'tracks': [
                    {'track_id': 'V1', 'name': 'Base', 'type': 'video', 'clips': [
                        {'edit_id': 'EDIT-001', 'clip_id': 'CLIP-001', 'timeline_start': 0.0, 'duration': 2.0, 'source_in': 0.0,
                         'filters': [{'service': 'brightness', 'properties': {'level': '0.1'}}]},
                    ]},
                    {'track_id': 'V2', 'name': 'Overlay', 'type': 'video', 'clips': [
                        {'edit_id': 'EDIT-002', 'clip_id': 'CLIP-002', 'timeline_start': 0.5, 'duration': 1.0, 'source_in': 0.0, 'filters': []},
                    ]},
                ],
                'transitions': [
                    {'service': 'composite', 'a_track': 'V1', 'b_track': 'V2', 'timeline_start': 0.5, 'duration': 1.0,
                     'properties': {'geometry': '0/0:100%x100%'}},
                ],
                'global_filters': [], 'markers': [], 'subtitle_file': '', 'notes': []
            }
            self.assertEqual(editor_project_export.validate_editor_project(project, editor, require_sources=False), [])
            kout = project / 'layered.kdenlive'; sout = project / 'layered.mlt'
            editor_project_export.export_kdenlive(editor, kout)
            editor_project_export.export_shotcut(editor, sout)
            for text in [kout.read_text(encoding='utf-8'), sout.read_text(encoding='utf-8')]:
                self.assertIn('<property name="mlt_service">brightness</property>', text)
                self.assertIn('<property name="mlt_service">composite</property>', text)
                self.assertIn('<property name="geometry">0/0:100%x100%</property>', text)


    def test_claim_ledger_and_campaign_lineage_validation(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            claims = [
                {'claim_id':'CLAIM-001','statement':'A verified production fact.','status':'verified','confidence':'high','sources':[{'citation':'Source A'}],'adopted':True,'used_by':['CONTENT-001']},
                {'claim_id':'CLAIM-002','statement':'An unresolved rumor.','status':'unresolved','confidence':'low','sources':[],'adopted':False,'used_by':[]},
            ]
            (project / '01_story/research/claims.jsonl').write_text('\n'.join(json.dumps(x) for x in claims) + '\n')
            (project / '06_release/social/brand_voice.json').write_text(json.dumps({
                'schema_version':1,'voice_attributes':['warm','specific'],'preferred_vocabulary':[],
                'avoid_vocabulary':[],'prohibited_claims':[]
            }, indent=2) + '\n')
            (project / '06_release/social/copy.jsonl').write_text(json.dumps({'copy_id':'COPY-001','body':'Verified fact.'}) + '\n')
            good = {'content_id':'CONTENT-001','destination':'press-kit','source_ids':['SCN-001'],'transformation':'fact-preserving summary','copy_id':'COPY-001','claim_ids':['CLAIM-001']}
            lineage = project / '06_release/social/content_lineage.jsonl'
            lineage.write_text(json.dumps(good) + '\n')
            self.assertEqual(claim_ledger.validate(claims, {'CLAIM-001'}), [])
            self.assertEqual(campaign_content.validate(project), [])
            bad = dict(good); bad['content_id']='CONTENT-002'; bad['claim_ids']=['CLAIM-002']
            lineage.write_text(json.dumps(good) + '\n' + json.dumps(bad) + '\n')
            errors = campaign_content.validate(project)
            self.assertTrue(any('non-public status' in e for e in errors))

    def test_real_edit_assist_silence_map_and_jump_cut(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            source = project / '05_post/edit_assist/source.mp4'
            source.parent.mkdir(parents=True, exist_ok=True)
            fc = '[1:a]aformat=sample_rates=48000:channel_layouts=stereo[a1];[2:a]aformat=sample_rates=48000:channel_layouts=stereo[a2];[3:a]aformat=sample_rates=48000:channel_layouts=stereo[a3];[a1][a2][a3]concat=n=3:v=0:a=1[a]'
            subprocess.run([
                'ffmpeg','-hide_banner','-loglevel','error','-y',
                '-f','lavfi','-i','color=c=blue:s=320x180:r=24:d=3',
                '-f','lavfi','-i','sine=frequency=440:duration=1:sample_rate=48000',
                '-f','lavfi','-i','anullsrc=r=48000:cl=stereo:d=1',
                '-f','lavfi','-i','sine=frequency=660:duration=1:sample_rate=48000',
                '-filter_complex',fc,'-map','0:v','-map','[a]','-t','3',
                '-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(source)
            ], check=True)
            smap = edit_assist.detect_silence(source, -35, .4)
            self.assertTrue(any(x['duration'] > .7 for x in smap['silences']))
            out = project / '05_post/edit_assist/jump.mp4'
            edit_assist.render_jump_cut(source, out, smap['keep'], 0.0)
            self.assertTrue(out.is_file())
            self.assertLess(edit_assist.media_duration(out), edit_assist.media_duration(source) - .5)

    def test_real_motion_graphics_lower_third(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            source = project / '05_post/graphics/source.mp4'; source.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','lavfi','-i','color=c=navy:s=320x180:r=24:d=1.5','-f','lavfi','-i','sine=frequency=440:duration=1.5','-shortest','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(source)], check=True)
            manifest = {
                'schema_version':1,'input':'05_post/graphics/source.mp4','output':'05_post/graphics/lower-third.mp4',
                'graphics':[{'gfx_id':'GFX-001','type':'lower-third','text':'Pippa Pebblehoof','secondary':'Short Film','start':0.2,'end':1.2,'style':{'font_size':22,'secondary_size':14}}]
            }
            self.assertEqual(motion_graphics.validate_manifest(manifest), [])
            motion_graphics.render_manifest(project, manifest)
            out = project / manifest['output']
            self.assertTrue(out.is_file())
            self.assertGreater(out.stat().st_size, 0)

    def test_remotion_adapter_scaffold_and_license_guard(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            obj={'schema_version':1,'compositions':[{'composition_id':'COMP-001','width':320,'height':180,'fps':24,'duration_frames':48,'background':'#000000','layers':[{'type':'text','text':'Title','start_frame':0,'duration_frames':48,'keyframes':[{'frame':0,'rotate_y_deg':-70,'opacity':0.0},{'frame':24,'rotate_y_deg':0,'opacity':1.0}]}]}]}
            manifest=project/'05_post/programmatic/compositions.json'; manifest.write_text(json.dumps(obj,indent=2)+'\n')
            self.assertEqual(remotion_adapter.validate(obj), [])
            out=remotion_adapter.scaffold(project,obj,'05_post/programmatic/remotion','4.0.513')
            self.assertTrue((out/'package.json').is_file())
            generated = out/'src/GeneratedComposition.tsx'
            self.assertTrue(generated.is_file())
            self.assertIn('rotateY', generated.read_text(encoding='utf-8'))
            generated.write_text('// user customization\n', encoding='utf-8')
            remotion_adapter.scaffold(project,obj,'05_post/programmatic/remotion','4.0.513')
            self.assertEqual(generated.read_text(encoding='utf-8'), '// user customization\n')
            proc=subprocess.run([sys.executable,str(ROOT/'scripts/remotion_adapter.py'),'install',str(project)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            self.assertNotEqual(proc.returncode,0)
            self.assertIn('acknowledge-license',proc.stdout)

    def test_production_document_exports_and_qc(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            d=project/'03_preproduction/documents'; d.mkdir(parents=True,exist_ok=True)
            (d/'tracker.json').write_text(json.dumps({'sheets':[{'name':'Shots','columns':['Shot','Seconds','Double'],'rows':[['SHOT-001',4,'=B4*2'],['SHOT-002',3,'=B5*2']]}]},indent=2)+'\n')
            (d/'notes.md').write_text('# Production Notes\n\n## Today\n- Check blocking\n- Verify props\n')
            manifest={'schema_version':1,'documents':[
                {'doc_id':'DOC-001','format':'xlsx','title':'Shot Tracker','data_path':'03_preproduction/documents/tracker.json','path':'03_preproduction/documents/tracker.xlsx','source_ids':['SHOT-001']},
                {'doc_id':'DOC-002','format':'docx','title':'Production Notes','content_path':'03_preproduction/documents/notes.md','path':'03_preproduction/documents/notes.docx','source_ids':[]},
                {'doc_id':'DOC-003','format':'pdf','title':'Production Notes','content_path':'03_preproduction/documents/notes.md','path':'03_preproduction/documents/notes.pdf','source_ids':[]},
            ]}
            self.assertEqual(production_documents.validate_manifest(project,manifest),[])
            results=[production_documents.render_record(project,r) for r in manifest['documents']]
            self.assertTrue(all(x['status']=='pass' for x in results))
            from openpyxl import load_workbook
            wb=load_workbook(d/'tracker.xlsx',data_only=False)
            self.assertTrue(str(wb['Shots']['C4'].value).startswith('='))
            self.assertTrue((d/'notes.docx').is_file())
            for name in ['tracker.md','notes.md']:
                self.assertTrue((d/name).is_file())
            self.assertTrue((d/'tracker.md').read_text(encoding='utf-8').strip())
            self.assertEqual(pdf_toolkit.info(d/'notes.pdf')['pages'],1)
            self.assertEqual(document_companions.audit(project), [])

    def test_pdf_toolkit_merge_render_and_optional_mutool(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); text='# One\n\nFirst PDF.'
            a=root/'a.pdf'; b=root/'b.pdf'
            production_documents.render_pdf('A',text,a); production_documents.render_pdf('B',text,b)
            merged=root/'merged.pdf'; pdf_toolkit.merge([a,b],merged)
            self.assertEqual(pdf_toolkit.info(merged)['pages'],2)
            rendered=pdf_toolkit.render(merged,root/'page',72)
            self.assertEqual(len(rendered),2)
            self.assertTrue(all(Path(x).is_file() for x in rendered))
            discovery=pdf_toolkit.discover()
            self.assertTrue(discovery['tools']['pypdf']['available'])
            if not discovery['tools']['mutool']['available']:
                with self.assertRaises(Exception):
                    pdf_toolkit.clean(merged,root/'clean.pdf')

    def test_work_units_frontier_and_decision_map(self):
        with tempfile.TemporaryDirectory() as td:
            project=Path(td)/'film'
            subprocess.run([sys.executable,str(ROOT/'scripts/init_story_project.py'),str(project)],check=True,stdout=subprocess.DEVNULL)
            units={'schema_version':1,'units':[
                {'unit_id':'UNIT-001','title':'Lock story intent','status':'ready','blocked_by':[],'source_ids':[],'acceptance_criteria':['Intent approved']},
                {'unit_id':'UNIT-002','title':'Build generation package','status':'ready','blocked_by':['UNIT-001'],'source_ids':['UNIT-001'],'acceptance_criteria':['Batch validates']},
            ]}
            work_units.save(project,units)
            self.assertEqual([u['unit_id'] for u in work_units.frontier(work_units.load(project))],['UNIT-001'])
            subprocess.run([sys.executable,str(ROOT/'scripts/work_units.py'),'set-status',str(project),'--unit','UNIT-001','--status','complete'],check=True,stdout=subprocess.DEVNULL)
            self.assertEqual([u['unit_id'] for u in work_units.frontier(work_units.load(project))],['UNIT-002'])
            dm={'schema_version':1,'destination':'A locked film production plan','notes':[],'decisions':[
                {'decision_id':'DEC-001','title':'Audience','question':'Who is it for?','status':'open','prerequisites':[]},
                {'decision_id':'DEC-002','title':'Ending','question':'What ending shape?','status':'open','prerequisites':['DEC-001']},
            ],'not_yet_specified':['Exact trailer structure'],'out_of_scope':[]}
            decision_map.save(project,dm)
            self.assertEqual([d['decision_id'] for d in decision_map.frontier(decision_map.load(project))],['DEC-001'])
            subprocess.run([sys.executable,str(ROOT/'scripts/decision_map.py'),'resolve',str(project),'--decision','DEC-001','--resolution','Family audience'],check=True,stdout=subprocess.DEVNULL)
            self.assertEqual([d['decision_id'] for d in decision_map.frontier(decision_map.load(project))],['DEC-002'])

    def test_rich_document_companion_gate(self):
        with tempfile.TemporaryDirectory() as td:
            project=Path(td)/'film'
            subprocess.run([sys.executable,str(ROOT/'scripts/init_story_project.py'),str(project)],check=True,stdout=subprocess.DEVNULL)
            out=project/'06_release/documents/example.pdf'; out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(b'%PDF-test')
            proc=subprocess.run([sys.executable,str(ROOT/'scripts/validate_story_project.py'),str(project)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            self.assertNotEqual(proc.returncode,0)
            self.assertIn('Markdown companion',proc.stdout)
            (out.with_suffix('.md')).write_text('# Example\n\nHuman-readable equivalent.\n',encoding='utf-8')
            proc=subprocess.run([sys.executable,str(ROOT/'scripts/validate_story_project.py'),str(project)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            self.assertEqual(proc.returncode,0,proc.stdout)

    def test_guided_wizard_always_has_markdown(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); spec=root/'wizard.json'; out=root/'prepare.sh'
            spec.write_text(json.dumps({'schema_version':1,'title':'Production Access','purpose':'Human-only setup','stages':[{'title':'Approve access','instructions':['Open the approved local tool and confirm access.'],'verification':'Access is visible','irreversible':False}]},indent=2)+'\n')
            subprocess.run([sys.executable,str(ROOT/'scripts/guided_wizard.py'),str(spec),'--out',str(out)],check=True,stdout=subprocess.DEVNULL)
            self.assertTrue(out.is_file()); self.assertTrue(out.with_suffix('.md').is_file())
            subprocess.run(['bash','-n',str(out)],check=True)

    def test_resource_safe_comfyui_batch_runs_without_llm(self):
        with tempfile.TemporaryDirectory() as td, FakeComfyServer() as srv:
            FakeComfyHandler.free_requests=[]; FakeComfyHandler.upload_requests=[]
            project=Path(td)/'film'
            subprocess.run([sys.executable,str(ROOT/'scripts/init_story_project.py'),str(project)],check=True,stdout=subprocess.DEVNULL)
            inp=project/'04_generation/comfyui/inputs/reference.png'; inp.parent.mkdir(parents=True,exist_ok=True); inp.write_bytes(b'prepared-reference')
            wf={'1':{'class_type':'LoadTest','inputs':{'image':'placeholder.png'}},'2':{'class_type':'SaveTest','inputs':{'data':['1',0]}}}
            wfp=project/'04_generation/comfyui/workflows/JOB-001.json'; wfp.parent.mkdir(parents=True,exist_ok=True); wfp.write_text(json.dumps(wf))
            batch={'schema_version':1,'batch_id':'BATCH-001','status':'prepared','sequential':True,'uploads':[{'upload_id':'UP-001','path':'04_generation/comfyui/inputs/reference.png','type':'input'}],'jobs':[{'job_id':'JOB-001','source_ids':['SHOT-001'],'workflow':'04_generation/comfyui/workflows/JOB-001.json','patches':[{'node':'1','input':'image','upload_id':'UP-001'}],'blocked_by':[],'output_dir':'04_generation/comfyui/outputs/JOB-001','timeout_s':2,'poll_interval_s':0.01,'max_transient_retries':0}]}
            bp=project/'04_generation/comfyui/offline_batch.json'; bp.write_text(json.dumps(batch,indent=2)+'\n')
            policy=json.loads((project/'00_project/resource_policy.json').read_text())
            policy['local_llm']={'adapter':'command','unload_command':[sys.executable,'-c','pass'],'reload_command':[sys.executable,'-c','pass'],'health_command':[sys.executable,'-c','pass'],'health_url':'','unload_timeout_s':10,'reload_timeout_s':10,'health_timeout_s':10}
            policy['comfyui']['url']=srv.url; policy['comfyui']['free_settle_s']=0; policy['comfyui']['queue_drain_timeout_s']=2; policy['exclusive_generation']['release_timeout_s']=2
            (project/'00_project/resource_policy.json').write_text(json.dumps(policy,indent=2)+'\n')
            state=resource_handoff.arm(project,'04_generation/comfyui/offline_batch.json',srv.url,detach=False)
            self.assertEqual(state['phase'],'waiting-for-agent-end')
            staged=json.loads(bp.read_text()); self.assertEqual(staged.get('preflight',{}).get('status'),'pass'); self.assertEqual(staged['staged_uploads']['UP-001']['name'],'uploaded.png'); self.assertEqual(len(FakeComfyHandler.upload_requests),1)
            (project/'00_project/resource_handoff.release').write_text('go\n')
            self.assertEqual(resource_handoff.daemon(project),0)
            final=json.loads((project/'00_project/resource_handoff.json').read_text())
            self.assertEqual(final['phase'],'complete'); self.assertEqual(final['llm_state'],'ready'); self.assertEqual(final['comfyui_state'],'unloaded')
            self.assertTrue((project/'00_project/RESOURCE_RESUME.md').is_file())
            self.assertTrue((project/'04_generation/comfyui/offline_batch_result.json').is_file())
            self.assertTrue(any(x.get('unload_models') and x.get('free_memory') for x in FakeComfyHandler.free_requests)); self.assertEqual(len(FakeComfyHandler.upload_requests),1)


    def test_skill_frontmatter_uses_strict_yaml_rules(self):
        bad = "---\nname: bad-example\ndescription: Unsafe scalar: this must be quoted\n---\n"
        with self.assertRaises(ValueError):
            validate_skills.frontmatter(bad)
        good = "---\nname: good-example\ndescription: \"Safe scalar: quoted\"\n---\n"
        parsed = validate_skills.frontmatter(good)
        self.assertEqual(parsed['name'], 'good-example')

    def test_llm_runtime_loopback_is_local_and_external_guard_blocks_misclassification(self):
        local = llm_runtime.classify_endpoint('http://127.0.0.1:8080')
        self.assertEqual(local['location'], 'local')
        local6 = llm_runtime.classify_endpoint('http://[::1]:8080')
        self.assertEqual(local6['location'], 'local')
        unknown = llm_runtime.classify_endpoint('https://example.invalid/v1')
        self.assertEqual(unknown['location'], 'unknown')
        with self.assertRaises(ValueError):
            resource_handoff.validate_llm_policy({'local_llm': {
                'adapter': 'external',
                'runtime_location': 'external',
                'endpoint': 'http://127.0.0.1:8080',
                'location_evidence': ['Assumed cloud because API is OpenAI-compatible.'],
            }})
        with self.assertRaises(ValueError):
            resource_handoff.validate_llm_policy({'local_llm': {
                'adapter': 'external',
                'runtime_location': 'unknown',
                'endpoint': '',
                'location_evidence': [],
            }})
        self.assertEqual(resource_handoff.validate_llm_policy({'local_llm': {
            'adapter': 'external',
            'runtime_location': 'external',
            'endpoint': 'https://api.example.invalid/v1',
            'location_evidence': ['User explicitly confirmed that this endpoint runs on another machine.'],
        }}), 'external')

    def test_resource_handoff_requires_declared_llm_lifecycle(self):
        with tempfile.TemporaryDirectory() as td, FakeComfyServer() as srv:
            project=Path(td)/'film'
            subprocess.run([sys.executable,str(ROOT/'scripts/init_story_project.py'),str(project)],check=True,stdout=subprocess.DEVNULL)
            wf={'1':{'class_type':'TestNode','inputs':{'choice':'a','value':1}},'2':{'class_type':'SaveTest','inputs':{'data':['1',0]}}}
            p=project/'04_generation/comfyui/workflows/test.json';p.write_text(json.dumps(wf))
            batch={'schema_version':1,'batch_id':'BATCH-001','status':'prepared','sequential':True,'uploads':[],'jobs':[{'job_id':'JOB-001','workflow':'04_generation/comfyui/workflows/test.json','patches':[],'blocked_by':[],'output_dir':'04_generation/comfyui/outputs/test'}]}
            (project/'04_generation/comfyui/offline_batch.json').write_text(json.dumps(batch))
            policy=json.loads((project/'00_project/resource_policy.json').read_text());policy['comfyui']['url']=srv.url;(project/'00_project/resource_policy.json').write_text(json.dumps(policy))
            with self.assertRaises(ValueError): resource_handoff.arm(project,'04_generation/comfyui/offline_batch.json',srv.url,detach=False)

    def test_video_model_selection_defaults_to_h3_and_blocks_silent_ltx(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            prefs = model_preferences.load(project)
            video = prefs['processes']['video_generation']
            self.assertEqual(video['selected_adapter'], 'minimax-h3')
            self.assertEqual(model_preferences.validate(prefs), [])
            video['selected_adapter'] = 'ltx-2-5'
            video['selection_source'] = 'default'
            video['user_confirmed'] = False
            self.assertTrue(any('non-default' in e for e in model_preferences.validate(prefs)))
            (project / '04_generation/shot_briefs.jsonl').write_text(json.dumps({'shot_id':'SHOT-001','scene_id':'SCN-001','target_model':'ltx-2-5'}) + '\n', encoding='utf-8')
            check = subprocess.run([sys.executable, str(ROOT / 'scripts/validate_story_project.py'), str(project)], text=True, capture_output=True)
            self.assertNotEqual(check.returncode, 0)
            self.assertIn('target_model', check.stdout + check.stderr)
            self.assertIn('minimax-h3', check.stdout + check.stderr)
            (project / '04_generation/shot_briefs.jsonl').unlink()
            subprocess.run([sys.executable, str(ROOT / 'scripts/model_preferences.py'), 'set-video', str(project), 'ltx-2-5', '--source', 'user'], check=True, stdout=subprocess.DEVNULL)
            chosen = model_preferences.load(project)['processes']['video_generation']
            self.assertEqual(chosen['selected_adapter'], 'ltx-2-5')
            self.assertEqual(chosen['selection_source'], 'user')
            self.assertTrue(chosen['user_confirmed'])
            subprocess.run([sys.executable, str(ROOT / 'scripts/model_preferences.py'), 'reset-video', str(project)], check=True, stdout=subprocess.DEVNULL)
            reset = model_preferences.load(project)['processes']['video_generation']
            self.assertEqual(reset['selected_adapter'], 'minimax-h3')

    def test_comfyui_model_inventory_and_per_process_resource_selection(self):
        with tempfile.TemporaryDirectory() as td, FakeComfyServer() as srv:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            inventory = model_inventory.scan(project, srv.url)
            self.assertIn('vae', inventory['folders'])
            self.assertIn('text_encoders', inventory['folders'])
            self.assertIn('loras', inventory['folders'])
            self.assertIn('upscale_models', inventory['folders'])
            self.assertIn('unet', inventory['folders'])
            self.assertIn('qwen-image-2512-Q4_K_M.gguf', inventory['folders']['unet']['models'])
            self.assertTrue(any(row.get('key') == 'node:CustomModelLoader:model_name' for row in inventory['node_choices']))
            summary = model_inventory.inventory_summary(inventory)
            self.assertIn('unet', summary['primary_weight_models'])
            self.assertIn('diffusion_models', summary['primary_weight_models'])
            qwen = model_inventory.search_inventory(inventory, 'qwen image 2512')
            self.assertTrue(any(row['name'] == 'qwen-image-2512-Q4_K_M.gguf' for row in qwen['matches']))
            self.assertIn('unet', model_preferences.PROCESS_SPECS['image_generation']['resource_folders'])
            menu = model_inventory.render_menu(project, inventory, 'video_generation')
            self.assertIn('minimax-h3', menu)
            self.assertIn('h3-vae.safetensors', menu)
            self.assertIn('camera-motion.safetensors', menu)
            self.assertIn('custom-node-model.safetensors', menu)

            prefs = model_preferences.load(project)
            self.assertEqual(prefs['schema_version'], 2)
            self.assertEqual(prefs['processes']['video_generation']['selected_adapter'], 'minimax-h3')
            self.assertIsNone(prefs['processes']['image_generation']['selected_adapter'])

            model_preferences.cmd_set_resource(project, 'video_generation', 'diffusion_models', ['h3-video.safetensors'], None)
            model_preferences.cmd_set_resource(project, 'video_generation', 'vae', ['h3-vae.safetensors'], None)
            model_preferences.cmd_set_resource(project, 'video_generation', 'text_encoders', ['clip-l.safetensors', 't5xxl.safetensors'], None)
            model_preferences.cmd_add_lora(project, 'video_generation', 'camera-motion.safetensors', None, 0.8, 0.7)
            self.assertEqual(model_preferences.validate(model_preferences.load(project), inventory), [])

            model_preferences.cmd_set_adapter(project, 'video_generation', 'ltx-2-5', 'user', '')
            model_preferences.cmd_set_resource(project, 'video_generation', 'vae', ['ltx-vae.safetensors'], None)
            ltx = model_preferences.load(project)
            self.assertEqual(ltx['processes']['video_generation']['profiles']['minimax-h3']['resources']['vae'], ['h3-vae.safetensors'])
            self.assertEqual(ltx['processes']['video_generation']['profiles']['ltx-2-5']['resources']['vae'], ['ltx-vae.safetensors'])

            model_preferences.cmd_set_adapter(project, 'image_generation', 'qwen-image-2512', 'user', '')
            model_preferences.cmd_set_resource(project, 'image_generation', 'diffusion_models', ['qwen-image.safetensors'], None)
            chosen = model_preferences.load(project)
            self.assertEqual(chosen['processes']['image_generation']['selected_adapter'], 'qwen-image-2512')

            broken = model_preferences.load(project)
            broken['processes']['image_generation']['profiles']['qwen-image-2512']['resources']['vae'] = ['missing-vae.safetensors']
            self.assertTrue(any('missing-vae.safetensors' in e for e in model_preferences.validate(broken, inventory)))

            legacy = {'schema_version': 1, 'video': {'default_model':'minimax-h3','selected_model':'ltx-2-5','selection_source':'user','user_confirmed':True,'allow_agent_substitution':False,'shot_overrides':{}}}
            migrated = model_preferences.normalize(legacy)
            self.assertEqual(migrated['schema_version'], 2)
            self.assertEqual(migrated['processes']['video_generation']['selected_adapter'], 'ltx-2-5')

    def test_comfyui_external_model_paths_use_server_registry_not_filesystem_scan(self):
        with tempfile.TemporaryDirectory() as td, FakeComfyServer() as srv:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            inventory = model_inventory.scan(project, srv.url)
            self.assertEqual(inventory['discovery_method'], 'comfyui-model-registry')
            self.assertEqual(inventory['registry_endpoints'], ['/models', '/models/{folder}'])
            self.assertFalse(inventory['filesystem_scan_used'])
            self.assertTrue(inventory['external_model_paths_supported'])
            self.assertGreater(inventory['resource_count'], 0)
            self.assertEqual(model_inventory.registry_warnings({'checkpoints': {'models': []}})[0].split('.')[0], 'ComfyUI returned model folder categories but no model filenames')
            md = (project / '00_project/comfyui_model_inventory.md').read_text(encoding='utf-8')
            self.assertIn('extra_model_paths.yaml', md)
            self.assertIn('does not scan the local filesystem', md)

        setup_skill = (ROOT / 'skills/generation-model-setup/SKILL.md').read_text(encoding='utf-8')
        discover_skill = (ROOT / 'skills/comfyui-discover/SKILL.md').read_text(encoding='utf-8')
        extension = (ROOT / 'extensions/story-film-progress/index.ts').read_text(encoding='utf-8')
        for token in ['extra_model_paths.yaml', '/models', 'Do not run `find /`']:
            self.assertIn(token, setup_skill)
        self.assertIn('input.required', discover_skill)
        self.assertIn('comfyModelFilesystemScanBlockReason', extension)
        self.assertIn('model_inventory.py scan', extension)
        self.assertIn('rawRegistryEndpoint', extension)
        self.assertIn('Do not write or run one-off curl/wget/Python parsers', extension)
        self.assertIn('Do not replace it with direct `curl`', setup_skill)

    def test_screenplay_consistency_uses_canon_not_hardcoded_names(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_story_project.py'), str(project)], check=True, stdout=subprocess.DEVNULL)
            canon = json.loads((project / '00_project/canon.json').read_text())
            canon['characters'] = {
                'CHAR-001': {'name': 'Elias Ruhn'},
                'CHAR-002': {'name': 'Mara Voss'},
                'CHAR-003': {'name': 'Zhara Nix', 'screenplay_names': ['ZHARA']},
            }
            (project / '00_project/canon.json').write_text(json.dumps(canon, indent=2) + '\n')
            fountain = (
                'INT. WORKSHOP - NIGHT\n\n'
                'ELIAS\nYour last job.\n\n'
                'MARA\nSeven o\'clock.\n\n'
                'ZHARA\nThe gate is open.\n'
            )
            (project / '02_screenplay/screenplay.fountain').write_text(fountain, encoding='utf-8')
            rows = [
                {'line_id': 'LINE-001', 'scene_id': 'SCN-001', 'order': 1, 'kind': 'dialogue', 'character_id': 'CHAR-001', 'text': 'Your last job.'},
                {'line_id': 'LINE-002', 'scene_id': 'SCN-001', 'order': 2, 'kind': 'dialogue', 'character_id': 'CHAR-002', 'text': "Seven o'clock."},
                {'line_id': 'LINE-003', 'scene_id': 'SCN-001', 'order': 3, 'kind': 'dialogue', 'character_id': 'CHAR-003', 'text': 'The gate is open.'},
            ]
            (project / '02_screenplay/line_manifest.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows), encoding='utf-8')
            self.assertEqual(screenplay_consistency.validate_project(project), [])

            bad = fountain.replace('ELIAS\n', 'EILIAS\n', 1)
            (project / '02_screenplay/screenplay.fountain').write_text(bad, encoding='utf-8')
            errors = screenplay_consistency.validate_project(project)
            joined = '\n'.join(errors)
            self.assertIn("unknown dialogue cue 'EILIAS'", joined)
            self.assertIn("did you mean 'ELIAS'", joined)
            self.assertNotIn('hardcoded', joined.lower())

    def test_project_validator_checks_graphics_compositions_and_documents(self):
        with tempfile.TemporaryDirectory() as td:
            project=Path(td)/'film'
            subprocess.run([sys.executable,str(ROOT/'scripts/init_story_project.py'),str(project)],check=True,stdout=subprocess.DEVNULL)
            (project/'05_post/graphics/graphics.json').write_text(json.dumps({'schema_version':1,'input':'x.mp4','output':'y.mp4','graphics':[{'gfx_id':'GFX-001','type':'text','text':'Title'}]},indent=2)+'\n')
            (project/'05_post/programmatic/compositions.json').write_text(json.dumps({'schema_version':1,'compositions':[{'composition_id':'COMP-001','width':320,'height':180,'fps':24,'duration_frames':24,'layers':[{'type':'text','text':'Title'}]}]},indent=2)+'\n')
            (project/'06_release/artwork/design_system.json').write_text(json.dumps({'schema_version':1,'visual_concept':'restrained handmade geometry','source_refs':[],'asset_paths':[],'safe_zones':{'title':0.08}},indent=2)+'\n')
            proc=subprocess.run([sys.executable,str(ROOT/'scripts/validate_story_project.py'),str(project)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            self.assertEqual(proc.returncode,0,proc.stdout)
            bad=json.loads((project/'05_post/programmatic/compositions.json').read_text()); bad['compositions'][0]['composition_id']='BAD-001'
            (project/'05_post/programmatic/compositions.json').write_text(json.dumps(bad))
            proc=subprocess.run([sys.executable,str(ROOT/'scripts/validate_story_project.py'),str(project)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            self.assertNotEqual(proc.returncode,0)
            self.assertIn('COMP-###',proc.stdout)

    def test_comfyui_workflow_catalog_reuses_existing_sources_and_rejects_guesses(self):
        workflow = {
            '1': {'class_type': 'TestNode', 'inputs': {'choice': 'a', 'value': 3}},
            '2': {'class_type': 'SaveTest', 'inputs': {'data': ['1', 0]}},
        }
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / 'film'
            workflows = project / '04_generation/comfyui/workflows'
            templates = project / '04_generation/comfyui/templates'
            workflows.mkdir(parents=True)
            templates.mkdir(parents=True)
            (workflows / 'local.json').write_text(json.dumps(workflow), encoding='utf-8')
            client = comfyui_control.Client('http://127.0.0.1:1')
            with patch.object(client, 'user_workflows', return_value=[
                {'source': 'user', 'name': 'saved.json', 'path': 'workflows/saved.json'}
            ]), patch.object(client, 'template_catalog', return_value=([
                {'source': 'core', 'name': 'core-image'},
                {'source': 'custom', 'module': 'CustomPack', 'name': 'custom-example'},
            ], [])):
                catalog = client.workflow_catalog(project)
            self.assertEqual(
                [x['source'] for x in catalog['workflows'][:4]],
                ['project-workflow', 'user', 'core', 'custom'],
            )
            with patch.object(client, '_get_first', return_value=workflow):
                self.assertEqual(client.fetch_workflow_source('user', 'saved.json'), workflow)
                self.assertEqual(client.fetch_workflow_source('custom', 'custom-example', module='CustomPack'), workflow)
            with patch.object(client, 'get', return_value={'nodes': [{'id': 1, 'type': 'TestNode'}], 'links': []}):
                core = client.fetch_workflow_source('core', 'core-image')
            self.assertEqual(comfyui_workflow.detect_format(core), 'ui')
            with self.assertRaises(ValueError):
                client.fetch_workflow_source('core', '../escape')
        with FakeComfyServer() as srv:
            guessed = {'1': {'class_type': 'QwenImageTextToImageApi', 'inputs': {}}}
            verdict = comfyui_control.Client(srv.url).validate_workflow(guessed)
            self.assertFalse(verdict['valid'])
            self.assertTrue(any('not installed' in item for item in verdict['errors']))

if __name__ == '__main__':
    unittest.main()
