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

import pipeline_progress
import workflow_preflight


class V0035RuntimePreflightGuardTests(unittest.TestCase):
    def test_mapped_comfyui_playbooks_compile_preflight_as_first_target(self):
        for playbook, profile in workflow_preflight.PLAYBOOK_PROFILES.items():
            path = ROOT / "skills/story-film/playbooks" / f"{playbook}.md"
            value = pipeline_progress.compile_pipeline(path)
            first = pipeline_progress.flatten_leaves(value)[0][1]
            self.assertIn("generation-workflow-setup", first["label"], playbook)
            self.assertIn(profile, first["label"], playbook)

    def test_pipeline_initialization_creates_and_enforces_preflight(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td) / "film"
            subprocess.run(
                [sys.executable, str(ROOT / "scripts/init_story_project.py"), str(project)],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            value = pipeline_progress.initialize(
                project,
                pipeline_progress.playbook_path("short-film"),
                False,
                3,
            )
            current = pipeline_progress.current_leaf(value)
            self.assertIsNotNone(current)
            self.assertIn("generation-workflow-setup", current[1]["label"])

            state = workflow_preflight.status(project)
            self.assertEqual(state["status"], "needs-selection")
            self.assertEqual(state["profile"], "film-production")

            with self.assertRaises(SystemExit):
                pipeline_progress.checkpoint(
                    project, "completed", None, None, None, "", "attempted bypass", []
                )

            prefs_path = project / "00_project/workflow_preferences.json"
            prefs = json.loads(prefs_path.read_text(encoding="utf-8"))
            prefs["selections"] = {
                category: {
                    "source": "test",
                    "category": category,
                    "name": f"{category}.json",
                }
                for category in state["required_categories"]
            }
            prefs_path.write_text(json.dumps(prefs, indent=2) + "\n", encoding="utf-8")
            self.assertEqual(workflow_preflight.status(project)["status"], "complete")

            advanced = pipeline_progress.checkpoint(
                project, "completed", None, None, None, "", "completed preflight", []
            )
            next_current = pipeline_progress.current_leaf(advanced)
            self.assertIsNotNone(next_current)
            self.assertNotIn("generation-workflow-setup", next_current[1]["label"])

    def test_pi_extension_blocks_preflight_bypass_and_package_rediscovery(self):
        source = (ROOT / "extensions/story-film-progress/index.ts").read_text(encoding="utf-8")
        for token in (
            "workflow_preflight.json",
            "workflowPreflightBlockReason",
            "packageRediscoveryBlockReason",
            "invalidProjectInitBlockReason",
            "generation-workflow-setup",
            "HARD GATE",
            "init_story_project.py does not accept --playbook",
        ):
            self.assertIn(token, source)
        self.assertNotIn("official core template", source)
        self.assertNotIn("installed custom-node example workflow", source)

    def test_story_router_has_direct_package_paths_and_blocking_preflight_rule(self):
        router = (ROOT / "skills/story-film/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("CATALOG.md` is the file beside this router", router)
        self.assertIn("does not accept `--playbook`", router)
        self.assertIn("mark the workflow-preflight target blocked", router)
        self.assertIn("unrelated installed skill packs", router)


if __name__ == "__main__":
    unittest.main()
