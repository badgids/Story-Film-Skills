from __future__ import annotations
import json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/'scripts'
if str(SCRIPTS) not in sys.path: sys.path.insert(0,str(SCRIPTS))
import minimax_h3_prompt_validator as v
import minimax_h3_skill_router as r

class Tests(unittest.TestCase):
    def test_style_skills_rejoin_h3_stack(self):
        for name in r.STYLE_SKILLS:
            text=(ROOT/'skills'/name/'SKILL.md').read_text()
            self.assertIn('h3-prompt-writing',text,name)
            self.assertIn('minimax-h3',text,name)
            self.assertIn('minimax_h3_prompt_validator.py',text,name)
            self.assertIn('prompt-qc',text,name)
        p=(ROOT/'skills/story-film/playbooks/generation-prompts.md').read_text()
        self.assertIn('automatically run the Story-Film H3 stack',p)
        self.assertIn('minimax_h3_prompt_validator.py',p)

    def test_prompt_validator(self):
        t='integrated_multimodal_description: [Shot 1] A woman (S1) says: <d>[English] Hello.</d>\n\noverall_soundscape: Rain.\n\nnon_diegetic_music: N/A\n'
        self.assertEqual(v.validate(t,'T2VA',6.0),[])
        self.assertTrue(v.validate(t.replace('overall_soundscape:','soundscape:'),'T2VA',6.0))
        i='For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.\n\nintegrated_multimodal_description: [Shot 1] Start from the supplied image. [Shot 2] At 00:03.000, the camera cuts closer.\n\noverall_soundscape: Room tone.\n\nnon_diegetic_music: N/A\n'
        self.assertEqual(v.validate(i,'I2VA',6.0),[])
        f='How the reference pictures align with the target video - Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the 8.00-second mark of the target video.\n\nintegrated_multimodal_description: [Shot 1] Move continuously between anchors.\n\noverall_soundscape: Fabric.\n\nnon_diegetic_music: N/A\n'
        self.assertEqual(v.validate(f,'FL2VA',8.0),[])
        l='How the reference pictures align with the target video - <Picture 1> (from [Shot 1]) aligns with the 6.00-second mark of the target video.\n\nintegrated_multimodal_description: [Shot 1] Converge on the final frame.\n\noverall_soundscape: Footsteps.\n\nnon_diegetic_music: N/A\n'
        self.assertEqual(v.validate(l,'L2VA',6.0),[])
        ref='subject_definitions:\n<Subject 1> is the performer in <Picture 1>.\n<Picture 1> is the composition anchor.\n<Audio 1> is approved vocal audio for <Subject 1> (S1).\n\nsummary:\n[reference generation + audio reference] <Subject 1> performs from <Picture 1>.\n\nretention_analysis:\n<Subject 1>: fully_preserved - identity.\n<Picture 1>: fully_preserved - composition.\n<Audio 1>: reference - timing.\n\ndetailed_description:\nCinematic live action.\n[Shot 1] <Subject 1> (S1) says: <d>[English] Hello.</d> while <Audio 1> controls timing.\n\noverall_soundscape:\nRoom tone.\n\nnon_diegetic_music:\nN/A\n'
        self.assertEqual(v.validate(ref,'Ref2VA',6.0),[])

    def test_exact_audio_and_custom_nodes_preserved(self):
        deps=json.loads((ROOT/'references/comfyui_workflow_dependencies.json').read_text())['packages']
        for key in ('comfyui-h3-exact-audio-lock','comfyui-orbitsheets','videohelpersuite','comfyui-gguf','qwen3-tts-flybird','nvidia-rtx-nodes','comfyui-vlm-nodes'):
            self.assertIn(key,deps)
        c=json.loads((ROOT/'references/comfyui_workflow_contracts.json').read_text())['contracts']['minimax-h3-r2v-exact-audio']
        for node in ('MiniMaxH3ReferenceToVideo','MiniMaxH3TimedAudio','MiniMaxH3ExactAudioLock','MiniMaxH3AddGuide','SaveVideo','VHS_LoadVideo'):
            self.assertIn(node,c['required_node_classes'])
        wf=json.loads((ROOT/'comfyui_workflows/video/MiniMax-H3/video_minimax_h3_r2v_exact_audio_hybrid.json').read_text())
        types={n.get('type') for n in wf.get('nodes',[])}
        for node in ('MiniMaxH3ReferenceToVideo','MiniMaxH3TimedAudio','MiniMaxH3ExactAudioLock','MiniMaxH3AddGuide'):
            self.assertIn(node,types)
        m=(ROOT/'skills/minimax-h3/SKILL.md').read_text()
        self.assertIn('selected workflow uses `MiniMaxH3ExactAudioLock`',m)
        self.assertIn('must not replace that path',m)
        self.assertIn('Do not impose an artificial speaker or utterance count',m)

if __name__=='__main__':
    unittest.main()
