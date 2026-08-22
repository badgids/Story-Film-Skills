# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
import json,tempfile,unittest,wave
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import reference_authority,temporal_continuity,dialogue_audio_authority,comfy_binding_audit,reference_sheets,staged_grounding,dialogue_timing_preflight,comfy_workflow_contracts
class Tests(unittest.TestCase):
 def test_reference_authority(self):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td);p=r/'03_preproduction/references/reference_manifest.json';p.parent.mkdir(parents=True);p.write_text(json.dumps({'references':[{'ref_id':'REF-001','authority_scopes':['character-identity'],'must_not_control':['camera'],'atlas':{'layout_is_reference_only':True}}]}));self.assertEqual(reference_authority.validate_project(r),[])
 def test_temporal_tail_requires_strip(self):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td);p=r/'04_generation/temporal_continuity.jsonl';p.parent.mkdir(parents=True);p.write_text(json.dumps({'temporal_tail':{'duration_seconds':2,'audio_policy':'keep'}})+'\n');self.assertTrue(temporal_continuity.validate_project(r))
 def test_audio_hash_and_authority(self):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td);a=r/'a.wav';
   with wave.open(str(a),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(b'\0\0'*8000)
   import hashlib;h=hashlib.sha256(a.read_bytes()).hexdigest();p=r/'04_generation/dialogue_audio_authority.jsonl';p.parent.mkdir(parents=True);p.write_text(json.dumps({'line_id':'LINE-001','speaker_id':'CHAR-001','approved_audio_media_id':'MEDIA-001','path':'a.wav','audio_sha256':h,'start_seconds':0,'visible_sync_required':True,'generation_audio_authority':'approved-dialogue','review_audio_authority':'approved-dialogue'})+'\n');self.assertEqual(dialogue_audio_authority.validate_project(r),[])
 def test_binding_audit(self):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td);wf=r/'04_generation/comfyui/workflows/a.json';wf.parent.mkdir(parents=True);wf.write_text(json.dumps({'1':{'class_type':'LoadImage','inputs':{}}}));p=r/'04_generation/comfyui/reference_bindings.jsonl';p.write_text(json.dumps({'workflow':'04_generation/comfyui/workflows/a.json','node_id':'1','node_type':'LoadImage','ref_id':'REF-001'})+'\n');self.assertEqual(comfy_binding_audit.validate_project(r),[])
 def test_reference_sheet_functional_view(self):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td);p=r/'03_preproduction/references/reference_sheet_plans.json';p.parent.mkdir(parents=True);p.write_text(json.dumps({'plans':[{'sheet_type':'prop-reference','subject_id':'PROP-001','required_views':['front'],'functional_views':['latch']}]}));self.assertEqual(reference_sheets.validate_project(r),[])
 def test_staged_grounding_order(self):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td);p=r/'03_preproduction/storyboards/grounding_passes.jsonl';p.parent.mkdir(parents=True);p.write_text(json.dumps({'target_id':'SHOT-001','stage':'composition','prompt':'layout','reference_bindings':[],'authority_scopes':['frame-zero-composition']})+'\n'+json.dumps({'target_id':'SHOT-001','stage':'identity','prompt':'identity','reference_bindings':[{'ref_id':'REF-001'}],'authority_scopes':['character-identity']})+'\n');self.assertEqual(staged_grounding.validate_project(r),[])
 def test_dialogue_timing_overflow(self):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td);a=r/'line.wav';
   with wave.open(str(a),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(b'\0\0'*16000)
   p=r/'04_generation/dialogue_timing_plan.json';p.parent.mkdir(parents=True);p.write_text(json.dumps({'clips':[{'duration_seconds':1,'lines':[{'line_id':'LINE-001','path':'line.wav','start_seconds':0}]}]}));self.assertTrue(dialogue_timing_preflight.validate_project(r))
 def test_contract_database_and_sanitized_blueprints(self):
  db=comfy_workflow_contracts.load_contracts();self.assertIn('minimax-h3-r2v-exact-audio',db['contracts']);
  for p in (ROOT/'references/comfyui_workflows').glob('*.json'):
   text=p.read_text();json.loads(text);self.assertNotIn('Pippa',text);self.assertNotIn('Pebblehoof',text);self.assertNotRegex(text,r'[A-Za-z]:\\Users\\|/home/[^/ ]+/')
  deps=comfy_workflow_contracts.load_dependencies();self.assertIn('comfyui-h3-exact-audio-lock',deps['packages']);self.assertIn('videohelpersuite',deps['packages']);self.assertIn('comfyui-gguf',deps['packages'])
  pairs={'video_minimax_h3_t2v.json':'minimax-h3-t2v','video_minimax_h3_i2v.json':'minimax-h3-i2v','video_minimax_h3_r2v.json':'minimax-h3-r2v','video_minimax_h3_r2v_exact_audio_hybrid.json':'minimax-h3-r2v-exact-audio','CharacterTurnaroundSheetH3.json':'character-reference-sheet','LocationOrbitSheetH3.json':'location-reference-sheet','PropReferenceSheetH3.json':'prop-reference-sheet','FrameInterpolationFILM.json':'film-frame-interpolation','RTX_SR_Upscaler_Video_reference.json':'rtx-video-upscale','qwen3_tts_flybird.json':'qwen3-tts-flybird','audio_stable_audio_3_sfx.json':'stable-audio-sfx','audio_minimax_music_3.json':'minimax-music-api'}
  for name,cid in pairs.items(): self.assertEqual(comfy_workflow_contracts.validate(ROOT/'references/comfyui_workflows'/name,db['contracts'][cid]),[],name)
if __name__=='__main__':unittest.main()
