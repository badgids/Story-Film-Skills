import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("comfy_official_runtime", ROOT / "scripts/comfy_official_runtime.py")
runtime = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(runtime)


class ManagedOfficialComfyRuntimeTests(unittest.TestCase):
    def test_bootstrap_installs_only_official_control_packages(self):
        self.assertEqual(runtime.OFFICIAL_PACKAGES, ("comfy-cli>=1.14.0", "comfy-mcp", "comfy-api-proxy"))
        argv = runtime.pip_install_argv("/managed/python")
        joined = " ".join(argv)
        self.assertIn("comfy-cli>=1.14.0", joined)
        self.assertIn("comfy-mcp", joined)
        self.assertIn("comfy-api-proxy", joined)
        self.assertNotIn("ComfyUI", joined)
        self.assertNotIn("model", joined.lower())
        self.assertNotIn("custom_nodes", joined)

    def test_project_resource_policy_controls_comfyui_url(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "film"
            state = root / "00_project"
            state.mkdir(parents=True)
            (state / "state.json").write_text("{}\n", encoding="utf-8")
            (state / "resource_policy.json").write_text(json.dumps({"comfyui": {"url": "http://127.0.0.1:9191"}}), encoding="utf-8")
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("STORY_FILM_COMFYUI_URL", None)
                os.environ.pop("COMFY_LOCAL_URL", None)
                self.assertEqual(runtime.resolve_comfyui_url(root / "04_generation"), "http://127.0.0.1:9191")

    def test_story_film_actions_route_through_managed_mcp(self):
        fake = {"ok": True, "result": {"tools": [{"name": "server_info", "description": "server"}, {"name": "search_templates", "description": "templates"}]}}
        with patch.object(runtime, "_run_mcp", return_value=fake) as call:
            out = runtime.dispatch_request({"action": "server-info"})
            self.assertTrue(out["ok"])
            self.assertEqual(call.call_args.args[0]["tool"], "server_info")
        with patch.object(runtime, "_run_mcp", return_value=fake):
            out = runtime.dispatch_request({"action": "search-tools", "query": "template"})
            self.assertEqual(out["count"], 1)
            self.assertEqual(out["tools"][0]["name"], "search_templates")

    def test_pi_extension_registers_native_story_comfy_tool(self):
        text = (ROOT / "extensions/story-film-comfy/index.ts").read_text(encoding="utf-8")
        self.assertIn('name: "story_comfy"', text)
        self.assertIn("pi.registerTool", text)
        self.assertIn("comfy_official_runtime.py", text)
        self.assertIn("ctx.ui.confirm", text)
        self.assertNotIn("QwenImageTextToImageApi", text)


if __name__ == "__main__":
    unittest.main()
