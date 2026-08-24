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


class V0036StartupPreflightHardGateTests(unittest.TestCase):
    def test_project_init_can_atomically_initialize_comfyui_playbook(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / "film"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/init_story_project.py"),
                    str(project),
                    "--title",
                    "Atomic Preflight",
                    "--format",
                    "video",
                    "--playbook",
                    "full-pipeline",
                ],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            progress = json.loads((project / "00_project/pipeline_progress.json").read_text(encoding="utf-8"))
            preflight = json.loads((project / "00_project/workflow_preflight.json").read_text(encoding="utf-8"))
            self.assertEqual(progress["pipeline_id"], "full-pipeline")
            self.assertEqual(progress["status"], "active")
            self.assertIn("generation-workflow-setup", progress["next_action"])
            self.assertEqual(preflight["playbook"], "full-pipeline")
            self.assertEqual(preflight["profile"], "film-production")
            self.assertEqual(preflight["status"], "needs-selection")
            self.assertTrue(preflight["missing_categories"])

    def test_pi_progress_guard_covers_nested_project_startup_and_managed_state(self):
        source = (ROOT / "extensions/story-film-progress/index.ts").read_text(encoding="utf-8")
        for token in (
            "projectRootFromTarget",
            "PIPELINE_REQUIRED_FORMATS",
            "no active authoritative pipeline",
            "storyFilmManagedStateBlockReason",
            "pipeline_progress.json, workflow_preflight.json, and workflow_preferences.json are Story-Film script-owned state",
            "wrongPlaybookPathBlockReason",
            "skills/story-film/playbooks/",
        ):
            self.assertIn(token, source)

    def test_story_comfy_can_target_child_project_explicitly(self):
        source = (ROOT / "extensions/story-film-comfy/index.ts").read_text(encoding="utf-8")
        self.assertIn("project: Type.Optional(Type.String())", source)
        self.assertIn("requestedProjectCwd", source)
        self.assertIn("delete request.project", source)

    def test_router_catalog_and_docs_put_preflight_before_creative_work(self):
        router = (ROOT / "skills/story-film/SKILL.md").read_text(encoding="utf-8")
        catalog = (ROOT / "skills/story-film/CATALOG.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        workflow_doc = (ROOT / "docs/workflows/story-to-film.md").read_text(encoding="utf-8")
        comfy_discover = (ROOT / "skills/comfyui-discover/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("initialize the project and authoritative progress ledger atomically", router)
        self.assertIn("<package>/skills/story-film/playbooks/<name>.md", catalog)
        self.assertIn("project=<project-root>", comfy_discover)
        self.assertNotIn("saved-ComfyUI, template, and external workflow", readme)
        self.assertNotIn("ComfyUI templates, user-specified", readme)
        self.assertIn("workflow preflight when ComfyUI-backed", workflow_doc)
        self.assertNotIn("saved ComfyUI workflows, templates, external sources", workflow_doc)


if __name__ == "__main__":
    unittest.main()
