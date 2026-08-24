# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import minimax_h3_skill_router


class V0039MiniMaxH3SkillTests(unittest.TestCase):
    def test_all_nine_h3_skill_capabilities_are_present(self):
        expected = {
            "h3-prompt-writing",
            "minimalist-product-ad-generator",
            "3d-animation-short-generator",
            "papercraft-stop-motion-explainer",
            "brand-promo-video-generator",
            "music-video-subtitle-generator",
            "co-op-game-intro-generator",
            "paper-collage-explainer-generator",
            "handdrawn-live-video-generator",
        }
        for name in expected:
            self.assertTrue((ROOT / "skills" / name / "SKILL.md").is_file(), name)
        self.assertTrue((ROOT / "skills/h3-prompt-writing/references/base-en.txt").is_file())
        self.assertTrue((ROOT / "skills/h3-prompt-writing/references/ref-en.txt").is_file())

    def test_h3_base_is_always_used_and_style_routing_is_conditional(self):
        cases = {
            "Make a minimalist product ad for this watch launch": "minimalist-product-ad-generator",
            "Create a stylized 3D animated short with character continuity": "3d-animation-short-generator",
            "Explain photosynthesis as a papercraft stop-motion explainer": "papercraft-stop-motion-explainer",
            "Create a verified brand promo for our app launch": "brand-promo-video-generator",
            "Build a music video with lyric typography synced to the beat": "music-video-subtitle-generator",
            "Create a co-op game intro for PLAYER 1 and PLAYER 2": "co-op-game-intro-generator",
            "Explain the concept as a halftone paper collage explainer": "paper-collage-explainer-generator",
            "Blend rough glowing hand-drawn animation with live action": "handdrawn-live-video-generator",
        }
        for brief, expected_style in cases.items():
            routed = minimax_h3_skill_router.route(brief)
            self.assertEqual(routed["base_skill"], "h3-prompt-writing")
            self.assertEqual(routed["style_skill"], expected_style)

        generic = minimax_h3_skill_router.route("A woman walks across a rainy station platform.")
        self.assertEqual(generic["base_skill"], "h3-prompt-writing")
        self.assertIsNone(generic["style_skill"])

        explicit = minimax_h3_skill_router.route(
            "Make a strange experimental video.",
            "paper-collage-explainer-generator",
        )
        self.assertEqual(explicit["base_skill"], "h3-prompt-writing")
        self.assertEqual(explicit["style_skill"], "paper-collage-explainer-generator")

    def test_h3_format_and_story_film_wiring_are_documented(self):
        minimax = (ROOT / "skills/minimax-h3/SKILL.md").read_text(encoding="utf-8")
        base = (ROOT / "skills/h3-prompt-writing/references/base-en.txt").read_text(encoding="utf-8")
        ref = (ROOT / "skills/h3-prompt-writing/references/ref-en.txt").read_text(encoding="utf-8")
        playbook = (ROOT / "skills/story-film/playbooks/generation-prompts.md").read_text(encoding="utf-8")
        qc = (ROOT / "skills/prompt-qc/SKILL.md").read_text(encoding="utf-8")
        model_routing = (ROOT / "references/MODEL_ROUTING.md").read_text(encoding="utf-8")
        source_routing = (ROOT / "references/MINIMAX_H3_SKILL_ROUTING.md").read_text(encoding="utf-8")
        sources = (ROOT / "SOURCES.md").read_text(encoding="utf-8")

        self.assertIn("h3_base_skill: h3-prompt-writing", minimax)
        self.assertIn("h3_style_skill:", minimax)
        self.assertIn("minimax_h3_skill_router.py", minimax)
        self.assertIn("integrated_multimodal_description", base)
        self.assertIn("overall_soundscape", base)
        self.assertIn("non_diegetic_music", base)
        self.assertIn("<d>[Language]", base)
        self.assertIn("subject_definitions", ref)
        self.assertIn("retention_analysis", ref)
        self.assertIn("detailed_description", ref)
        self.assertIn("h3-prompt-writing", playbook)
        self.assertIn("h3_style_skill", playbook)
        self.assertIn("for MiniMax H3", qc)
        self.assertIn("minimax_h3_skill_router.py", model_routing)
        self.assertIn("Authority order", source_routing)
        self.assertIn("d21241f0a4b3acbb34c97dae47fa417b7065e438", sources)

    def test_style_adaptations_have_no_hub_runtime_dependency(self):
        for name in minimax_h3_skill_router.STYLE_SKILLS:
            text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("hub_generate_", text)
            self.assertNotIn("hub_canvas_", text)


if __name__ == "__main__":
    unittest.main()
