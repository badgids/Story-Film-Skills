#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Workflow-first ComfyUI source catalog and durable selection for Story-Film Skills."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LIBRARY_ROOT = ROOT / "comfyui_workflows"
PROJECT_DEFAULTS = Path("04_generation/comfyui/default_workflows")
PROJECT_WORKFLOWS = Path("04_generation/comfyui/workflows")
PROJECT_TEMPLATES = Path("04_generation/comfyui/templates")
CATALOG_FILE = Path("00_project/comfyui_workflow_catalog.json")
PREFERENCES_FILE = Path("00_project/workflow_preferences.json")
SOURCES_FILE = Path("00_project/workflow_sources.json")

CATEGORIES = (
    "image",
    "image-edit",
    "video",
    "tts",
    "music",
    "sfx",
    "character-sheet",
    "orbit-sheet",
    "location-orbit",
    "prop-sheet",
    "storyboard",
    "upscale",
    "frame-interpolation",
    "llm",
    "other",
)

CATEGORY_ALIASES = {
    "image_generation": "image",
    "image-generation": "image",
    "image_edit": "image-edit",
    "image-edit-generation": "image-edit",
    "video_generation": "video",
    "video-generation": "video",
    "text-to-speech": "tts",
    "text_to_speech": "tts",
    "voice": "tts",
    "music_generation": "music",
    "sfx_foley": "sfx",
    "sfx-foley": "sfx",
    "character_sheet": "character-sheet",
    "orbit_sheet": "orbit-sheet",
    "location_orbit": "location-orbit",
    "prop_sheet": "prop-sheet",
    "prop-reference": "prop-sheet",
    "prop_reference": "prop-sheet",
    "image_upscaling": "upscale",
    "video_upscaling": "upscale",
    "frame_interpolation": "frame-interpolation",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def project_root(value: str | Path) -> Path:
    root = Path(value).expanduser().resolve()
    if not (root / "00_project").is_dir():
        raise SystemExit(f"not a Story-Film project: {root}")
    return root


def normalize_category(value: str | None) -> str:
    if not value:
        return ""
    raw = value.strip().lower().replace("_", "-")
    raw = CATEGORY_ALIASES.get(value.strip().lower(), CATEGORY_ALIASES.get(raw, raw))
    if raw not in CATEGORIES:
        raise SystemExit(f"unknown workflow category {value!r}; choices: {', '.join(CATEGORIES)}")
    return raw


def safe_name(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip(".-")
    return text or "workflow"


def detect_format(path: Path) -> str:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "invalid"
    if not isinstance(obj, dict):
        return "invalid"
    if isinstance(obj.get("nodes"), list):
        return "ui"
    if any(isinstance(v, dict) and isinstance(v.get("class_type"), str) for v in obj.values()):
        return "api"
    return "unknown"


def infer_category(text: str) -> str:
    s = re.sub(r"[_/\\.-]+", " ", text.casefold())
    if re.search(r"\b(?:tts|text to speech|speech|voice clone|voice design)\b", s):
        return "tts"
    if re.search(r"\b(?:music|song|score)\b", s):
        return "music"
    if re.search(r"\b(?:sfx|foley|sound effect)\b", s):
        return "sfx"
    if "location" in s and re.search(r"\b(?:orbit|turnaround|angles?)\b", s):
        return "location-orbit"
    if "character" in s and re.search(r"\b(?:sheet|turnaround|reference|angles?)\b", s):
        return "character-sheet"
    if "prop" in s and re.search(r"\b(?:sheet|reference|orbit|turnaround|angles?)\b", s):
        return "prop-sheet"
    if re.search(r"\b(?:orbit|multiple angles?|multi angle)\b", s):
        return "orbit-sheet"
    if "storyboard" in s:
        return "storyboard"
    if re.search(r"\b(?:upscale|upscaler|super resolution|superresolution)\b", s):
        return "upscale"
    if re.search(r"\b(?:interpolation|interpolate|rife)\b", s):
        return "frame-interpolation"
    if re.search(r"\b(?:image edit|imageedit|identity edit|reference style|edit image)\b", s):
        return "image-edit"
    if re.search(r"\b(?:llm|text gen|text generation|qwen3vl|qwen3 vl)\b", s):
        return "llm"
    if re.search(r"\b(?:video|i2v|t2v|r2v|ref2v|ref2va|wan2|ltx2|minimax h3)\b", s):
        return "video"
    if re.search(r"\b(?:image|txt2img|text to image|t2i|flux2|krea2)\b", s):
        return "image"
    return "other"


def infer_model(text: str) -> str:
    s = text.casefold()
    patterns = (
        ("MiniMax-H3", r"minimax[\s_.-]*h3|\bh3\b"),
        ("Wan2.2", r"wan[\s_.-]*2[\s_.-]*2|wan22"),
        ("LTX2.5", r"ltx[\s_.-]*2[\s_.-]*5"),
        ("LTX2.3", r"ltx[\s_.-]*2[\s_.-]*3|ltx23"),
        ("Qwen-Image-Edit", r"qwen.*image.*edit|qwen.*edit"),
        ("Qwen-Image-2512", r"qwen.*image.*2512|qwen[\s_.-]*image"),
        ("Qwen3TTS", r"qwen3.*tts"),
        ("Qwen3-VL", r"qwen3.*vl"),
        ("Qwen3.5", r"qwen3[\s_.-]*5"),
        ("Qwen3", r"qwen3"),
        ("Krea2", r"krea[\s_.-]*2|krea2"),
        ("Flux2", r"flux[\s_.-]*2|flux2"),
        ("ACE-Step-XL", r"ace[\s_.-]*step.*xl|acestep.*xl"),
        ("Stable-Audio-3", r"stable.*audio.*3"),
        ("MiniMax-Music-3", r"minimax.*music.*3"),
        ("NVIDIA-RTX", r"rtx.*(?:upscale|super|video)|nvidia.*rtx"),
        ("FILM", r"\bfilm\b.*(?:interpol|frame)|frame.*interpol.*film"),
    )
    for name, rx in patterns:
        if re.search(rx, s):
            return name
    return "Unspecified"


def load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def local_entry(
    *,
    source: str,
    path: Path,
    category: str,
    model: str,
    storage: str,
    display_path: str,
) -> dict[str, Any]:
    return {
        "source": source,
        "category": category,
        "model": model or "Unspecified",
        "name": path.name,
        "path": display_path,
        "storage": storage,
        "format": detect_format(path),
    }


def scan_structured(
    root: Path,
    *,
    source: str,
    storage: str,
    display_prefix: str = "",
    skip_top: set[str] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not root.is_dir():
        return rows
    skip_top = skip_top or set()
    for path in sorted(root.rglob("*.json")):
        rel = path.relative_to(root)
        if not rel.parts or rel.parts[0] in skip_top:
            continue
        if len(rel.parts) >= 3 and rel.parts[0] in CATEGORIES:
            category = rel.parts[0]
            model = rel.parts[1]
        else:
            category = infer_category(rel.as_posix())
            model = infer_model(rel.as_posix())
        display = (Path(display_prefix) / rel).as_posix() if display_prefix else rel.as_posix()
        rows.append(
            local_entry(
                source=source,
                path=path,
                category=category,
                model=model,
                storage=storage,
                display_path=display,
            )
        )
    return rows


def scan_project_loose(root: Path, rel: Path, source: str) -> list[dict[str, Any]]:
    base = root / rel
    rows: list[dict[str, Any]] = []
    if not base.is_dir():
        return rows
    for path in sorted(base.rglob("*.json")):
        relative = path.relative_to(root).as_posix()
        text = relative
        rows.append(
            local_entry(
                source=source,
                path=path,
                category=infer_category(text),
                model=infer_model(text),
                storage="project-relative",
                display_path=relative,
            )
        )
    return rows


def sources_path(root: Path) -> Path:
    return root / SOURCES_FILE


def source_records(root: Path) -> list[dict[str, Any]]:
    obj = load_json(sources_path(root), {"schema_version": 1, "sources": []})
    rows = obj.get("sources", []) if isinstance(obj, dict) else []
    return [dict(x) for x in rows if isinstance(x, dict)]


def scan_external(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []
    for index, record in enumerate(source_records(root), 1):
        raw = str(record.get("path") or "").strip()
        if not raw:
            continue
        source_path = Path(raw).expanduser()
        if not source_path.is_absolute():
            source_path = (root / source_path).resolve()
        else:
            source_path = source_path.resolve()
        category_override = normalize_category(str(record.get("category") or "")) if record.get("category") else ""
        model_override = str(record.get("model") or "").strip()
        if source_path.is_file():
            candidates = [source_path] if source_path.suffix.lower() == ".json" else []
        elif source_path.is_dir():
            candidates = sorted(source_path.rglob("*.json"))
        else:
            warnings.append(f"external workflow source #{index} is unavailable: {source_path}")
            continue
        for path in candidates:
            label = f"{source_path.name}/{path.relative_to(source_path).as_posix()}" if source_path.is_dir() else path.name
            rows.append(
                local_entry(
                    source="external",
                    path=path,
                    category=category_override or infer_category(label),
                    model=model_override or infer_model(label),
                    storage="absolute",
                    display_path=str(path),
                )
            )
    return rows, warnings


def live_entries(root: Path, url: str) -> tuple[list[dict[str, Any]], list[str]]:
    if not url:
        return [], []
    try:
        from comfyui_control import Client, resolve_url  # type: ignore
        client = Client(resolve_url(url))
        result = client.workflow_catalog(root)
    except Exception as exc:
        return [], [f"live ComfyUI workflow catalog unavailable: {exc}"]

    rows: list[dict[str, Any]] = []
    warnings = list(result.get("warnings", [])) if isinstance(result, dict) else []
    for item in result.get("workflows", []) if isinstance(result, dict) else []:
        if not isinstance(item, dict):
            continue
        raw_source = str(item.get("source") or "")
        if raw_source in {"project-workflow", "project-template"}:
            continue
        source_map = {
            "user": "comfyui-user",
            "core": "comfyui-core-template",
            "custom": "comfyui-custom-template",
        }
        if raw_source not in source_map:
            continue
        text = json.dumps(item, ensure_ascii=False, sort_keys=True)
        model_text = " ".join(str(x) for x in item.get("models", [])) if isinstance(item.get("models"), list) else text
        rows.append(
            {
                "source": source_map[raw_source],
                "category": infer_category(text),
                "model": infer_model(model_text + " " + text),
                "name": str(item.get("name") or item.get("title") or "workflow"),
                "module": str(item.get("module") or ""),
                "format": "remote",
                "remote_source": raw_source,
                "metadata": item,
            }
        )
    return rows, warnings


def dedupe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        key = json.dumps(
            {
                "source": row.get("source"),
                "path": row.get("path"),
                "name": row.get("name"),
                "module": row.get("module"),
            },
            sort_keys=True,
            ensure_ascii=False,
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def build_catalog(
    root: Path,
    *,
    category: str = "",
    query: str = "",
    url: str = "",
    include_generate: bool = True,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []

    rows.extend(
        scan_structured(
            LIBRARY_ROOT,
            source="built-in",
            storage="repo-relative",
            display_prefix="comfyui_workflows",
            skip_top={"custom", "research"},
        )
    )
    rows.extend(
        scan_structured(
            LIBRARY_ROOT / "custom",
            source="package-custom",
            storage="repo-relative",
            display_prefix="comfyui_workflows/custom",
        )
    )
    rows.extend(
        scan_structured(
            root / PROJECT_DEFAULTS,
            source="project-default",
            storage="project-relative",
            display_prefix=PROJECT_DEFAULTS.as_posix(),
        )
    )
    rows.extend(scan_project_loose(root, PROJECT_WORKFLOWS, "project-workflow"))
    rows.extend(scan_project_loose(root, PROJECT_TEMPLATES, "project-template"))

    external_rows, external_warnings = scan_external(root)
    rows.extend(external_rows)
    warnings.extend(external_warnings)

    remote_rows, remote_warnings = live_entries(root, url)
    rows.extend(remote_rows)
    warnings.extend(remote_warnings)

    rows = dedupe(rows)
    wanted = normalize_category(category) if category else ""
    if wanted:
        rows = [row for row in rows if row.get("category") == wanted]

    needle = query.casefold().strip()
    if needle:
        rows = [
            row
            for row in rows
            if needle in json.dumps(row, ensure_ascii=False, sort_keys=True).casefold()
        ]

    priority = {
        "project-default": 0,
        "package-custom": 1,
        "built-in": 2,
        "project-workflow": 3,
        "project-template": 4,
        "comfyui-user": 5,
        "comfyui-core-template": 6,
        "comfyui-custom-template": 7,
        "external": 8,
        "generate-new": 9,
    }
    rows.sort(
        key=lambda row: (
            priority.get(str(row.get("source")), 99),
            str(row.get("model", "")).casefold(),
            str(row.get("name", "")).casefold(),
        )
    )

    if wanted and include_generate:
        rows.append(
            {
                "source": "generate-new",
                "category": wanted,
                "model": "Live ComfyUI schemas",
                "name": f"Generate a new {wanted} workflow",
                "format": "generated-candidate",
            }
        )

    numbered: list[dict[str, Any]] = []
    for number, row in enumerate(rows, 1):
        item = dict(row)
        item["number"] = number
        numbered.append(item)

    return {
        "schema_version": 1,
        "generated_at": now(),
        "category": wanted,
        "query": query,
        "comfyui_url": url,
        "count": len(numbered),
        "workflows": numbered,
        "warnings": warnings,
    }


def print_catalog(catalog: dict[str, Any]) -> None:
    category = catalog.get("category") or "all"
    rows = catalog.get("workflows", [])
    print(f"Workflow choices for {category} ({len(rows)}):")
    print()
    for row in rows:
        number = row.get("number")
        source = row.get("source")
        model = row.get("model") or "Unspecified"
        name = row.get("name") or "workflow"
        print(f"{number}. [{source}] {model} - {name}")
        path = row.get("path")
        if path:
            print(f"   {path}")
        module = row.get("module")
        if module:
            print(f"   module: {module}")
    if rows:
        print()
        print("Reply with the number you want to use.")
    for warning in catalog.get("warnings", []):
        print(f"WARNING: {warning}")


def cmd_catalog(args: argparse.Namespace) -> int:
    root = project_root(args.project)
    catalog = build_catalog(
        root,
        category=args.category,
        query=args.query,
        url=args.url,
        include_generate=not args.no_generate,
    )
    write_json(root / CATALOG_FILE, catalog)
    print_catalog(catalog)
    return 0


def cmd_choose(args: argparse.Namespace) -> int:
    root = project_root(args.project)
    catalog = load_json(root / CATALOG_FILE, {})
    rows = catalog.get("workflows", []) if isinstance(catalog, dict) else []
    try:
        number = int(args.number)
    except ValueError as exc:
        raise SystemExit("workflow choice must be a number from the latest catalog") from exc
    selected = next((dict(row) for row in rows if isinstance(row, dict) and row.get("number") == number), None)
    if selected is None:
        raise SystemExit(f"workflow choice {number} is not in the latest catalog")
    category = str(selected.get("category") or catalog.get("category") or "other")
    selected.pop("number", None)
    selected["selected_at"] = now()

    path = root / PREFERENCES_FILE
    prefs = load_json(path, {"schema_version": 1, "selections": {}})
    if not isinstance(prefs, dict):
        prefs = {"schema_version": 1, "selections": {}}
    selections = prefs.setdefault("selections", {})
    if not isinstance(selections, dict):
        selections = {}
        prefs["selections"] = selections
    selections[category] = selected
    prefs["updated_at"] = now()
    write_json(path, prefs)
    print(json.dumps({"category": category, "selection": selected}, indent=2, ensure_ascii=False))
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    root = project_root(args.project)
    print(json.dumps(load_json(root / PREFERENCES_FILE, {"schema_version": 1, "selections": {}}), indent=2, ensure_ascii=False))
    return 0


def cmd_clear(args: argparse.Namespace) -> int:
    root = project_root(args.project)
    category = normalize_category(args.category)
    path = root / PREFERENCES_FILE
    prefs = load_json(path, {"schema_version": 1, "selections": {}})
    selections = prefs.get("selections", {}) if isinstance(prefs, dict) else {}
    if isinstance(selections, dict):
        selections.pop(category, None)
    if not isinstance(prefs, dict):
        prefs = {"schema_version": 1, "selections": {}}
    prefs["updated_at"] = now()
    write_json(path, prefs)
    print(path)
    return 0


def cmd_source_add(args: argparse.Namespace) -> int:
    root = project_root(args.project)
    path = Path(args.path).expanduser()
    path = path.resolve() if path.is_absolute() else (Path.cwd() / path).resolve()
    if not path.exists():
        raise SystemExit(f"workflow source does not exist: {path}")
    if path.is_file() and path.suffix.lower() != ".json":
        raise SystemExit("workflow source file must be a .json file")
    category = normalize_category(args.category) if args.category else ""
    obj = load_json(sources_path(root), {"schema_version": 1, "sources": []})
    if not isinstance(obj, dict):
        obj = {"schema_version": 1, "sources": []}
    sources = obj.setdefault("sources", [])
    if not isinstance(sources, list):
        sources = []
        obj["sources"] = sources
    record = {
        "path": str(path),
        "category": category,
        "model": args.model.strip(),
        "added_at": now(),
    }
    if any(isinstance(row, dict) and str(row.get("path")) == str(path) for row in sources):
        raise SystemExit(f"workflow source is already registered: {path}")
    sources.append(record)
    write_json(sources_path(root), obj)
    print(json.dumps({"number": len(sources), **record}, indent=2, ensure_ascii=False))
    return 0


def cmd_source_list(args: argparse.Namespace) -> int:
    root = project_root(args.project)
    rows = source_records(root)
    for index, row in enumerate(rows, 1):
        print(f"{index}. {row.get('path', '')}")
        if row.get("category") or row.get("model"):
            print(f"   category={row.get('category') or 'auto'} model={row.get('model') or 'auto'}")
    if not rows:
        print("No external workflow sources are registered.")
    return 0


def cmd_source_remove(args: argparse.Namespace) -> int:
    root = project_root(args.project)
    obj = load_json(sources_path(root), {"schema_version": 1, "sources": []})
    rows = obj.get("sources", []) if isinstance(obj, dict) else []
    if not isinstance(rows, list):
        rows = []
    number = int(args.number)
    if number < 1 or number > len(rows):
        raise SystemExit(f"source number must be between 1 and {len(rows)}")
    removed = rows.pop(number - 1)
    obj["sources"] = rows
    write_json(sources_path(root), obj)
    print(json.dumps(removed, indent=2, ensure_ascii=False))
    return 0


def resolve_local_entry(root: Path, selected: dict[str, Any]) -> Path:
    storage = selected.get("storage")
    raw = str(selected.get("path") or "")
    if storage == "repo-relative":
        path = (ROOT / raw).resolve()
    elif storage == "project-relative":
        path = (root / raw).resolve()
    elif storage == "absolute":
        path = Path(raw).expanduser().resolve()
    else:
        raise SystemExit("selected workflow does not have a local source path")
    if not path.is_file():
        raise SystemExit(f"selected workflow source is unavailable: {path}")
    return path


def cmd_materialize(args: argparse.Namespace) -> int:
    root = project_root(args.project)
    category = normalize_category(args.category)
    prefs = load_json(root / PREFERENCES_FILE, {})
    selections = prefs.get("selections", {}) if isinstance(prefs, dict) else {}
    selected = selections.get(category) if isinstance(selections, dict) else None
    if not isinstance(selected, dict):
        raise SystemExit(f"no workflow is selected for {category}")

    source = str(selected.get("source") or "")
    if source == "generate-new":
        raise SystemExit(
            "generate-new is selected. Build one candidate through the bounded live-schema "
            "comfyui-workflow path, save it as a project workflow, refresh the catalog, and choose that real workflow."
        )

    destination = root / PROJECT_TEMPLATES / "selected" / category / safe_name(str(selected.get("name") or "workflow.json"))
    destination.parent.mkdir(parents=True, exist_ok=True)

    if source in {"built-in", "package-custom", "project-default", "project-workflow", "project-template", "external"}:
        src = resolve_local_entry(root, selected)
        if src.resolve() != destination.resolve():
            shutil.copy2(src, destination)
    elif source in {"comfyui-user", "comfyui-core-template", "comfyui-custom-template"}:
        if not args.url:
            raise SystemExit("materializing a ComfyUI-saved/template workflow requires --url")
        try:
            from comfyui_control import Client, resolve_url  # type: ignore
            client = Client(resolve_url(args.url))
            remote_source = str(selected.get("remote_source") or "")
            workflow = client.fetch_workflow_source(
                remote_source,
                str(selected.get("name") or ""),
                module=str(selected.get("module") or "") or None,
            )
        except Exception as exc:
            raise SystemExit(f"could not fetch selected ComfyUI workflow: {exc}") from exc
        destination.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        raise SystemExit(f"unsupported selected workflow source: {source}")

    result = {
        "category": category,
        "source": source,
        "source_name": selected.get("name"),
        "materialized_path": destination.relative_to(root).as_posix(),
        "format": detect_format(destination),
    }
    selected["materialized_path"] = result["materialized_path"]
    selected["materialized_at"] = now()
    prefs["updated_at"] = now()
    write_json(root / PREFERENCES_FILE, prefs)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Catalog and select complete ComfyUI workflows for Story-Film Skills.")
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("catalog", help="Build and print the numbered workflow catalog.")
    p.add_argument("project")
    p.add_argument("--category", default="")
    p.add_argument("--query", default="")
    p.add_argument("--url", default="")
    p.add_argument("--no-generate", action="store_true")
    p.set_defaults(func=cmd_catalog)

    p = sub.add_parser("choose", help="Choose a numbered entry from the most recent catalog.")
    p.add_argument("project")
    p.add_argument("number")
    p.set_defaults(func=cmd_choose)

    p = sub.add_parser("show", help="Show durable workflow selections.")
    p.add_argument("project")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("clear", help="Clear one workflow selection.")
    p.add_argument("project")
    p.add_argument("category")
    p.set_defaults(func=cmd_clear)

    p = sub.add_parser("source-add", help="Register another workflow JSON file or directory.")
    p.add_argument("project")
    p.add_argument("path")
    p.add_argument("--category", default="")
    p.add_argument("--model", default="")
    p.set_defaults(func=cmd_source_add)

    p = sub.add_parser("source-list", help="List registered external workflow sources.")
    p.add_argument("project")
    p.set_defaults(func=cmd_source_list)

    p = sub.add_parser("source-remove", help="Remove a registered external workflow source by number.")
    p.add_argument("project")
    p.add_argument("number", type=int)
    p.set_defaults(func=cmd_source_remove)

    p = sub.add_parser("materialize", help="Copy/fetch the selected workflow into the project.")
    p.add_argument("project")
    p.add_argument("category")
    p.add_argument("--url", default="")
    p.set_defaults(func=cmd_materialize)

    args = ap.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
