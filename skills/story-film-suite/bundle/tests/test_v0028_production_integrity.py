# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
import hashlib
import json
import sys
import tempfile
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import comfy_binding_audit
import comfy_workflow_contracts
import dialogue_audio_authority
import dialogue_timing_preflight
import reference_authority
import reference_sheets
import staged_grounding
import temporal_continuity


class Tests(unittest.TestCase):
    def test_reference_authority(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / "03_preproduction/references/reference_manifest.json"
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps(
                    {
                        "references": [
                            {
                                "ref_id": "REF-001",
                                "authority_scopes": ["character-identity"],
                                "must_not_control": ["camera"],
                                "atlas": {"layout_is_reference_only": True},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(reference_authority.validate_project(root), [])

    def test_temporal_tail_requires_strip(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / "04_generation/temporal_continuity.jsonl"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"temporal_tail": {"duration_seconds": 2, "audio_policy": "keep"}}) + "\n")
            self.assertTrue(temporal_continuity.validate_project(root))

    def test_audio_hash_and_authority(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            audio = root / "a.wav"
            with wave.open(str(audio), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(8000)
                wav.writeframes(b"\0\0" * 8000)
            digest = hashlib.sha256(audio.read_bytes()).hexdigest()
            path = root / "04_generation/dialogue_audio_authority.jsonl"
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps(
                    {
                        "line_id": "LINE-001",
                        "speaker_id": "CHAR-001",
                        "approved_audio_media_id": "MEDIA-001",
                        "path": "a.wav",
                        "audio_sha256": digest,
                        "start_seconds": 0,
                        "visible_sync_required": True,
                        "generation_audio_authority": "approved-dialogue",
                        "review_audio_authority": "approved-dialogue",
                    }
                )
                + "\n"
            )
            self.assertEqual(dialogue_audio_authority.validate_project(root), [])

    def test_binding_audit(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workflow = root / "04_generation/comfyui/workflows/a.json"
            workflow.parent.mkdir(parents=True)
            workflow.write_text(json.dumps({"1": {"class_type": "LoadImage", "inputs": {}}}))
            path = root / "04_generation/comfyui/reference_bindings.jsonl"
            path.write_text(
                json.dumps(
                    {
                        "workflow": "04_generation/comfyui/workflows/a.json",
                        "node_id": "1",
                        "node_type": "LoadImage",
                        "ref_id": "REF-001",
                    }
                )
                + "\n"
            )
            self.assertEqual(comfy_binding_audit.validate_project(root), [])

    def test_reference_sheet_functional_view(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / "03_preproduction/references/reference_sheet_plans.json"
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps(
                    {
                        "plans": [
                            {
                                "sheet_type": "prop-reference",
                                "subject_id": "PROP-001",
                                "required_views": ["front"],
                                "functional_views": ["latch"],
                            }
                        ]
                    }
                )
            )
            self.assertEqual(reference_sheets.validate_project(root), [])

    def test_staged_grounding_order(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = root / "03_preproduction/storyboards/grounding_passes.jsonl"
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps(
                    {
                        "target_id": "SHOT-001",
                        "stage": "composition",
                        "prompt": "layout",
                        "reference_bindings": [],
                        "authority_scopes": ["frame-zero-composition"],
                    }
                )
                + "\n"
                + json.dumps(
                    {
                        "target_id": "SHOT-001",
                        "stage": "identity",
                        "prompt": "identity",
                        "reference_bindings": [{"ref_id": "REF-001"}],
                        "authority_scopes": ["character-identity"],
                    }
                )
                + "\n"
            )
            self.assertEqual(staged_grounding.validate_project(root), [])

    def test_dialogue_timing_overflow(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            audio = root / "line.wav"
            with wave.open(str(audio), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(8000)
                wav.writeframes(b"\0\0" * 16000)
            path = root / "04_generation/dialogue_timing_plan.json"
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps(
                    {
                        "clips": [
                            {
                                "duration_seconds": 1,
                                "lines": [{"line_id": "LINE-001", "path": "line.wav", "start_seconds": 0}],
                            }
                        ]
                    }
                )
            )
            self.assertTrue(dialogue_timing_preflight.validate_project(root))

    def test_contract_database_and_bundled_workflows(self):
        db = comfy_workflow_contracts.load_contracts()
        self.assertIn("minimax-h3-r2v-exact-audio", db["contracts"])

        root = ROOT / "comfyui_workflows"
        workflows = sorted(root.rglob("*.json"))
        self.assertGreaterEqual(len(workflows), 15)
        self.assertFalse(any(path.suffix.lower() == ".zip" for path in root.rglob("*") if path.is_file()))

        for path in workflows:
            value = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsInstance(value, dict, path.relative_to(ROOT).as_posix())

        deps = comfy_workflow_contracts.load_dependencies()
        self.assertIn("comfyui-h3-exact-audio-lock", deps["packages"])
        self.assertIn("videohelpersuite", deps["packages"])
        self.assertIn("comfyui-gguf", deps["packages"])

        for rel in [
            "video/MiniMax-H3/video_minimax_h3_t2v.json",
            "video/MiniMax-H3/video_minimax_h3_i2v.json",
            "video/MiniMax-H3/video_minimax_h3_r2v.json",
            "character-sheet/MiniMax-H3/CharacterTurnaroundSheetH3.json",
            "location-orbit/MiniMax-H3/LocationOrbitSheetH3.json",
            "music/MiniMax-Music-3/audio_minimax_music_3.json",
        ]:
            self.assertTrue((root / rel).is_file(), rel)


if __name__ == "__main__":
    unittest.main()
