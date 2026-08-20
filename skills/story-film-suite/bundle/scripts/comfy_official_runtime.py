#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Story-Film managed bridge to the official Comfy control stack.

Story-Film owns this Apache-2.0 bridge only. The upstream packages are installed
into a separate managed Python environment and retain their own licenses.

The bootstrap installs only control tooling:
  * comfy-cli>=1.14.0
  * comfy-mcp
  * comfy-api-proxy

It never installs ComfyUI, models, or custom nodes as part of bootstrap.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import platform
import re
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import venv
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import model_inventory

OFFICIAL_PACKAGES = ("comfy-cli>=1.14.0", "comfy-mcp", "comfy-api-proxy")
DEFAULT_COMFYUI_URL = "http://127.0.0.1:8188"
DEFAULT_V2_URL = "http://127.0.0.1:8189"
STATE_SCHEMA = 1


class RuntimeErrorDetail(RuntimeError):
    pass


def _json_safe(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", exclude_none=True)
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _emit(value: Any) -> None:
    print(json.dumps(_json_safe(value), ensure_ascii=False))


def _runtime_root() -> Path:
    override = os.environ.get("STORY_FILM_COMFY_RUNTIME_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData/Local"))
        return base / "Story-Film-Skills" / "comfy-runtime"
    if platform.system() == "Darwin":
        return Path.home() / "Library" / "Caches" / "Story-Film-Skills" / "comfy-runtime"
    base = Path(os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache"))
    return base / "story-film-skills" / "comfy-runtime"


def _venv_dir() -> Path:
    return _runtime_root() / "venv"


def _bin_dir() -> Path:
    return _venv_dir() / ("Scripts" if os.name == "nt" else "bin")


def _exe(name: str) -> Path:
    suffix = ".exe" if os.name == "nt" else ""
    return _bin_dir() / f"{name}{suffix}"


def _venv_python() -> Path:
    return _exe("python")


def pip_install_argv(python: str | Path) -> list[str]:
    return [
        str(python), "-m", "pip", "install", "--disable-pip-version-check",
        "--upgrade", *OFFICIAL_PACKAGES,
    ]


def _state_path() -> Path:
    return _runtime_root() / "state.json"


def _proxy_pid_path() -> Path:
    return _runtime_root() / "proxy.pid"


def _proxy_log_path() -> Path:
    return _runtime_root() / "proxy.log"


def _package_versions() -> dict[str, str]:
    py = _venv_python()
    if not py.is_file():
        return {}
    code = (
        "import json, importlib.metadata as m\n"
        "names=['comfy-cli','comfy-mcp','comfy-api-proxy','mcp']\n"
        "out={}\n"
        "for n in names:\n"
        "  try: out[n]=m.version(n)\n"
        "  except m.PackageNotFoundError: pass\n"
        "print(json.dumps(out))"
    )
    proc = subprocess.run([str(py), "-c", code], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode:
        return {}
    try:
        obj = json.loads(proc.stdout)
        return obj if isinstance(obj, dict) else {}
    except json.JSONDecodeError:
        return {}


def _runtime_ready() -> bool:
    needed = (_venv_python(), _exe("comfy"), _exe("comfy-mcp"), _exe("comfy-api-proxy"))
    return all(p.is_file() for p in needed)


def ensure_runtime(*, upgrade: bool = False) -> dict[str, Any]:
    if sys.version_info < (3, 10):
        raise RuntimeErrorDetail("Story-Film's managed official Comfy runtime requires Python 3.10 or newer.")
    root = _runtime_root()
    root.mkdir(parents=True, exist_ok=True)
    created = False
    if not _venv_python().is_file():
        venv.EnvBuilder(with_pip=True, clear=False).create(_venv_dir())
        created = True
    installed = False
    if upgrade or not _runtime_ready():
        proc = subprocess.run(
            pip_install_argv(_venv_python()),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if proc.returncode:
            tail = "\n".join(proc.stdout.splitlines()[-30:])
            raise RuntimeErrorDetail(
                "Could not install Story-Film's managed official Comfy control runtime. "
                "ComfyUI and model installation were not attempted.\n" + tail
            )
        installed = True
    if not _runtime_ready():
        raise RuntimeErrorDetail("Managed Comfy control runtime is incomplete after installation.")
    state = {
        "schema_version": STATE_SCHEMA,
        "managed_by": "story-film-skills",
        "runtime_root": str(root),
        "venv": str(_venv_dir()),
        "comfy": str(_exe("comfy")),
        "comfy_mcp": str(_exe("comfy-mcp")),
        "comfy_api_proxy": str(_exe("comfy-api-proxy")),
        "requested_packages": list(OFFICIAL_PACKAGES),
        "versions": _package_versions(),
        "created": created,
        "installed_or_upgraded": installed,
        "installs_comfyui": False,
        "installs_models": False,
    }
    _state_path().write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return state


def _find_project(start: str | Path | None) -> Path | None:
    if start is None:
        return None
    here = Path(start).expanduser().resolve()
    if here.is_file():
        here = here.parent
    while True:
        if (here / "00_project" / "state.json").is_file() or (here / "00_project" / "resource_policy.json").is_file():
            return here
        if here.parent == here:
            return None
        here = here.parent


def _clean_http_url(raw: str, label: str) -> str:
    value = raw.strip().rstrip("/")
    if "://" not in value:
        value = "http://" + value
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme != "http" or not parsed.hostname or parsed.username or parsed.password:
        raise RuntimeErrorDetail(f"invalid {label} URL: {raw!r}; expected an http URL without embedded credentials")
    return value


def resolve_comfyui_url(project: str | Path | None = None, explicit: str | None = None) -> str:
    if explicit:
        return _clean_http_url(explicit, "ComfyUI")
    env_value = os.environ.get("STORY_FILM_COMFYUI_URL") or os.environ.get("COMFY_LOCAL_URL")
    if env_value:
        return _clean_http_url(env_value, "ComfyUI")
    root = _find_project(project)
    if root:
        policy = root / "00_project" / "resource_policy.json"
        try:
            obj = json.loads(policy.read_text(encoding="utf-8"))
            value = obj.get("comfyui", {}).get("url")
            if isinstance(value, str) and value.strip():
                return _clean_http_url(value, "ComfyUI")
        except (OSError, json.JSONDecodeError, AttributeError):
            pass
    return DEFAULT_COMFYUI_URL


def resolve_v2_url(explicit: str | None = None) -> str:
    return _clean_http_url(explicit or os.environ.get("STORY_FILM_COMFY_API_V2_URL") or DEFAULT_V2_URL, "Comfy API v2")


def _managed_env(comfyui_url: str) -> dict[str, str]:
    env = dict(os.environ)
    env["COMFY_BIN"] = str(_exe("comfy"))
    env["COMFY_LOCAL_URL"] = comfyui_url
    return env


async def _mcp_exchange(request: dict[str, Any], comfyui_url: str) -> dict[str, Any]:
    # Imported only inside the managed venv. comfy-mcp brings a compatible MCP SDK.
    from mcp import ClientSession, StdioServerParameters  # type: ignore
    from mcp.client.stdio import stdio_client  # type: ignore

    params = StdioServerParameters(
        command=str(_exe("comfy-mcp")),
        args=[],
        env=_managed_env(comfyui_url),
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            action = request.get("action")
            if action == "list-tools":
                result = await session.list_tools()
            elif action == "call":
                name = str(request.get("tool") or "").strip()
                if not name:
                    raise RuntimeErrorDetail("MCP tool name is required")
                arguments = request.get("arguments") or {}
                if not isinstance(arguments, dict):
                    raise RuntimeErrorDetail("MCP tool arguments must be an object")
                result = await session.call_tool(name, arguments)
            else:
                raise RuntimeErrorDetail(f"unsupported MCP exchange action: {action!r}")
            return {
                "ok": True,
                "transport": "managed-comfy-mcp-stdio",
                "comfyui_url": comfyui_url,
                "server": _json_safe(init),
                "result": _json_safe(result),
            }


def _internal_mcp(request: dict[str, Any], comfyui_url: str) -> dict[str, Any]:
    return asyncio.run(_mcp_exchange(request, comfyui_url))


def _run_mcp(request: dict[str, Any], comfyui_url: str, timeout: float = 3600.0) -> dict[str, Any]:
    ensure_runtime()
    payload = json.dumps({"request": request, "comfyui_url": comfyui_url}, ensure_ascii=False)
    proc = subprocess.run(
        [str(_venv_python()), str(Path(__file__).resolve()), "_mcp"],
        input=payload,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=_managed_env(comfyui_url),
        timeout=timeout,
    )
    if proc.returncode:
        detail = (proc.stderr or proc.stdout).strip()
        raise RuntimeErrorDetail(detail or f"managed comfy-mcp bridge exited {proc.returncode}")
    try:
        obj = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeErrorDetail("managed comfy-mcp bridge returned invalid JSON") from exc
    if not isinstance(obj, dict):
        raise RuntimeErrorDetail("managed comfy-mcp bridge returned an invalid result")
    return obj


def _tool_records(obj: dict[str, Any]) -> list[dict[str, Any]]:
    result = obj.get("result")
    if not isinstance(result, dict):
        return []
    tools = result.get("tools")
    if isinstance(tools, list):
        return [x for x in tools if isinstance(x, dict)]
    # Pydantic dump of ListToolsResult is normally {tools:[...]}; keep a fallback.
    nested = result.get("result")
    if isinstance(nested, dict) and isinstance(nested.get("tools"), list):
        return [x for x in nested["tools"] if isinstance(x, dict)]
    return []


def _tool_search_terms(query: str) -> set[str]:
    terms = {token for token in re.findall(r"[a-z0-9]+", query.casefold()) if token not in {"a", "an", "and", "or", "the", "to", "for", "of", "with", "in", "on"}}
    if terms & {"checkpoint", "ckpt", "unet", "diffusion", "lora", "vae", "sdxl", "flux", "qwen", "minimax", "ltx"}:
        terms.add("model")
    if terms & {"graph", "workflow", "template"}:
        terms.update({"workflow", "template"})
    return terms


def _tool_match_score(tool: dict[str, Any], terms: set[str]) -> int:
    haystack = (str(tool.get("name", "")) + " " + str(tool.get("description", ""))).casefold()
    return sum(1 for term in terms if term in haystack)


def _http_json(url: str, *, method: str = "GET", body: Any = None, timeout: float = 15.0) -> Any:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method.upper(), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        if not raw:
            return {"status": resp.status}
        text = raw.decode("utf-8", errors="replace")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"status": resp.status, "text": text}


def _proxy_health(v2_url: str) -> dict[str, Any]:
    try:
        value = _http_json(v2_url + "/api/v2/health", timeout=2.0)
        return {"running": True, "url": v2_url, "health": value}
    except Exception:
        return {"running": False, "url": v2_url}


def proxy_start(comfyui_url: str, v2_url: str) -> dict[str, Any]:
    ensure_runtime()
    health = _proxy_health(v2_url)
    if health["running"]:
        return health
    parsed = urllib.parse.urlparse(v2_url)
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeErrorDetail("Story-Film only auto-starts comfy-api-proxy on loopback")
    port = parsed.port or 8189
    _runtime_root().mkdir(parents=True, exist_ok=True)
    log = open(_proxy_log_path(), "ab", buffering=0)
    proc = subprocess.Popen(
        [str(_exe("comfy-api-proxy")), "--comfyui", comfyui_url, "--host", "127.0.0.1", "--port", str(port)],
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        env=dict(os.environ),
    )
    _proxy_pid_path().write_text(str(proc.pid) + "\n", encoding="utf-8")
    deadline = time.monotonic() + 15.0
    while time.monotonic() < deadline:
        health = _proxy_health(v2_url)
        if health["running"]:
            health["pid"] = proc.pid
            health["log"] = str(_proxy_log_path())
            return health
        if proc.poll() is not None:
            break
        time.sleep(0.25)
    raise RuntimeErrorDetail(f"comfy-api-proxy did not become healthy; see {_proxy_log_path()}")


def proxy_stop(v2_url: str) -> dict[str, Any]:
    pid = None
    try:
        pid = int(_proxy_pid_path().read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        pass
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        except PermissionError as exc:
            raise RuntimeErrorDetail(f"cannot stop managed comfy-api-proxy pid {pid}: {exc}") from exc
    try:
        _proxy_pid_path().unlink()
    except FileNotFoundError:
        pass
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and _proxy_health(v2_url)["running"]:
        time.sleep(0.2)
    return {"running": _proxy_health(v2_url)["running"], "url": v2_url, "stopped_pid": pid}


def v2_request(v2_url: str, method: str, path: str, body: Any = None) -> dict[str, Any]:
    clean = "/" + path.lstrip("/")
    if not (clean == "/api/v2/health" or clean.startswith("/api/v2/")):
        raise RuntimeErrorDetail("v2 request path must stay under /api/v2/")
    token = os.environ.get("COMFY_API_V2_TOKEN", "")
    data = None
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(v2_url + clean, data=data, method=method.upper(), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60.0) as resp:
            raw = resp.read()
            text = raw.decode("utf-8", errors="replace") if raw else ""
            try:
                value = json.loads(text) if text else None
            except json.JSONDecodeError:
                value = text
            return {"ok": True, "status": resp.status, "url": v2_url + clean, "result": value}
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "status": exc.code, "url": v2_url + clean, "error": text}


def dispatch_request(req: dict[str, Any], *, project: str | Path | None = None) -> dict[str, Any]:
    action = str(req.get("action") or "doctor").strip().lower()
    comfyui_url = resolve_comfyui_url(project, req.get("comfyui_url") if isinstance(req.get("comfyui_url"), str) else None)
    v2_url = resolve_v2_url(req.get("v2_url") if isinstance(req.get("v2_url"), str) else None)
    if action in {"doctor", "ensure"}:
        state = ensure_runtime(upgrade=bool(req.get("upgrade")))
        state["comfyui_url"] = comfyui_url
        state["proxy"] = _proxy_health(v2_url)
        return {"ok": True, "action": action, "runtime": state}
    if action == "server-info":
        return _run_mcp({"action": "call", "tool": "server_info", "arguments": {}}, comfyui_url, 120.0)
    if action in {"model-inventory", "model-search"}:
        root = _find_project(project)
        if root is None:
            raise RuntimeErrorDetail("model inventory requires a Story-Film project with 00_project state")
        inventory = model_inventory.scan(root, comfyui_url)
        if action == "model-inventory":
            return {
                "ok": True,
                "action": action,
                "comfyui_url": comfyui_url,
                "inventory": str(model_inventory.json_path(root)),
                "markdown": str(model_inventory.markdown_path(root)),
                "summary": model_inventory.inventory_summary(inventory),
            }
        try:
            limit = int(req.get("limit") or 100)
        except (TypeError, ValueError) as exc:
            raise RuntimeErrorDetail("model-search limit must be an integer") from exc
        return {
            "ok": True,
            "action": action,
            "comfyui_url": comfyui_url,
            "inventory": str(model_inventory.json_path(root)),
            **model_inventory.search_inventory(
                inventory,
                str(req.get("query") or "").strip(),
                str(req.get("folder") or "").strip() or None,
                limit,
            ),
        }
    if action == "list-tools":
        return _run_mcp({"action": "list-tools"}, comfyui_url, 120.0)
    if action == "search-tools":
        result = _run_mcp({"action": "list-tools"}, comfyui_url, 120.0)
        query = str(req.get("query") or "").strip().lower()
        tools = _tool_records(result)
        terms = _tool_search_terms(query)
        if terms:
            scored = [(tool, _tool_match_score(tool, terms)) for tool in tools]
            tools = [tool for tool, score in sorted(scored, key=lambda item: (-item[1], str(item[0].get("name", "")).casefold())) if score > 0]
        return {"ok": True, "action": action, "query": query, "terms": sorted(terms), "tools": tools, "count": len(tools)}
    if action == "call":
        tool = str(req.get("tool") or "").strip()
        args = req.get("arguments") or {}
        return _run_mcp({"action": "call", "tool": tool, "arguments": args}, comfyui_url)
    if action == "proxy-status":
        return {"ok": True, "action": action, **_proxy_health(v2_url)}
    if action == "proxy-start":
        return {"ok": True, "action": action, **proxy_start(comfyui_url, v2_url)}
    if action == "proxy-stop":
        return {"ok": True, "action": action, **proxy_stop(v2_url)}
    if action == "v2-request":
        return v2_request(v2_url, str(req.get("method") or "GET"), str(req.get("path") or "/api/v2/health"), req.get("body"))
    raise RuntimeErrorDetail(f"unknown Story-Film Comfy action: {action}")


def _read_request_stdin() -> dict[str, Any]:
    try:
        obj = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeErrorDetail("request stdin must be JSON") from exc
    if not isinstance(obj, dict):
        raise RuntimeErrorDetail("request must be a JSON object")
    return obj


def main() -> int:
    ap = argparse.ArgumentParser(description="Story-Film managed official Comfy runtime")
    sub = ap.add_subparsers(dest="command", required=True)
    req = sub.add_parser("request")
    req.add_argument("--project")
    ensure = sub.add_parser("ensure")
    ensure.add_argument("--upgrade", action="store_true")
    ensure.add_argument("--project")
    doctor = sub.add_parser("doctor")
    doctor.add_argument("--project")
    sub.add_parser("_mcp")
    args = ap.parse_args()
    try:
        if args.command == "_mcp":
            payload = _read_request_stdin()
            request = payload.get("request")
            comfyui_url = payload.get("comfyui_url")
            if not isinstance(request, dict) or not isinstance(comfyui_url, str):
                raise RuntimeErrorDetail("invalid internal MCP request")
            _emit(_internal_mcp(request, comfyui_url))
            return 0
        if args.command == "ensure":
            _emit({"ok": True, "runtime": ensure_runtime(upgrade=args.upgrade), "comfyui_url": resolve_comfyui_url(args.project)})
            return 0
        if args.command == "doctor":
            _emit(dispatch_request({"action": "doctor"}, project=args.project))
            return 0
        if args.command == "request":
            _emit(dispatch_request(_read_request_stdin(), project=args.project))
            return 0
    except (RuntimeErrorDetail, subprocess.TimeoutExpired, OSError) as exc:
        _emit({"ok": False, "error": str(exc), "type": type(exc).__name__})
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
