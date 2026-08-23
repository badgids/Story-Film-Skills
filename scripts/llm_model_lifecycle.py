#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Deterministic local-model lifecycle for llama.cpp llama-server and Ollama.

This module never shells out to curl/jq and never restarts the model server merely
for model-memory handoff. It snapshots the models resident before generation,
unloads them through the server's native HTTP API, verifies the result, and later
restores that exact set. Models that appeared only while the LLM was absent can be
removed before the original set is restored.
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from llm_runtime import classify_endpoint

SCHEMA_VERSION = 1
NATIVE_RUNTIMES = {"auto", "llama-server", "ollama"}
ENV_ENDPOINTS = (
    "LLAMA_SERVER_URL",
    "LLAMA_SERVER",
    "OLLAMA_HOST",
    "OPENAI_BASE_URL",
    "OPENAI_API_BASE",
)


class LifecycleError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_endpoint(value: str) -> str:
    text = (value or "").strip().rstrip("/")
    if not text:
        return ""
    if "://" not in text:
        text = "http://" + text
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise LifecycleError("local LLM endpoint must be an http(s) URL")
    if parsed.username or parsed.password:
        raise LifecycleError("local LLM endpoint must not contain embedded credentials")
    return text


def _candidate_endpoints(explicit: str) -> list[str]:
    values: list[str] = []
    if explicit.strip():
        values.append(explicit.strip())
    for key in ENV_ENDPOINTS:
        value = os.environ.get(key, "").strip()
        if value and value not in values:
            values.append(value)
    return values


def require_local(endpoint: str) -> str:
    endpoint = normalize_endpoint(endpoint)
    result = classify_endpoint(endpoint)
    if result.get("location") != "local":
        raise LifecycleError(
            "model lifecycle is local-only; the endpoint is not proven local: " + endpoint
        )
    return endpoint


def _request_json(
    endpoint: str,
    path: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    timeout: float = 30,
) -> dict[str, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(endpoint + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[-1000:]
        raise LifecycleError(f"{method} {path} failed with HTTP {exc.code}: {detail}") from exc
    except OSError as exc:
        raise LifecycleError(f"{method} {path} failed: {exc}") from exc
    if not raw:
        return {}
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LifecycleError(f"{method} {path} returned invalid JSON") from exc
    if not isinstance(value, dict):
        raise LifecycleError(f"{method} {path} must return a JSON object")
    return value


def _llama_status(row: dict[str, Any]) -> str:
    status: Any = row.get("status")
    if isinstance(status, dict):
        status = status.get("value") or status.get("status") or status.get("state")
    return str(status or "").strip().lower()


def _llama_rows(endpoint: str, timeout: float) -> list[dict[str, str]]:
    data = _request_json(endpoint, "/models", timeout=timeout)
    rows = data.get("data", [])
    if not isinstance(rows, list):
        raise LifecycleError("llama-server /models response has no data array")
    out: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        model = row.get("id") or row.get("model") or row.get("name")
        if not isinstance(model, str) or not model.strip():
            continue
        out.append({"model": model.strip(), "status": _llama_status(row)})
    return out


def _ollama_rows(endpoint: str, timeout: float) -> list[dict[str, str]]:
    data = _request_json(endpoint, "/api/ps", timeout=timeout)
    rows = data.get("models", [])
    if not isinstance(rows, list):
        raise LifecycleError("Ollama /api/ps response has no models array")
    out: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        model = row.get("name") or row.get("model")
        if isinstance(model, str) and model.strip():
            out.append({"model": model.strip(), "status": "loaded"})
    return out


def _probe(endpoint: str, runtime: str, timeout: float) -> str:
    if runtime == "llama-server":
        _llama_rows(endpoint, timeout)
        return runtime
    if runtime == "ollama":
        _ollama_rows(endpoint, timeout)
        return runtime
    try:
        _llama_rows(endpoint, min(timeout, 5))
        return "llama-server"
    except Exception:
        pass
    try:
        _ollama_rows(endpoint, min(timeout, 5))
        return "ollama"
    except Exception as exc:
        raise LifecycleError(
            "endpoint is local but is neither a compatible llama-server router nor Ollama API"
        ) from exc


def resolve(runtime: str, endpoint: str, timeout: float = 30) -> tuple[str, str]:
    runtime = (runtime or "auto").strip().lower()
    if runtime not in NATIVE_RUNTIMES:
        raise LifecycleError("runtime must be auto, llama-server, or ollama")
    candidates = _candidate_endpoints(endpoint)
    if not candidates:
        raise LifecycleError(
            "no local LLM endpoint was configured; record Pi's active local endpoint in resource_policy.json"
        )
    failures: list[str] = []
    for candidate in candidates:
        try:
            local = require_local(candidate)
            return _probe(local, runtime, timeout), local
        except Exception as exc:
            failures.append(f"{candidate}: {exc}")
    raise LifecycleError("no configured local LLM endpoint could be used: " + " | ".join(failures))


def list_models(runtime: str, endpoint: str, timeout: float = 30) -> dict[str, Any]:
    resolved_runtime, resolved_endpoint = resolve(runtime, endpoint, timeout)
    if resolved_runtime == "llama-server":
        rows = _llama_rows(resolved_endpoint, timeout)
        # Router mode can list unloaded aliases too. Only resident/loading states
        # participate in memory handoff. Missing status is treated conservatively
        # as resident because some server versions omit it for loaded rows.
        resident = [
            row["model"]
            for row in rows
            if row["status"] not in {"unloaded", "not-loaded", "not_loaded", "error", "failed"}
        ]
    else:
        rows = _ollama_rows(resolved_endpoint, timeout)
        resident = [row["model"] for row in rows]
    return {
        "schema_version": SCHEMA_VERSION,
        "runtime": resolved_runtime,
        "endpoint": resolved_endpoint,
        "models": resident,
        "rows": rows,
    }


def _wait_model(
    runtime: str,
    endpoint: str,
    model: str,
    *,
    loaded: bool,
    timeout: float,
) -> None:
    end = time.time() + timeout
    while time.time() < end:
        current = set(list_models(runtime, endpoint, min(10, max(1, end - time.time())))["models"])
        if (model in current) == loaded:
            return
        time.sleep(0.25)
    action = "load" if loaded else "unload"
    raise LifecycleError(f"timed out waiting for {runtime} model to {action}: {model}")


def unload_model(runtime: str, endpoint: str, model: str, timeout: float = 120) -> None:
    runtime, endpoint = resolve(runtime, endpoint, min(timeout, 30))
    if runtime == "llama-server":
        _request_json(
            endpoint,
            "/models/unload",
            method="POST",
            body={"model": model},
            timeout=timeout,
        )
    else:
        _request_json(
            endpoint,
            "/api/generate",
            method="POST",
            body={"model": model, "prompt": "", "stream": False, "keep_alive": 0},
            timeout=timeout,
        )
    _wait_model(runtime, endpoint, model, loaded=False, timeout=timeout)


def load_model(
    runtime: str,
    endpoint: str,
    model: str,
    *,
    keep_alive: str = "5m",
    timeout: float = 300,
) -> None:
    runtime, endpoint = resolve(runtime, endpoint, min(timeout, 30))
    if runtime == "llama-server":
        _request_json(
            endpoint,
            "/models/load",
            method="POST",
            body={"model": model},
            timeout=timeout,
        )
    else:
        _request_json(
            endpoint,
            "/api/generate",
            method="POST",
            body={"model": model, "prompt": "", "stream": False, "keep_alive": keep_alive},
            timeout=timeout,
        )
    _wait_model(runtime, endpoint, model, loaded=True, timeout=timeout)


def snapshot_and_unload(
    runtime: str,
    endpoint: str,
    *,
    state_path: str | Path,
    timeout: float = 120,
) -> dict[str, Any]:
    current = list_models(runtime, endpoint, min(timeout, 30))
    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "runtime": current["runtime"],
        "endpoint": current["endpoint"],
        "models": list(current["models"]),
        "created_at": _now(),
    }
    path = Path(state_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for model in list(snapshot["models"]):
        unload_model(snapshot["runtime"], snapshot["endpoint"], model, timeout=timeout)
    remaining = list_models(snapshot["runtime"], snapshot["endpoint"], min(timeout, 30))["models"]
    if remaining:
        raise LifecycleError("local LLM models remain loaded after unload: " + ", ".join(remaining))
    return snapshot


def restore(
    state: dict[str, Any] | str | Path,
    *,
    keep_alive: str = "5m",
    unload_untracked: bool = True,
    timeout: float = 300,
) -> dict[str, Any]:
    if isinstance(state, (str, Path)):
        path = Path(state)
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise LifecycleError(f"invalid lifecycle snapshot: {path}") from exc
    if not isinstance(state, dict) or state.get("schema_version") != SCHEMA_VERSION:
        raise LifecycleError("lifecycle snapshot has an unsupported schema")
    runtime = str(state.get("runtime") or "")
    endpoint = str(state.get("endpoint") or "")
    targets = [str(x) for x in state.get("models", []) if isinstance(x, str) and x.strip()]
    runtime, endpoint = resolve(runtime, endpoint, min(timeout, 30))
    current = list_models(runtime, endpoint, min(timeout, 30))["models"]
    if unload_untracked:
        for model in list(current):
            if model not in targets:
                unload_model(runtime, endpoint, model, timeout=min(timeout, 120))
    current = list_models(runtime, endpoint, min(timeout, 30))["models"]
    for model in targets:
        if model not in current:
            load_model(runtime, endpoint, model, keep_alive=keep_alive, timeout=timeout)
    final = list_models(runtime, endpoint, min(timeout, 30))["models"]
    missing = [model for model in targets if model not in final]
    extra = [model for model in final if model not in targets]
    if missing or (unload_untracked and extra):
        raise LifecycleError(
            "model restore verification failed; missing=" + repr(missing) + " extra=" + repr(extra)
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "runtime": runtime,
        "endpoint": endpoint,
        "models": final,
        "restored_at": _now(),
    }


def unload_all(runtime: str, endpoint: str, timeout: float = 120) -> dict[str, Any]:
    current = list_models(runtime, endpoint, min(timeout, 30))
    for model in list(current["models"]):
        unload_model(current["runtime"], current["endpoint"], model, timeout=timeout)
    final = list_models(current["runtime"], current["endpoint"], min(timeout, 30))
    if final["models"]:
        raise LifecycleError("models remain loaded: " + ", ".join(final["models"]))
    return {"runtime": current["runtime"], "endpoint": current["endpoint"], "unloaded": current["models"]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic llama-server/Ollama model lifecycle")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("list", "unload-all"):
        p = sub.add_parser(name)
        p.add_argument("--runtime", choices=sorted(NATIVE_RUNTIMES), default="auto")
        p.add_argument("--endpoint", default="")
        p.add_argument("--timeout", type=float, default=120)
    p = sub.add_parser("snapshot-unload")
    p.add_argument("--runtime", choices=sorted(NATIVE_RUNTIMES), default="auto")
    p.add_argument("--endpoint", default="")
    p.add_argument("--state", required=True)
    p.add_argument("--timeout", type=float, default=120)
    p = sub.add_parser("restore")
    p.add_argument("--state", required=True)
    p.add_argument("--keep-alive", default="5m")
    p.add_argument("--timeout", type=float, default=300)
    p.add_argument("--keep-untracked", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "list":
            result = list_models(args.runtime, args.endpoint, args.timeout)
        elif args.command == "unload-all":
            result = unload_all(args.runtime, args.endpoint, args.timeout)
        elif args.command == "snapshot-unload":
            result = snapshot_and_unload(
                args.runtime, args.endpoint, state_path=args.state, timeout=args.timeout
            )
        else:
            result = restore(
                args.state,
                keep_alive=args.keep_alive,
                unload_untracked=not args.keep_untracked,
                timeout=args.timeout,
            )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc), "type": type(exc).__name__}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
