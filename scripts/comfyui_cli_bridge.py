#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Any


def comfy_bin() -> str:
    explicit = os.getenv("COMFY_BIN")
    if explicit:
        p = Path(explicit).expanduser()
        if p.is_file():
            return str(p)
        raise FileNotFoundError(f"COMFY_BIN does not exist: {p}")
    found = shutil.which("comfy")
    if not found:
        raise FileNotFoundError("comfy-cli is not installed or `comfy` is not on PATH")
    return found


def safe_model_url(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        raise ValueError("model URL must be an http(s) URL")
    if parts.username or parts.password:
        raise ValueError("model URL must not contain embedded credentials")
    sensitive = {"token", "api_key", "apikey", "key", "authorization", "auth", "access_token"}
    for key, _ in urllib.parse.parse_qsl(parts.query, keep_blank_values=True):
        if key.lower() in sensitive or "token" in key.lower() or "secret" in key.lower():
            raise ValueError(
                "model URL contains credential-like query data; configure provider credentials through comfy-cli instead"
            )
    return url


def parse_output(text: str) -> Any:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        lines = [x for x in stripped.splitlines() if x.strip()]
        for line in reversed(lines):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
        return {"text": stripped}


def run_cli(args: list[str], *, where_local: bool = False, timeout: float | None = None) -> dict[str, Any]:
    cmd = [comfy_bin()]
    if where_local:
        cmd += ["--where", "local"]
    cmd += ["--json"] + args
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, check=False)
    result = {
        "command": [Path(cmd[0]).name] + cmd[1:],
        "returncode": proc.returncode,
        "stdout": parse_output(proc.stdout),
        "stderr": proc.stderr.strip(),
    }
    if proc.returncode != 0:
        result["ok"] = False
    else:
        result["ok"] = True
    return result


def require_confirmation(confirm: bool, action: str) -> None:
    if not confirm:
        raise PermissionError(
            f"{action} changes the ComfyUI execution environment. "
            "Run it only after explicit user approval and pass --confirm."
        )


def reject_all(values: list[str], action: str) -> None:
    if any(str(v).strip().lower() == "all" for v in values):
        raise ValueError(f"{action} refuses the broad target 'all'; name exact packages instead")


def main() -> int:
    ap = argparse.ArgumentParser(description="Stable narrow bridge to official comfy-cli.")
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("info")
    sub.add_parser("which")
    sub.add_parser("env")

    p = sub.add_parser("launch")
    p.add_argument("--foreground", action="store_true")

    sub.add_parser("stop")

    p = sub.add_parser("run")
    p.add_argument("--workflow", required=True)
    p.add_argument("--wait", action="store_true")

    p = sub.add_parser("job-status")
    p.add_argument("prompt_id")

    p = sub.add_parser("job-wait")
    p.add_argument("prompt_id")

    p = sub.add_parser("download")
    p.add_argument("prompt_id")
    p.add_argument("--out-dir", required=True)

    sub.add_parser("system-stats")
    sub.add_parser("discover")

    p = sub.add_parser("templates-list")
    p.add_argument("--type")
    p.add_argument("--limit", type=int)

    p = sub.add_parser("templates-fetch")
    p.add_argument("name")
    p.add_argument("--out", required=True)

    p = sub.add_parser("nodes-list")
    p.add_argument("--produces")
    p.add_argument("--category")
    p.add_argument("--limit", type=int)
    p.add_argument("--exclude-deprecated", action="store_true")

    p = sub.add_parser("nodes-show")
    p.add_argument("name")

    p = sub.add_parser("nodes-path")
    p.add_argument("source_type")
    p.add_argument("dest_type")

    p = sub.add_parser("workflow-slots")
    p.add_argument("workflow")

    p = sub.add_parser("workflow-notes")
    p.add_argument("workflow")

    p = sub.add_parser("workflow-decompose")
    p.add_argument("workflow")
    p.add_argument("--name", required=True)

    p = sub.add_parser("workflow-compose")
    p.add_argument("blueprint")

    p = sub.add_parser("models-list-folders")

    p = sub.add_parser("models-list-folder")
    p.add_argument("folder")
    p.add_argument("--limit", type=int)

    p = sub.add_parser("models-search")
    p.add_argument("--text")
    p.add_argument("--type")
    p.add_argument("--limit", type=int, default=20)

    p = sub.add_parser("models-show")
    p.add_argument("name")

    p = sub.add_parser("model-download")
    p.add_argument("--url", required=True)
    p.add_argument("--relative-path")
    p.add_argument("--filename")
    p.add_argument("--background", action="store_true")
    p.add_argument("--confirm", action="store_true")

    p = sub.add_parser("node-deps")
    p.add_argument("names", nargs="*")

    p = sub.add_parser("node-install")
    p.add_argument("names", nargs="+")
    p.add_argument("--confirm", action="store_true")

    p = sub.add_parser("node-reinstall")
    p.add_argument("names", nargs="+")
    p.add_argument("--confirm", action="store_true")

    p = sub.add_parser("node-uninstall")
    p.add_argument("names", nargs="+")
    p.add_argument("--confirm", action="store_true")

    p = sub.add_parser("node-update")
    p.add_argument("names", nargs="+")
    p.add_argument("--confirm", action="store_true")

    p = sub.add_parser("node-fix")
    p.add_argument("names", nargs="+")
    p.add_argument("--confirm", action="store_true")

    p = sub.add_parser("deps-in-workflow")
    p.add_argument("--workflow", required=True)
    p.add_argument("--out", required=True)

    p = sub.add_parser("install-deps")
    p.add_argument("--workflow", required=True)
    p.add_argument("--confirm", action="store_true")

    p = sub.add_parser("free")
    p.add_argument("--free-memory", action="store_true")

    args = ap.parse_args()
    try:
        if args.command == "info":
            out = {
                "comfy_bin": comfy_bin(),
                "which": run_cli(["which"]),
                "env": run_cli(["env"]),
            }
        elif args.command == "which":
            out = run_cli(["which"])
        elif args.command == "env":
            out = run_cli(["env"])
        elif args.command == "launch":
            cli_args = ["launch"]
            if not args.foreground:
                cli_args.append("--background")
            out = run_cli(cli_args)
        elif args.command == "stop":
            out = run_cli(["stop"])
        elif args.command == "run":
            cli_args = ["run", "--workflow", str(Path(args.workflow))]
            if args.wait:
                cli_args.append("--wait")
            out = run_cli(cli_args, where_local=True)
        elif args.command == "job-status":
            out = run_cli(["jobs", "status", args.prompt_id], where_local=True)
        elif args.command == "job-wait":
            out = run_cli(["jobs", "wait", args.prompt_id], where_local=True)
        elif args.command == "download":
            out = run_cli(["download", args.prompt_id, "-o", args.out_dir], where_local=True)
        elif args.command == "system-stats":
            out = run_cli(["system-stats"], where_local=True)
        elif args.command == "discover":
            out = run_cli(["discover"], where_local=True)
        elif args.command == "templates-list":
            cli_args = ["templates", "ls"]
            if args.type:
                cli_args += ["--type", args.type]
            if args.limit is not None:
                cli_args += ["--limit", str(args.limit)]
            out = run_cli(cli_args, where_local=True)
        elif args.command == "templates-fetch":
            out = run_cli(["templates", "fetch", args.name, "--out", args.out], where_local=True)
        elif args.command == "nodes-list":
            cli_args = ["nodes", "ls"]
            if args.produces:
                cli_args += ["--produces", args.produces]
            if args.category:
                cli_args += ["--category", args.category]
            if args.limit is not None:
                cli_args += ["--limit", str(args.limit)]
            if args.exclude_deprecated:
                cli_args.append("--exclude-deprecated")
            out = run_cli(cli_args, where_local=True)
        elif args.command == "nodes-show":
            out = run_cli(["nodes", "show", args.name], where_local=True)
        elif args.command == "nodes-path":
            out = run_cli(["nodes", "path", args.source_type, args.dest_type], where_local=True)
        elif args.command == "workflow-slots":
            out = run_cli(["workflow", "slots", args.workflow], where_local=True)
        elif args.command == "workflow-notes":
            out = run_cli(["workflow", "notes", args.workflow], where_local=True)
        elif args.command == "workflow-decompose":
            out = run_cli(["workflow", "decompose", args.workflow, "--name", args.name], where_local=True)
        elif args.command == "workflow-compose":
            out = run_cli(["workflow", "compose", args.blueprint], where_local=True)
        elif args.command == "models-list-folders":
            out = run_cli(["models", "list-folders"], where_local=True)
        elif args.command == "models-list-folder":
            cli_args = ["models", "list-folder", args.folder]
            if args.limit is not None:
                cli_args += ["--limit", str(args.limit)]
            out = run_cli(cli_args, where_local=True)
        elif args.command == "models-search":
            cli_args = ["models", "search"]
            if args.text:
                cli_args += ["--text", args.text]
            if args.type:
                cli_args += ["--type", args.type]
            cli_args += ["--limit", str(args.limit)]
            out = run_cli(cli_args, where_local=True)
        elif args.command == "models-show":
            out = run_cli(["models", "show", args.name], where_local=True)
        elif args.command == "model-download":
            require_confirmation(args.confirm, "Model download")
            cli_args = ["model", "download", "--url", safe_model_url(args.url)]
            if args.relative_path:
                cli_args += ["--relative-path", args.relative_path]
            if args.filename:
                cli_args += ["--filename", args.filename]
            if args.background:
                cli_args.append("--background")
            out = run_cli(cli_args, where_local=True)
        elif args.command == "node-deps":
            out = run_cli(["node", "deps"] + args.names, where_local=True)
        elif args.command in {"node-install", "node-reinstall", "node-uninstall", "node-update", "node-fix"}:
            action = args.command.removeprefix("node-")
            require_confirmation(args.confirm, f"Custom node {action}")
            reject_all(args.names, f"Custom node {action}")
            cli_args = ["node", action]
            if action == "install":
                cli_args.append("--exit-on-fail")
            cli_args += args.names
            out = run_cli(cli_args, where_local=True)
        elif args.command == "deps-in-workflow":
            out = run_cli(["node", "deps-in-workflow", "--workflow", args.workflow, "--output", args.out], where_local=True)
        elif args.command == "install-deps":
            require_confirmation(args.confirm, "Workflow dependency installation")
            out = run_cli(["node", "install-deps", "--workflow", args.workflow], where_local=True)
        elif args.command == "free":
            cli_args = ["free"]
            if args.free_memory:
                cli_args.append("--free-memory")
            out = run_cli(cli_args, where_local=True)
        else:
            raise RuntimeError("unknown command")
        print(json.dumps(out, indent=2, ensure_ascii=False))
        if isinstance(out, dict) and out.get("ok") is False:
            return 1
        return 0
    except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
