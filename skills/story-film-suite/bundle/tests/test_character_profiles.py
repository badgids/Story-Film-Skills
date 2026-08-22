import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import character_profiles


class CharacterProfileTests(unittest.TestCase):
    def project(self, td, canon, state=None):
        root = Path(td)
        (root / "00_project").mkdir(parents=True)
        (root / "01_story").mkdir(parents=True)
        (root / "00_project/canon.json").write_text(json.dumps(canon), encoding="utf-8")
        (root / "01_story/story_state.json").write_text(json.dumps(state or {"scene_order": [], "characters": {}}), encoding="utf-8")
        return root

    def test_legacy_character_and_relationship_string_remain_valid(self):
        with tempfile.TemporaryDirectory() as td:
            canon = {"characters": {"CHAR-001": {"name": "Mara"}, "CHAR-002": {"name": "Elias"}}}
            state = {"scene_order": ["SCN-001"], "characters": {"CHAR-001": {"relationships": {"CHAR-002": "guarded"}}}}
            self.assertEqual(character_profiles.validate_project(self.project(td, canon, state)), [])

    def test_rich_profile_and_canonical_pair_pass(self):
        with tempfile.TemporaryDirectory() as td:
            canon = {
                "characters": {
                    "CHAR-001": {"name": "Mara", "identity": {"must_preserve": ["scar left"], "must_not_be": ["scar right"], "may_vary": ["expression"]}, "performance_signature": {"speech": {"cadence": "deliberate", "habits": ["pauses"]}, "movement": {"gesture_quality": "economical", "habitual_actions": []}, "stillness": {"gaze": "steady"}}},
                    "CHAR-002": {"name": "Elias"},
                },
                "relationship_baselines": {"CHAR-001::CHAR-002": {"characters": ["CHAR-001", "CHAR-002"], "room_shape": "quiet"}},
            }
            state = {"scene_order": ["SCN-001"], "characters": {"CHAR-001": {"relationships": {"CHAR-002": {"state": "guarded", "last_changed_in": "SCN-001"}}}}}
            self.assertEqual(character_profiles.validate_project(self.project(td, canon, state)), [])

    def test_bad_identity_list_and_pair_key_fail(self):
        with tempfile.TemporaryDirectory() as td:
            canon = {
                "characters": {"CHAR-001": {"identity": {"must_preserve": "scar"}}, "CHAR-002": {}},
                "relationship_baselines": {"CHAR-002::CHAR-001": {"characters": ["CHAR-001", "CHAR-002"]}},
            }
            errors = character_profiles.validate_project(self.project(td, canon))
            self.assertTrue(any("must_preserve" in x for x in errors))
            self.assertTrue(any("canonical pair" in x for x in errors))

    def test_unknown_current_relationship_target_fails(self):
        with tempfile.TemporaryDirectory() as td:
            canon = {"characters": {"CHAR-001": {}}}
            state = {"scene_order": ["SCN-001"], "characters": {"CHAR-001": {"relationships": {"CHAR-999": {"state": "unknown"}}}}}
            errors = character_profiles.validate_project(self.project(td, canon, state))
            self.assertTrue(any("unresolved character ID" in x for x in errors))


if __name__ == "__main__":
    unittest.main()
