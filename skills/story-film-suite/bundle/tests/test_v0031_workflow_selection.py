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
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
WORKFLOW_ROOT = ROOT / "comfyui_workflows"


class V0031WorkflowSelectionTests(unittest.TestCase):
    def test_supplied_workflow_library_is_extracted_and_task_first(self):
        workflows = sorted(WORKFLOW_ROOT.rglob("*.json"))
        self.assertGreaterEqual(len(workflows), 15)
        self.assertFalse(any(path.suffix.lower() == ".zip" for path in WORKFLOW_ROOT.rglob("*") if path.is_file()))
        self.assertFalse((ROOT / "references/comfyui_workflows").exists())
        self.assertFalse((ROOT / "docs/generation/sanitized-workflows.md").exists())

        for path in workflows:
            rel = path.relative_to(WORKFLOW_ROOT)
            self.assertGreaterEqual(len(rel.parts), 3, rel.as_posix())
            value = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsInstance(value, dict, rel.as_posix())

        required = [
            "video/MiniMax-H3/video_minimax_h3_t2v.json",
            "video/MiniMax-H3/video_minimax_h3_i2v.json",
            "video/MiniMax-H3/video_minimax_h3_r2v.json",
            "video/MiniMax-H3/video_minimax_h3_r2v_exact_audio_hybrid.json",
            "character-sheet/MiniMax-H3/CharacterTurnaroundSheetH3.json",
            "location-orbit/MiniMax-H3/LocationOrbitSheetH3.json",
            "prop-sheet/MiniMax-H3/PropReferenceSheetH3.json",
            "tts/Qwen3-TTS/qwen3_tts_flybird.json",
            "music/MiniMax-Music-3/audio_minimax_music_3.json",
            "sfx/Stable-Audio-3/audio_stable_audio_3_sfx.json",
            "upscale/NVIDIA-RTX/RTX_SR_Upscaler_Video_reference.json",
            "frame-interpolation/FILM/FrameInterpolationFILM.json",
        ]
        for rel in required:
            self.assertTrue((WORKFLOW_ROOT / rel).is_file(), rel)

    def test_video_catalog_is_numbered_and_complete_for_extension_library(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / "film"
            subprocess.run(
                [sys.executable, str(ROOT / "scripts/init_story_project.py"), str(project)],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/workflow_catalog.py"),
                    "catalog",
                    str(project),
                    "--category",
                    "video",
                ],
                check=True,
                text=True,
                capture_output=True,
            )
            catalog = json.loads((project / "00_project/comfyui_workflow_catalog.json").read_text(encoding="utf-8"))
            expected_video = list((WORKFLOW_ROOT / "video").rglob("*.json"))
            custom_video = WORKFLOW_ROOT / "custom" / "video"
            if custom_video.is_dir():
                expected_video.extend(custom_video.rglob("*.json"))
            self.assertEqual(len(catalog["workflows"]), len(expected_video))
            self.assertTrue(
                all(row["source"] in {"built-in", "package-custom"} for row in catalog["workflows"])
            )
            self.assertRegex(result.stdout, r"(?m)^1\. \[built-in\]")
            self.assertIn("Reply with the number you want to use.", result.stdout)
            self.assertNotIn("ask_user_question", result.stdout)
            self.assertFalse(any("research/" in str(row.get("path", "")) for row in catalog["workflows"]))

            subprocess.run(
                [sys.executable, str(ROOT / "scripts/workflow_catalog.py"), "choose", str(project), "1"],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            prefs = json.loads((project / "00_project/workflow_preferences.json").read_text(encoding="utf-8"))
            selected = prefs["selections"]["video"]
            self.assertEqual(selected["source"], "built-in")
            self.assertEqual(selected["category"], "video")

            subprocess.run(
                [sys.executable, str(ROOT / "scripts/workflow_catalog.py"), "materialize", str(project), "video"],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            prefs = json.loads((project / "00_project/workflow_preferences.json").read_text(encoding="utf-8"))
            materialized = project / prefs["selections"]["video"]["materialized_path"]
            self.assertTrue(materialized.is_file())
            json.loads(materialized.read_text(encoding="utf-8"))

    def test_catalog_ignores_project_and_external_workflows(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            project = base / "film"
            subprocess.run(
                [sys.executable, str(ROOT / "scripts/init_story_project.py"), str(project)],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            project_default = project / "04_generation/comfyui/default_workflows/sfx/CustomSFX/default.json"
            project_default.parent.mkdir(parents=True, exist_ok=True)
            project_default.write_text(json.dumps({"1": {"class_type": "TestSFX", "inputs": {}}}), encoding="utf-8")
            project_workflow = project / "04_generation/comfyui/workflows/project.json"
            project_workflow.write_text(json.dumps({"1": {"class_type": "ProjectNode", "inputs": {}}}), encoding="utf-8")

            catalog = __import__("workflow_catalog").build_catalog(project, category="sfx", include_generate=False)
            sources = {row["source"] for row in catalog["workflows"]}
            self.assertTrue(sources <= {"built-in", "package-custom"})
            self.assertNotIn("project-default", sources)
            self.assertNotIn("project-workflow", sources)
            self.assertNotIn("external", sources)
            self.assertNotIn("comfyui-user", sources)

    def test_workflow_first_contract_retires_model_tui(self):
        reference = (ROOT / "references/WORKFLOW_SELECTION.md").read_text(encoding="utf-8")
        setup = (ROOT / "skills/generation-workflow-setup/SKILL.md").read_text(encoding="utf-8")
        legacy = (ROOT / "skills/generation-model-setup/SKILL.md").read_text(encoding="utf-8")
        docs = (ROOT / "docs/generation/workflow-selection.md").read_text(encoding="utf-8")

        self.assertIn("ordinary numbered list", reference)
        self.assertIn("selected workflow is the authority", reference)
        self.assertIn("Do **not** use `ask_user_question`", setup)
        self.assertIn("There is no four-choice limit", setup)
        self.assertIn("Direct interactive model/resource selection was retired", legacy)
        self.assertIn("comfyui_workflows/custom/<task>/<model>/", docs)
        self.assertIn("does not scan project folders, ComfyUI userdata", docs)
        self.assertIn("Story-Film does **not** scan:", reference)
        self.assertIn("Explicit workflow creation", reference)
        self.assertNotIn("[comfyui-core-template]", docs)

        pipeline = (ROOT / "scripts/comfy_workflow_pipeline.py").read_text(encoding="utf-8")
        self.assertIn("workflow_preferences.json", pipeline)
        self.assertIn("selected_workflow_authority", pipeline)
        self.assertIn("durable selected workflow", pipeline)

        validator = (ROOT / "scripts/validate_skills.py").read_text(encoding="utf-8")
        self.assertIn("'comfyui_workflows' in p.parts", validator)
        self.assertIn("Preserve it exactly", validator)

        comfy_generate = (ROOT / "skills/story-film/playbooks/comfyui-generate.md").read_text(encoding="utf-8")
        self.assertNotIn("generate-new catalog option", comfy_generate)
        self.assertIn("explicitly asks Story-Film to create a new workflow", comfy_generate)
        self.assertIn("bounded live-schema workflow-authoring path", comfy_generate)


if __name__ == "__main__":
    unittest.main()
