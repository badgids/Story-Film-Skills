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
        fake = {"ok": True, "result": {"tools": [
            {"name": "server_info", "description": "server"},
            {"name": "search_templates", "description": "templates"},
            {"name": "search_models", "description": "List or search local model files"},
        ]}}
        with patch.object(runtime, "_run_mcp", return_value=fake) as call:
            out = runtime.dispatch_request({"action": "server-info"})
            self.assertTrue(out["ok"])
            self.assertEqual(call.call_args.args[0]["tool"], "server_info")
        with patch.object(runtime, "_run_mcp", return_value=fake):
            out = runtime.dispatch_request({"action": "search-tools", "query": "template"})
            self.assertEqual(out["count"], 1)
            self.assertEqual(out["tools"][0]["name"], "search_templates")
            out = runtime.dispatch_request({"action": "search-tools", "query": "image to image text to image sdxl flux checkpoint"})
            self.assertTrue(any(tool.get("name") == "search_models" for tool in out["tools"]))

    def test_native_model_inventory_searches_all_live_folders_and_node_choices(self):
        inventory = {
            "schema_version": 1,
            "folders": {
                "checkpoints": {"count": 1, "models": ["stable_audio_3_medium.safetensors"]},
                "unet": {"count": 1, "models": ["qwen-image-2512-Q4_K_M.gguf"]},
                "diffusion_models": {"count": 2, "models": ["minimax_h3_fl2va_pruned_int8_convrot.safetensors", "ltx-2.5-22b-dev-transformer-comfy-int8-convrot.safetensors"]},
            },
            "resource_count": 4,
            "node_choices": [{
                "key": "node:UnetLoaderGGUF:unet_name",
                "node_class": "UnetLoaderGGUF",
                "input": "unet_name",
                "choices": ["qwen-image-2512-Q4_K_M.gguf"],
            }],
            "warnings": [],
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "film"
            (root / "00_project").mkdir(parents=True)
            (root / "00_project/state.json").write_text("{}\n", encoding="utf-8")
            with patch.object(runtime.model_inventory, "scan", return_value=inventory):
                out = runtime.dispatch_request({"action": "model-inventory"}, project=root)
                self.assertIn("unet", out["summary"]["primary_weight_models"])
                self.assertIn("diffusion_models", out["summary"]["primary_weight_models"])
                found = runtime.dispatch_request({"action": "model-search", "query": "qwen image 2512"}, project=root)
                self.assertGreaterEqual(found["total"], 1)
                self.assertTrue(any(row["name"] == "qwen-image-2512-Q4_K_M.gguf" for row in found["matches"]))
                h3 = runtime.dispatch_request({"action": "model-search", "query": "minimax h3"}, project=root)
                self.assertTrue(any(row.get("folder") == "diffusion_models" for row in h3["matches"]))

    def test_pi_extension_registers_native_story_comfy_tool(self):
        text = (ROOT / "extensions/story-film-comfy/index.ts").read_text(encoding="utf-8")
        self.assertIn('name: "story_comfy"', text)
        self.assertIn("pi.registerTool", text)
        self.assertIn("comfy_official_runtime.py", text)
        self.assertIn("ctx.ui.confirm", text)
        self.assertIn('Type.Literal("model-inventory")', text)
        self.assertIn('Type.Literal("model-search")', text)
        self.assertIn("Never treat the checkpoints folder as the complete image/video model inventory", text)
        self.assertIn('pi.on?.("tool_call"', text)
        self.assertIn("Story-Film blocks shell/filesystem ComfyUI discovery", text)
        self.assertIn("action=model-inventory", text)
        self.assertNotIn("if (!storyProjectRoot(ctx.cwd)) return undefined;", text)
        self.assertNotIn("QwenImageTextToImageApi", text)

    def test_comfyui_discovery_contract_forbids_shell_fallback(self):
        suite = (ROOT / "skills/story-film-suite/SKILL.md").read_text(encoding="utf-8")
        router = (ROOT / "skills/story-film/SKILL.md").read_text(encoding="utf-8")
        comfy = (ROOT / "skills/comfyui/SKILL.md").read_text(encoding="utf-8")
        discover = (ROOT / "skills/comfyui-discover/SKILL.md").read_text(encoding="utf-8")
        mcp = (ROOT / "skills/comfyui-mcp/SKILL.md").read_text(encoding="utf-8")
        core = (ROOT / "references/CORE_CONTRACT.md").read_text(encoding="utf-8")
        mcp_ref = (ROOT / "references/COMFYUI_MCP.md").read_text(encoding="utf-8")

        self.assertIn("Do not use Bash, `find`, `ls`, or directory scans to rediscover this bundle", suite)
        self.assertIn("## ComfyUI discovery precedence", router)
        self.assertIn("`story_comfy` has precedence over shell/filesystem discovery", comfy)
        self.assertIn("use Bash, `find`, `ls`, `which`, `locate`", discover)
        self.assertIn("not permission to use Bash", mcp)
        self.assertIn("## 15. Tool-owned ComfyUI discovery", core)
        self.assertIn("not a managed-runtime failure", mcp_ref)


if __name__ == "__main__":
    unittest.main()
