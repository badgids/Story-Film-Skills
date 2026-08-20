#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Manage explicit Story-Film generation process, adapter, and ComfyUI resource choices."""
from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 2
DEFAULT_VIDEO_MODEL = "minimax-h3"
ALLOWED_SOURCES = {"unselected", "default", "user", "user-project", "delegated"}
EXPLICIT_SOURCES = {"user", "user-project", "delegated"}

PROCESS_SPECS: dict[str, dict[str, Any]] = {
    "image_generation": {
        "label": "Image generation",
        "default_adapter": None,
        "known_adapters": ["qwen-image-2512", "krea-2"],
        "resource_folders": ["checkpoints", "diffusion_models", "unet", "diffusers", "vae", "text_encoders", "loras", "clip_vision", "controlnet", "style_models", "embeddings"],
    },
    "image_edit": {
        "label": "Image edit generation",
        "default_adapter": None,
        "known_adapters": ["qwen-image-edit-2511"],
        "resource_folders": ["checkpoints", "diffusion_models", "unet", "diffusers", "vae", "text_encoders", "loras", "clip_vision", "controlnet", "style_models", "embeddings"],
    },
    "video_generation": {
        "label": "Video generation",
        "default_adapter": DEFAULT_VIDEO_MODEL,
        "known_adapters": ["minimax-h3", "ltx-2-5"],
        "resource_folders": ["checkpoints", "diffusion_models", "unet", "diffusers", "vae", "text_encoders", "loras", "clip_vision", "controlnet", "embeddings"],
    },
    "tts": {
        "label": "Text to speech",
        "default_adapter": None,
        "known_adapters": ["qwen3-tts"],
        "resource_folders": ["checkpoints", "diffusion_models", "text_encoders", "audio_encoders", "loras"],
    },
    "music": {
        "label": "Music generation",
        "default_adapter": None,
        "known_adapters": ["ace-step-xl", "minimax-music-3", "stable-audio-3"],
        "resource_folders": ["checkpoints", "diffusion_models", "text_encoders", "audio_encoders", "vae", "loras"],
    },
    "sfx_foley": {
        "label": "SFX and Foley generation",
        "default_adapter": None,
        "known_adapters": ["stable-audio-3"],
        "resource_folders": ["checkpoints", "diffusion_models", "text_encoders", "audio_encoders", "vae", "loras"],
    },
    "image_upscaling": {
        "label": "Image upscaling",
        "default_adapter": None,
        "known_adapters": [],
        "resource_folders": ["upscale_models", "latent_upscale_models"],
    },
    "video_upscaling": {
        "label": "Video upscaling",
        "default_adapter": None,
        "known_adapters": [],
        "resource_folders": ["upscale_models", "latent_upscale_models"],
    },
    "frame_interpolation": {
        "label": "Frame interpolation",
        "default_adapter": None,
        "known_adapters": [],
        "resource_folders": ["frame_interpolation"],
    },
}


def path_for(root: Path) -> Path:
    return root / "00_project/model_preferences.json"


def inventory_path_for(root: Path) -> Path:
    return root / "00_project/comfyui_model_inventory.json"


def empty_process(process_id: str) -> dict[str, Any]:
    spec = PROCESS_SPECS.get(process_id, {"default_adapter": None})
    default_adapter = spec.get("default_adapter")
    process = {
        "default_adapter": default_adapter,
        "selected_adapter": default_adapter,
        "selection_source": "default" if default_adapter else "unselected",
        "user_confirmed": False,
        "allow_agent_substitution": False,
        "profiles": {},
        "overrides": {},
    }
    if default_adapter:
        process["profiles"][default_adapter] = {"resources": {}}
    return process


def default_preferences() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "inventory_source": "00_project/comfyui_model_inventory.json",
        "processes": {process_id: empty_process(process_id) for process_id in PROCESS_SPECS},
    }


def migrate_v1(obj: dict[str, Any]) -> dict[str, Any]:
    out = default_preferences()
    video = obj.get("video") if isinstance(obj.get("video"), dict) else {}
    dst = out["processes"]["video_generation"]
    selected = str(video.get("selected_model") or DEFAULT_VIDEO_MODEL)
    dst["selected_adapter"] = selected
    dst["selection_source"] = video.get("selection_source", "default")
    dst["user_confirmed"] = bool(video.get("user_confirmed", False))
    dst["allow_agent_substitution"] = False
    dst["overrides"] = deepcopy(video.get("shot_overrides", {})) if isinstance(video.get("shot_overrides"), dict) else {}
    dst["profiles"].setdefault(selected, {"resources": {}})
    if video.get("note"):
        dst["note"] = str(video["note"])
    return out


def normalize(obj: dict[str, Any]) -> dict[str, Any]:
    if obj.get("schema_version") == 1:
        return migrate_v1(obj)
    out = deepcopy(obj)
    if out.get("schema_version") != SCHEMA_VERSION:
        return out
    processes = out.setdefault("processes", {})
    for process_id in PROCESS_SPECS:
        if process_id not in processes or not isinstance(processes[process_id], dict):
            processes[process_id] = empty_process(process_id)
    out.setdefault("inventory_source", "00_project/comfyui_model_inventory.json")
    return out


def load(root: Path) -> dict[str, Any]:
    path = path_for(root)
    if not path.exists():
        return default_preferences()
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("model_preferences.json must contain a JSON object")
    return normalize(raw)


def save(root: Path, obj: dict[str, Any]) -> Path:
    path = path_for(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = normalize(obj)
    normalized["schema_version"] = SCHEMA_VERSION
    path.write_text(json.dumps(normalized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_inventory(root: Path) -> dict[str, Any] | None:
    path = inventory_path_for(root)
    if not path.is_file():
        return None
    obj = json.loads(path.read_text(encoding="utf-8"))
    return obj if isinstance(obj, dict) else None


def process_for(obj: dict[str, Any], process_id: str) -> dict[str, Any]:
    if process_id not in PROCESS_SPECS:
        raise ValueError(f"unknown process {process_id!r}; use list-processes")
    processes = obj.setdefault("processes", {})
    process = processes.setdefault(process_id, empty_process(process_id))
    if not isinstance(process, dict):
        raise ValueError(f"process {process_id!r} is not an object")
    return process


def active_adapter(process: dict[str, Any]) -> str | None:
    value = process.get("selected_adapter")
    return str(value) if isinstance(value, str) and value.strip() else None


def profile_for(process: dict[str, Any], adapter: str | None = None, *, create: bool = True) -> dict[str, Any]:
    chosen = adapter or active_adapter(process)
    if not chosen:
        raise ValueError("no adapter/model family is selected for this process")
    profiles = process.setdefault("profiles", {})
    if not isinstance(profiles, dict):
        raise ValueError("profiles must be an object")
    if chosen not in profiles:
        if not create:
            raise ValueError(f"no profile exists for adapter {chosen!r}")
        profiles[chosen] = {"resources": {}}
    profile = profiles[chosen]
    if not isinstance(profile, dict):
        raise ValueError(f"profile {chosen!r} must be an object")
    resources = profile.setdefault("resources", {})
    if not isinstance(resources, dict):
        raise ValueError(f"profile {chosen!r}.resources must be an object")
    return profile


def inventory_models(inventory: dict[str, Any] | None, folder: str) -> set[str] | None:
    if not inventory:
        return None
    if folder.startswith("node:"):
        rows = inventory.get("node_choices") if isinstance(inventory.get("node_choices"), list) else []
        for row in rows:
            if isinstance(row, dict) and row.get("key") == folder:
                values = row.get("choices", [])
                return {str(x) for x in values} if isinstance(values, list) else set()
        return set()
    folders = inventory.get("folders")
    if not isinstance(folders, dict) or folder not in folders:
        return set()
    row = folders.get(folder)
    if isinstance(row, dict):
        values = row.get("models", [])
    else:
        values = row
    return {str(x) for x in values} if isinstance(values, list) else set()


def validate(obj: dict[str, Any], inventory: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    obj = normalize(obj)
    if obj.get("schema_version") != SCHEMA_VERSION:
        return [f"schema_version must be {SCHEMA_VERSION}"]
    processes = obj.get("processes")
    if not isinstance(processes, dict):
        return ["processes must be an object"]

    for process_id, process in processes.items():
        if process_id not in PROCESS_SPECS:
            errors.append(f"unknown process {process_id!r}")
            continue
        if not isinstance(process, dict):
            errors.append(f"{process_id} must be an object")
            continue
        default_adapter = PROCESS_SPECS[process_id].get("default_adapter")
        if process.get("default_adapter") != default_adapter:
            errors.append(f"{process_id}.default_adapter must be {default_adapter!r}")
        source = process.get("selection_source")
        if source not in ALLOWED_SOURCES:
            errors.append(f"{process_id}.selection_source is invalid")
        if process.get("allow_agent_substitution") is not False:
            errors.append(f"{process_id}.allow_agent_substitution must be false")
        selected = active_adapter(process)
        if not selected and source not in {"unselected"}:
            errors.append(f"{process_id}: no selected_adapter requires selection_source=unselected")
        if selected and not default_adapter and source == "default":
            errors.append(f"{process_id}: an adapter without a declared default requires user or delegated selection")
        if selected and default_adapter and selected != default_adapter and source not in EXPLICIT_SOURCES:
            errors.append(f"{process_id}: a non-default adapter requires explicit user choice or delegated selection")
        if selected and source in EXPLICIT_SOURCES and process.get("user_confirmed") is not True:
            errors.append(f"{process_id}: explicit or delegated adapter selection requires user_confirmed=true")
        profiles = process.get("profiles", {})
        if not isinstance(profiles, dict):
            errors.append(f"{process_id}.profiles must be an object")
            continue
        for adapter, profile in profiles.items():
            check_inventory = inventory if adapter == selected else None
            if not isinstance(profile, dict):
                errors.append(f"{process_id}.profiles.{adapter} must be an object")
                continue
            resources = profile.get("resources", {})
            if not isinstance(resources, dict):
                errors.append(f"{process_id}.profiles.{adapter}.resources must be an object")
                continue
            for folder, values in resources.items():
                if folder == "loras":
                    if not isinstance(values, list):
                        errors.append(f"{process_id}/{adapter}: loras must be an array")
                        continue
                    available = inventory_models(check_inventory, "loras")
                    for row in values:
                        if not isinstance(row, dict) or not str(row.get("name", "")).strip():
                            errors.append(f"{process_id}/{adapter}: each LoRA requires a name")
                            continue
                        name = str(row["name"])
                        for strength_name in ("strength_model", "strength_clip"):
                            strength = row.get(strength_name, 1.0)
                            if not isinstance(strength, (int, float)):
                                errors.append(f"{process_id}/{adapter}: LoRA {name} {strength_name} must be numeric")
                        if available is not None and name not in available:
                            errors.append(f"{process_id}/{adapter}: selected LoRA {name!r} is not in the current ComfyUI inventory")
                    continue
                if not isinstance(values, list) or any(not isinstance(x, str) or not x.strip() for x in values):
                    errors.append(f"{process_id}/{adapter}: resource folder {folder!r} must contain an array of names")
                    continue
                available = inventory_models(check_inventory, folder)
                if available is not None:
                    for name in values:
                        if name not in available:
                            errors.append(f"{process_id}/{adapter}: selected {folder} resource {name!r} is not in the current ComfyUI inventory")
        overrides = process.get("overrides", {})
        if not isinstance(overrides, dict):
            errors.append(f"{process_id}.overrides must be an object")
    return errors


def cmd_show(root: Path) -> int:
    print(json.dumps(load(root), indent=2, ensure_ascii=False))
    return 0


def cmd_list_processes() -> int:
    for process_id, spec in PROCESS_SPECS.items():
        default = spec.get("default_adapter") or "none"
        known = ", ".join(spec.get("known_adapters", [])) or "none"
        print(f"{process_id}: {spec['label']} | default={default} | known adapters={known}")
    return 0


def cmd_set_adapter(root: Path, process_id: str, adapter: str, source: str, note: str) -> int:
    if source not in EXPLICIT_SOURCES:
        raise SystemExit("set-adapter requires --source user, user-project, or delegated")
    obj = load(root)
    process = process_for(obj, process_id)
    process["selected_adapter"] = adapter
    process["selection_source"] = source
    process["user_confirmed"] = True
    process["allow_agent_substitution"] = False
    profile_for(process, adapter, create=True)
    if note:
        process["note"] = note
    errors = validate(obj, load_inventory(root))
    if errors:
        raise SystemExit("; ".join(errors))
    print(save(root, obj))
    return 0


def cmd_reset_process(root: Path, process_id: str) -> int:
    obj = load(root)
    old = process_for(obj, process_id)
    fresh = empty_process(process_id)
    # Keep model-specific profiles so a user can switch back without losing exact VAE/CLIP/LoRA choices.
    if isinstance(old.get("profiles"), dict):
        fresh["profiles"] = deepcopy(old["profiles"])
        default_adapter = fresh.get("default_adapter")
        if default_adapter:
            fresh["profiles"].setdefault(default_adapter, {"resources": {}})
    obj["processes"][process_id] = fresh
    print(save(root, obj))
    return 0


def cmd_set_resource(root: Path, process_id: str, folder: str, values: list[str], adapter: str | None) -> int:
    if folder == "loras":
        raise SystemExit("use add-lora/remove-lora for LoRA selections")
    obj = load(root)
    process = process_for(obj, process_id)
    profile = profile_for(process, adapter)
    profile["resources"][folder] = values
    errors = validate(obj, load_inventory(root))
    if errors:
        raise SystemExit("; ".join(errors))
    print(save(root, obj))
    return 0


def cmd_clear_resource(root: Path, process_id: str, folder: str, adapter: str | None) -> int:
    obj = load(root)
    process = process_for(obj, process_id)
    profile = profile_for(process, adapter)
    profile["resources"].pop(folder, None)
    print(save(root, obj))
    return 0


def cmd_add_lora(root: Path, process_id: str, name: str, adapter: str | None, strength_model: float, strength_clip: float) -> int:
    obj = load(root)
    process = process_for(obj, process_id)
    profile = profile_for(process, adapter)
    rows = profile["resources"].setdefault("loras", [])
    if not isinstance(rows, list):
        raise SystemExit("existing loras selection is not an array")
    rows[:] = [row for row in rows if not isinstance(row, dict) or row.get("name") != name]
    rows.append({"name": name, "strength_model": strength_model, "strength_clip": strength_clip})
    errors = validate(obj, load_inventory(root))
    if errors:
        raise SystemExit("; ".join(errors))
    print(save(root, obj))
    return 0


def cmd_remove_lora(root: Path, process_id: str, name: str, adapter: str | None) -> int:
    obj = load(root)
    process = process_for(obj, process_id)
    profile = profile_for(process, adapter)
    rows = profile["resources"].get("loras", [])
    if isinstance(rows, list):
        profile["resources"]["loras"] = [row for row in rows if not isinstance(row, dict) or row.get("name") != name]
    print(save(root, obj))
    return 0


def cmd_validate(root: Path) -> int:
    errors = validate(load(root), load_inventory(root))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK")
    return 0


def cmd_migrate(root: Path) -> int:
    print(save(root, load(root)))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Manage Story-Film generation model and ComfyUI resource preferences.")
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list-processes")

    for name in ("show", "validate", "migrate"):
        p = sub.add_parser(name)
        p.add_argument("project_dir")

    p = sub.add_parser("set-adapter")
    p.add_argument("project_dir")
    p.add_argument("process", choices=sorted(PROCESS_SPECS))
    p.add_argument("adapter")
    p.add_argument("--source", choices=sorted(EXPLICIT_SOURCES), default="user")
    p.add_argument("--note", default="")

    p = sub.add_parser("reset-process")
    p.add_argument("project_dir")
    p.add_argument("process", choices=sorted(PROCESS_SPECS))

    p = sub.add_parser("set-resource")
    p.add_argument("project_dir")
    p.add_argument("process", choices=sorted(PROCESS_SPECS))
    p.add_argument("folder")
    p.add_argument("values", nargs="+")
    p.add_argument("--adapter")

    p = sub.add_parser("clear-resource")
    p.add_argument("project_dir")
    p.add_argument("process", choices=sorted(PROCESS_SPECS))
    p.add_argument("folder")
    p.add_argument("--adapter")

    p = sub.add_parser("add-lora")
    p.add_argument("project_dir")
    p.add_argument("process", choices=sorted(PROCESS_SPECS))
    p.add_argument("name")
    p.add_argument("--adapter")
    p.add_argument("--strength-model", type=float, default=1.0)
    p.add_argument("--strength-clip", type=float, default=1.0)

    p = sub.add_parser("remove-lora")
    p.add_argument("project_dir")
    p.add_argument("process", choices=sorted(PROCESS_SPECS))
    p.add_argument("name")
    p.add_argument("--adapter")

    # Backward-compatible aliases from v0.0.13.
    p = sub.add_parser("set-video")
    p.add_argument("project_dir")
    p.add_argument("model")
    p.add_argument("--source", choices=sorted(EXPLICIT_SOURCES), default="user")
    p.add_argument("--note", default="")

    p = sub.add_parser("reset-video")
    p.add_argument("project_dir")

    args = ap.parse_args()
    if args.command == "list-processes":
        return cmd_list_processes()
    root = Path(args.project_dir).expanduser().resolve()
    if args.command == "show":
        return cmd_show(root)
    if args.command == "validate":
        return cmd_validate(root)
    if args.command == "migrate":
        return cmd_migrate(root)
    if args.command == "set-adapter":
        return cmd_set_adapter(root, args.process, args.adapter, args.source, args.note)
    if args.command == "reset-process":
        return cmd_reset_process(root, args.process)
    if args.command == "set-resource":
        return cmd_set_resource(root, args.process, args.folder, args.values, args.adapter)
    if args.command == "clear-resource":
        return cmd_clear_resource(root, args.process, args.folder, args.adapter)
    if args.command == "add-lora":
        return cmd_add_lora(root, args.process, args.name, args.adapter, args.strength_model, args.strength_clip)
    if args.command == "remove-lora":
        return cmd_remove_lora(root, args.process, args.name, args.adapter)
    if args.command == "set-video":
        return cmd_set_adapter(root, "video_generation", args.model, args.source, args.note)
    if args.command == "reset-video":
        return cmd_reset_process(root, "video_generation")
    raise SystemExit(f"unknown command {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
