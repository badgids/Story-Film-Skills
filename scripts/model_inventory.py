#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Poll ComfyUI model folders and build a user-facing Story-Film selection inventory."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from comfyui_control import Client, resolve_url
from model_preferences import PROCESS_SPECS, load as load_preferences

SCHEMA_VERSION = 1
MODEL_INPUT_TOKENS = ("model", "ckpt", "checkpoint", "vae", "clip", "encoder", "lora", "upscale", "control", "unet", "diffusion", "audio", "tts", "voice", "interpolation")
PRIMARY_WEIGHT_FOLDERS = ("checkpoints", "diffusion_models", "unet", "diffusers")
FOLDER_PREFIXES = {
    "checkpoints": "C",
    "diffusion_models": "D",
    "unet": "UN",
    "diffusers": "DF",
    "vae": "V",
    "text_encoders": "T",
    "loras": "L",
    "clip_vision": "CV",
    "controlnet": "CN",
    "audio_encoders": "AE",
    "upscale_models": "U",
    "latent_upscale_models": "LU",
    "frame_interpolation": "F",
    "style_models": "S",
    "embeddings": "E",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def json_path(root: Path) -> Path:
    return root / "00_project/comfyui_model_inventory.json"


def markdown_path(root: Path) -> Path:
    return root / "00_project/comfyui_model_inventory.md"


def inventory_resource_count(folders: dict[str, Any]) -> int:
    total = 0
    for row in folders.values():
        if isinstance(row, dict) and isinstance(row.get("models"), list):
            total += len(row["models"])
    return total


def registry_warnings(folders: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if not folders:
        warnings.append("ComfyUI returned no model folder categories from /models.")
    elif inventory_resource_count(folders) == 0:
        warnings.append(
            "ComfyUI returned model folder categories but no model filenames. "
            "Treat this as a live registry/discovery blocker. Do not infer that the user has no models, "
            "do not scan the filesystem, and do not create mock media."
        )
    return warnings


def extract_node_choices(info: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for node_class, schema in sorted(info.items(), key=lambda item: str(item[0]).casefold()):
        if not isinstance(schema, dict):
            continue
        input_schema = schema.get("input") if isinstance(schema.get("input"), dict) else {}
        for section in ("required", "optional"):
            fields = input_schema.get(section) if isinstance(input_schema.get(section), dict) else {}
            for name, spec in fields.items():
                low = str(name).lower()
                if not any(token in low for token in MODEL_INPUT_TOKENS):
                    continue
                if not isinstance(spec, (list, tuple)) or not spec:
                    continue
                choices = spec[0]
                if not isinstance(choices, list) or not choices or any(not isinstance(x, str) for x in choices):
                    continue
                rows.append({
                    "key": f"node:{node_class}:{name}",
                    "node_class": str(node_class),
                    "input": str(name),
                    "section": section,
                    "choices": sorted({str(x) for x in choices}, key=str.casefold),
                })
    return rows


def scan(root: Path, url: str, timeout: float = 20.0) -> dict[str, Any]:
    client = Client(resolve_url(url), timeout=timeout)
    folders: dict[str, Any] = {}
    for folder in sorted(client.model_types(), key=str.casefold):
        try:
            names = sorted(client.models(folder), key=str.casefold)
            folders[folder] = {"count": len(names), "models": names}
        except Exception as exc:
            folders[folder] = {"count": 0, "models": [], "error": str(exc)}
    try:
        node_choices = extract_node_choices(client.object_info())
    except Exception:
        node_choices = []
    obj = {
        "schema_version": SCHEMA_VERSION,
        "server": client.base_url,
        "captured_at": now_iso(),
        "discovery_method": "comfyui-model-registry",
        "registry_endpoints": ["/models", "/models/{folder}"],
        "filesystem_scan_used": False,
        "external_model_paths_supported": True,
        "folders": folders,
        "resource_count": inventory_resource_count(folders),
        "node_choices": node_choices,
        "warnings": registry_warnings(folders),
    }
    json_path(root).parent.mkdir(parents=True, exist_ok=True)
    json_path(root).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown_path(root).write_text(render_inventory(obj), encoding="utf-8")
    return obj


def load(root: Path) -> dict[str, Any]:
    path = json_path(root)
    if not path.is_file():
        raise FileNotFoundError(f"{path} does not exist; run model_inventory.py scan first")
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or obj.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("invalid ComfyUI model inventory")
    return obj


def folder_models(obj: dict[str, Any], folder: str) -> list[str]:
    folders = obj.get("folders") if isinstance(obj.get("folders"), dict) else {}
    row = folders.get(folder)
    if isinstance(row, dict) and isinstance(row.get("models"), list):
        return [str(x) for x in row["models"]]
    return []


def inventory_summary(obj: dict[str, Any]) -> dict[str, Any]:
    folders = obj.get("folders") if isinstance(obj.get("folders"), dict) else {}
    nonempty = [
        folder for folder in sorted(folders, key=str.casefold)
        if folder_models(obj, folder)
    ]
    primary = {
        folder: folder_models(obj, folder)
        for folder in PRIMARY_WEIGHT_FOLDERS
        if folder_models(obj, folder)
    }
    node_choices = obj.get("node_choices") if isinstance(obj.get("node_choices"), list) else []
    model_choice_rows = []
    for row in node_choices:
        if not isinstance(row, dict):
            continue
        key_text = f"{row.get('node_class', '')} {row.get('input', '')}".lower()
        if any(token in key_text for token in ("model", "ckpt", "checkpoint", "unet", "diffusion")):
            model_choice_rows.append(row)
    return {
        "folder_count": len(folders),
        "resource_count": int(obj.get("resource_count", 0) or 0),
        "nonempty_folders": nonempty,
        "primary_weight_folders": list(PRIMARY_WEIGHT_FOLDERS),
        "primary_weight_models": primary,
        "model_choice_rows": model_choice_rows,
        "warnings": obj.get("warnings", []) if isinstance(obj.get("warnings"), list) else [],
    }


def _query_terms(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", value.casefold())


def search_inventory(
    obj: dict[str, Any],
    query: str = "",
    folder: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    limit = max(1, min(int(limit), 500))
    terms = _query_terms(query)
    wanted_folder = folder.casefold() if isinstance(folder, str) and folder.strip() else None
    matches: list[dict[str, Any]] = []
    folders = obj.get("folders") if isinstance(obj.get("folders"), dict) else {}
    for folder_name in sorted(folders, key=str.casefold):
        if wanted_folder and folder_name.casefold() != wanted_folder:
            continue
        for name in folder_models(obj, folder_name):
            haystack = f"{folder_name} {name}".casefold()
            if terms and not all(term in haystack for term in terms):
                continue
            matches.append({"source": "registry-folder", "folder": folder_name, "name": name})
    if not wanted_folder:
        rows = obj.get("node_choices") if isinstance(obj.get("node_choices"), list) else []
        for row in rows:
            if not isinstance(row, dict):
                continue
            choices = row.get("choices") if isinstance(row.get("choices"), list) else []
            for name in choices:
                haystack = f"{row.get('node_class', '')} {row.get('input', '')} {name}".casefold()
                if terms and not all(term in haystack for term in terms):
                    continue
                matches.append({
                    "source": "node-choice",
                    "key": row.get("key"),
                    "node_class": row.get("node_class"),
                    "input": row.get("input"),
                    "name": str(name),
                })
    matches.sort(key=lambda row: (str(row.get("name", "")).casefold(), str(row.get("folder", "")).casefold(), str(row.get("key", "")).casefold()))
    total = len(matches)
    return {
        "query": query,
        "folder": folder or "",
        "total": total,
        "shown": min(total, limit),
        "matches": matches[:limit],
    }


def render_inventory(obj: dict[str, Any]) -> str:
    lines = [
        "# ComfyUI Model Inventory",
        "",
        f"Server: `{obj.get('server', '')}`",
        "",
        f"Captured: `{obj.get('captured_at', '')}`",
        "",
        "This file contains model names returned by the running ComfyUI server. Story-Film Skills does not choose these files for you.",
        "",
        "The ComfyUI model registry is authoritative. It includes model directories that ComfyUI registered from `extra_model_paths.yaml` and other supported startup configuration. Story-Film does not scan the local filesystem to rediscover those paths.",
        "",
        f"Total server-reported model resources: `{obj.get('resource_count', 0)}`",
        "",
    ]
    for warning in obj.get("warnings", []) if isinstance(obj.get("warnings"), list) else []:
        lines.extend([f"> WARNING: {warning}", ""])
    folders = obj.get("folders") if isinstance(obj.get("folders"), dict) else {}
    for folder in sorted(folders, key=str.casefold):
        row = folders[folder]
        models = row.get("models", []) if isinstance(row, dict) else []
        lines.extend([f"## {folder}", ""])
        if not models:
            lines.append("No models were reported in this folder.")
        else:
            for i, name in enumerate(models, 1):
                lines.append(f"{i}. `{name}`")
        lines.append("")
    node_choices = obj.get("node_choices") if isinstance(obj.get("node_choices"), list) else []
    if node_choices:
        lines.extend(["## Model choices exposed by installed nodes", ""])
        for row in node_choices:
            lines.append(f"### `{row.get('node_class')}` / `{row.get('input')}`")
            lines.append("")
            for i, name in enumerate(row.get("choices", []), 1):
                lines.append(f"{i}. `{name}`")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_menu(root: Path, obj: dict[str, Any], process_id: str | None = None) -> str:
    prefs = load_preferences(root)
    wanted = [process_id] if process_id else list(PROCESS_SPECS)
    lines = [
        "# Story-Film Generation Model Selection",
        "",
        "Choose the adapter/model family and the exact ComfyUI resources you want for each process.",
        "The lists below come from the current ComfyUI server inventory.",
        "",
    ]
    processes = prefs.get("processes", {}) if isinstance(prefs.get("processes"), dict) else {}
    folders = obj.get("folders") if isinstance(obj.get("folders"), dict) else {}
    for pid in wanted:
        if pid not in PROCESS_SPECS:
            raise ValueError(f"unknown process {pid!r}")
        spec = PROCESS_SPECS[pid]
        process = processes.get(pid, {}) if isinstance(processes.get(pid), dict) else {}
        selected = process.get("selected_adapter") or "not selected"
        lines.extend([
            f"## {spec['label']} (`{pid}`)",
            "",
            f"Current adapter/model family: `{selected}`",
            "",
            "### Adapter/model family",
            "",
        ])
        known = spec.get("known_adapters", [])
        if not known:
            lines.append("No Story-Film adapter is forced for this process. You can name the adapter or workflow family that you want to use.")
        else:
            for i, adapter in enumerate(known, 1):
                suffix = " (default)" if adapter == spec.get("default_adapter") else ""
                lines.append(f"A{i}. `{adapter}`{suffix}")
        lines.extend(["", "### Installed ComfyUI resources", ""])
        relevant = list(dict.fromkeys(spec.get("resource_folders", [])))
        extra = [f for f in folders if f not in relevant and folder_models(obj, f)]
        for folder in relevant + extra:
            models = folder_models(obj, folder)
            if not models and folder not in folders:
                continue
            lines.extend([f"#### {folder}", ""])
            if not models:
                lines.append("No installed resources reported.")
            else:
                prefix = FOLDER_PREFIXES.get(folder, "X")
                for i, name in enumerate(models, 1):
                    lines.append(f"{prefix}{i}. `{name}`")
            lines.append("")
        node_choices = obj.get("node_choices") if isinstance(obj.get("node_choices"), list) else []
        if node_choices:
            lines.extend(["### Model choices exposed by installed ComfyUI nodes", ""])
            for row in node_choices:
                lines.append(f"`{row.get('key')}`")
                for i, name in enumerate(row.get("choices", []), 1):
                    lines.append(f"N{i}. `{name}`")
                lines.append("")
        lines.extend([
            "You can select zero, one, or more resources from a folder when the workflow supports them.",
            "LoRA selections also record model and CLIP strengths.",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Poll ComfyUI models and print Story-Film selection menus.")
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("scan")
    p.add_argument("project_dir")
    p.add_argument("--url")
    p.add_argument("--timeout", type=float, default=20.0)
    p = sub.add_parser("show")
    p.add_argument("project_dir")
    p.add_argument("--folder")
    p = sub.add_parser("menu")
    p.add_argument("project_dir")
    p.add_argument("--process", choices=sorted(PROCESS_SPECS))
    args = ap.parse_args()
    root = Path(args.project_dir).expanduser().resolve()
    if args.command == "scan":
        obj = scan(root, resolve_url(args.url), args.timeout)
        print(json.dumps({
            "inventory": str(json_path(root)),
            "markdown": str(markdown_path(root)),
            "folder_count": len(obj["folders"]),
            "resource_count": obj.get("resource_count", 0),
            "warnings": obj.get("warnings", []),
        }, indent=2))
        return 0
    obj = load(root)
    if args.command == "show":
        if args.folder:
            print(json.dumps({args.folder: folder_models(obj, args.folder)}, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(obj, indent=2, ensure_ascii=False))
        return 0
    print(render_menu(root, obj, args.process), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
