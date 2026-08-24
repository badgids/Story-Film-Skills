# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import llm_model_lifecycle
import workflow_catalog
import workflow_preflight

WORKFLOW_ROOT = ROOT / "comfyui_workflows"

NEW_WORKFLOWS = (
    "image-edit/Krea2/krea2-character-consistency-workflow.json",
    "image-edit/Krea2/krea2_reference_style.json",
    "storyboard/Krea2/Krea2_Storyboard.json",
    "image/Krea2/Krea2_txt2img.json",
    "image-edit/Krea2/smartvision_krea2_identity_edit.json",
    "image-edit/Krea2/smartvision_krea2_identity_edit_8GB_VRAM.json",
    "character-sheet/Krea2/smartvision_krea2_reference_sheet.json",
    "orbit-sheet/Qwen-Image-Edit/comfyui-workflow-multiple-angles.json",
    "image/Qwen-Image-2512/image_qwen_Image_2512.json",
    "image-edit/Qwen-Image-Edit/image_qwen_image_edit.json",
    "llm/Qwen3-VL/llm_qwen3vl_text_gen.json",
    "llm/Qwen3.5/llm_qwen3_5_text_gen.json",
    "llm/Qwen3/llm_qwen3_text_gen.json",
    "orbit-sheet/Qwen-Image-Edit/qwen-edit-multiple-angle-VNCCS.json",
)


class _ModelServer(ThreadingHTTPServer):
    def __init__(self, runtime: str):
        super().__init__(("127.0.0.1", 0), _ModelHandler)
        self.runtime = runtime
        self.models = ["pi-model"]

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.server_port}"


class _ModelHandler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def _json(self, value: dict, status: int = 200) -> None:
        raw = json.dumps(value).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        server = self.server
        if server.runtime == "llama-server" and self.path == "/models":
            self._json({"data": [{"id": model, "status": "loaded"} for model in server.models]})
            return
        if server.runtime == "ollama" and self.path == "/api/ps":
            self._json({"models": [{"name": model} for model in server.models]})
            return
        self._json({"error": "not found"}, 404)

    def do_POST(self):
        size = int(self.headers.get("Content-Length", "0") or 0)
        body = json.loads(self.rfile.read(size) or b"{}")
        server = self.server
        if server.runtime == "llama-server" and self.path in {"/models/load", "/models/unload"}:
            model = str(body.get("model") or "")
            if self.path.endswith("/unload"):
                server.models = [x for x in server.models if x != model]
            elif model and model not in server.models:
                server.models.append(model)
            self._json({"ok": True})
            return
        if server.runtime == "ollama" and self.path == "/api/generate":
            model = str(body.get("model") or "")
            if body.get("keep_alive") == 0:
                server.models = [x for x in server.models if x != model]
            elif model and model not in server.models:
                server.models.append(model)
            self._json({"done": True})
            return
        self._json({"error": "not found"}, 404)


class V0032PreflightLifecycleWorkflowTests(unittest.TestCase):
    def test_new_workflows_are_built_in_without_source_zip(self):
        workflows = sorted(WORKFLOW_ROOT.rglob("*.json"))
        production = [path for path in workflows if "research" not in path.relative_to(WORKFLOW_ROOT).parts]
        research = [path for path in workflows if "research" in path.relative_to(WORKFLOW_ROOT).parts]
        self.assertGreaterEqual(len(workflows), 29)
        self.assertGreaterEqual(len(production), 26)
        self.assertGreaterEqual(len(research), 3)
        self.assertFalse(any(path.suffix.lower() == ".zip" for path in WORKFLOW_ROOT.rglob("*") if path.is_file()))
        for rel in NEW_WORKFLOWS:
            path = WORKFLOW_ROOT / rel
            self.assertTrue(path.is_file(), rel)
            self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict, rel)

    def test_project_workflows_are_not_discovery_sources(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / "film"
            subprocess.run(
                [sys.executable, str(ROOT / "scripts/init_story_project.py"), str(project)],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            custom = project / "04_generation/comfyui/default_workflows/image/UserAdded"
            custom.mkdir(parents=True, exist_ok=True)
            for index in range(137):
                (custom / f"user_{index:03d}.json").write_text(
                    json.dumps({"1": {"class_type": "UserNode", "inputs": {"index": index}}}),
                    encoding="utf-8",
                )
            catalog = workflow_catalog.build_catalog(project, category="image", include_generate=False)
            self.assertFalse(any(row.get("source") == "project-default" for row in catalog["workflows"]))
            self.assertTrue(all(row.get("source") in {"built-in", "package-custom"} for row in catalog["workflows"]))
            self.assertNotIn("limit", catalog)

    def test_film_workflow_preflight_is_complete_before_story_work(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / "film"
            subprocess.run(
                [sys.executable, str(ROOT / "scripts/init_story_project.py"), str(project)],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            state = workflow_preflight.set_preflight(
                project,
                playbook="short-film",
                profile="",
                categories=[],
            )
            self.assertEqual(state["status"], "needs-selection")
            self.assertEqual(tuple(state["required_categories"]), workflow_preflight.FILM_PRODUCTION)
            prefs_path = project / "00_project/workflow_preferences.json"
            prefs = json.loads(prefs_path.read_text(encoding="utf-8"))
            prefs["selections"] = {
                category: {"source": "built-in", "category": category, "name": category + ".json"}
                for category in state["required_categories"]
            }
            prefs_path.write_text(json.dumps(prefs, indent=2) + "\n", encoding="utf-8")
            complete = workflow_preflight.status(project)
            self.assertEqual(complete["status"], "complete")
            self.assertEqual(complete["missing_categories"], [])

        router = (ROOT / "skills/story-film/SKILL.md").read_text(encoding="utf-8")
        setup = (ROOT / "skills/generation-workflow-setup/SKILL.md").read_text(encoding="utf-8")
        short = (ROOT / "skills/story-film/playbooks/short-film.md").read_text(encoding="utf-8")
        feature = (ROOT / "skills/story-film/playbooks/feature-film.md").read_text(encoding="utf-8")
        self.assertIn("before any story or canon artifact", router)
        self.assertIn("Do not ask again later", setup)
        self.assertIn("workflow preflight", short.lower())
        self.assertIn("workflow preflight", feature.lower())

    def _exercise_lifecycle(self, runtime: str) -> None:
        server = _ModelServer(runtime)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as td:
                state_path = Path(td) / "snapshot.json"
                snapshot = llm_model_lifecycle.snapshot_and_unload(
                    "auto", server.url, state_path=state_path, timeout=5
                )
                self.assertEqual(snapshot["runtime"], runtime)
                self.assertEqual(snapshot["models"], ["pi-model"])
                self.assertEqual(server.models, [])
                # Simulate a ComfyUI helper model that was not loaded before handoff.
                server.models.append("comfy-helper")
                restored = llm_model_lifecycle.restore(state_path, timeout=5)
                self.assertEqual(restored["models"], ["pi-model"])
                self.assertEqual(server.models, ["pi-model"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_llama_server_snapshot_unload_and_restore(self):
        self._exercise_lifecycle("llama-server")

    def test_ollama_snapshot_unload_and_restore(self):
        self._exercise_lifecycle("ollama")

    def test_resource_handoff_uses_native_lifecycle_not_agent_scripts(self):
        source = (ROOT / "scripts/resource_handoff.py").read_text(encoding="utf-8")
        skill = (ROOT / "skills/llm-model-lifecycle/SKILL.md").read_text(encoding="utf-8")
        reference = (ROOT / "references/RESOURCE_SAFE_GENERATION.md").read_text(encoding="utf-8")
        self.assertIn("llm_model_lifecycle", source)
        for adapter in ("auto", "llama-server", "ollama"):
            self.assertIn(adapter, source)
        self.assertIn("Never author an ad hoc curl", skill)
        self.assertIn("POST /models/unload", reference)
        self.assertIn("keep_alive", reference)
        self.assertIn("untracked temporary models", reference)


if __name__ == "__main__":
    unittest.main()
