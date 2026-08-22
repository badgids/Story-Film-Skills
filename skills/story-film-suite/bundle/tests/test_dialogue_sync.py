import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import dialogue_sync


class DialogueSyncTests(unittest.TestCase):
    def base_project(self, td):
        root = Path(td)
        for rel in ["00_project", "02_screenplay", "03_preproduction/references", "04_generation"]:
            (root / rel).mkdir(parents=True, exist_ok=True)
        canon = {"characters": {"CHAR-001": {"name": "Mara"}}, "props": {"PROP-001": {"name": "Key"}}}
        (root / "00_project/canon.json").write_text(json.dumps(canon), encoding="utf-8")
        (root / "03_preproduction/references/reference_manifest.json").write_text(json.dumps({"references": [{"ref_id": "REF-001", "role": "last frame"}]}), encoding="utf-8")
        (root / "02_screenplay/line_manifest.jsonl").write_text(json.dumps({"line_id": "LINE-001", "scene_id": "SCN-001", "kind": "dialogue", "character_id": "CHAR-001", "text": "Stay here."}) + "\n", encoding="utf-8")
        return root

    def write_valid(self, root):
        sync = {"line_id": "LINE-001", "speaker_id": "CHAR-001", "required": True, "mouth_visibility": "required", "cut_policy": "hold-through-line", "timing_source": "measured-speech", "speech_duration_s": 1.2, "occlusion_constraints": ["mouth unobstructed"]}
        shot = {"shot_id": "SHOT-001", "scene_id": "SCN-001", "line_ids": ["LINE-001"], "subjects": ["CHAR-001"], "duration_seconds": 2.0, "lip_sync": [sync], "end_frame": {"required": True, "subjects": [{"subject_id": "CHAR-001", "state": "still"}], "props": [{"prop_id": "PROP-001", "state": "held"}], "reference_id": "REF-001"}}
        (root / "04_generation/shot_briefs.jsonl").write_text(json.dumps(shot) + "\n", encoding="utf-8")
        shooting = {"scenes": [{"scene_id": "SCN-001", "units": [{"line_id": "LINE-001", "kind": "dialogue", "speaker": "CHAR-001", "text": "Stay here.", "shot_ids": ["SHOT-001"], "lip_sync": [sync]}]}]}
        (root / "03_preproduction/shooting_script.json").write_text(json.dumps(shooting), encoding="utf-8")

    def test_valid_visible_dialogue_and_end_frame_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.base_project(td)
            self.write_valid(root)
            self.assertEqual(dialogue_sync.validate_project(root), [])
            report = dialogue_sync.build_coverage(root)
            self.assertTrue(report["lip_sync_ready"])

    def test_wrong_speaker_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.base_project(td)
            self.write_valid(root)
            shot = json.loads((root / "04_generation/shot_briefs.jsonl").read_text())
            shot["lip_sync"][0]["speaker_id"] = "CHAR-002"
            (root / "04_generation/shot_briefs.jsonl").write_text(json.dumps(shot) + "\n", encoding="utf-8")
            errors = dialogue_sync.validate_project(root)
            self.assertTrue(any("speaker_id" in x for x in errors))

    def test_required_visible_speaker_must_be_subject(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.base_project(td)
            self.write_valid(root)
            shot = json.loads((root / "04_generation/shot_briefs.jsonl").read_text())
            shot["subjects"] = []
            (root / "04_generation/shot_briefs.jsonl").write_text(json.dumps(shot) + "\n", encoding="utf-8")
            errors = dialogue_sync.validate_project(root)
            self.assertTrue(any("not a shot subject" in x for x in errors))

    def test_unresolved_end_frame_reference_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.base_project(td)
            self.write_valid(root)
            shot = json.loads((root / "04_generation/shot_briefs.jsonl").read_text())
            shot["end_frame"]["reference_id"] = "REF-999"
            (root / "04_generation/shot_briefs.jsonl").write_text(json.dumps(shot) + "\n", encoding="utf-8")
            errors = dialogue_sync.validate_project(root)
            self.assertTrue(any("REF-999" in x and "does not resolve" in x for x in errors))

    def test_measured_timing_requires_duration(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.base_project(td)
            self.write_valid(root)
            shot = json.loads((root / "04_generation/shot_briefs.jsonl").read_text())
            del shot["lip_sync"][0]["speech_duration_s"]
            (root / "04_generation/shot_briefs.jsonl").write_text(json.dumps(shot) + "\n", encoding="utf-8")
            errors = dialogue_sync.validate_project(root)
            self.assertTrue(any("requires speech_duration_s" in x for x in errors))

    def test_missing_matching_shooting_sync_blocks_coverage(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.base_project(td)
            self.write_valid(root)
            shooting = json.loads((root / "03_preproduction/shooting_script.json").read_text())
            shooting["scenes"][0]["units"][0]["lip_sync"] = []
            (root / "03_preproduction/shooting_script.json").write_text(json.dumps(shooting), encoding="utf-8")
            report = dialogue_sync.build_coverage(root)
            self.assertFalse(report["lip_sync_ready"])
            self.assertTrue(report["missing_lip_sync_coverage"])

    def test_offscreen_dialogue_does_not_create_requirement(self):
        with tempfile.TemporaryDirectory() as td:
            root = self.base_project(td)
            (root / "04_generation/shot_briefs.jsonl").write_text(json.dumps({"shot_id": "SHOT-001", "scene_id": "SCN-001", "line_ids": ["LINE-001"], "subjects": [], "duration_seconds": 2.0}) + "\n", encoding="utf-8")
            (root / "03_preproduction/shooting_script.json").write_text(json.dumps({"scenes": [{"scene_id": "SCN-001", "units": [{"line_id": "LINE-001", "kind": "dialogue", "speaker": "CHAR-001", "text": "Stay here.", "shot_ids": ["SHOT-001"]}]}]}), encoding="utf-8")
            self.assertEqual(dialogue_sync.validate_project(root), [])
            self.assertTrue(dialogue_sync.build_coverage(root)["lip_sync_ready"])


if __name__ == "__main__":
    unittest.main()
