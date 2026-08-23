#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Deterministic orchestration around LLM-authored ComfyUI workflows.

The LLM may author one canonical API-format workflow candidate. This module owns
all procedural work around that candidate: source discovery, safe source import,
live registry snapshots, marker contracts, validation, fan-out to per-shot
workflows, offline-batch compilation, and preservation of overwritten workflows.

This module never installs ComfyUI, models, or custom nodes and never writes code
under a ComfyUI custom_nodes directory.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import comfyui_batch
import comfyui_control
import comfy_workflow_runtime
import model_inventory
import resource_handoff
import workflow_catalog as workflow_selection

SCHEMA_VERSION = 1
CONTRACT_REL = "04_generation/comfyui/recovery/workflow_build_contract.json"
SCHEMA_SNAPSHOT_REL = "04_generation/comfyui/recovery/live_node_schemas.json"
RECOVERY_ROOT_REL = "04_generation/comfyui/recovery"
DEFAULT_CANDIDATE_REL = "04_generation/comfyui/candidates/LLM-CANDIDATE.json"
DEFAULT_BATCH_REL = "04_generation/comfyui/offline_batch.json"
DEFAULT_CANONICAL_REL = "04_generation/comfyui/templates/validated/LLM-CANONICAL.json"

PROMPT_MARKER = "__STORY_FILM_PROMPT__"
NEGATIVE_MARKER = "__STORY_FILM_NEGATIVE_PROMPT__"
FILENAME_MARKER = "__STORY_FILM_FILENAME_PREFIX__"

MEDIA_DEFAULTS = {
    "image": {
        "records": "04_generation/image_briefs.jsonl",
        "output_kind": "image",
    },
    "video": {
        "records": "04_generation/video_briefs.jsonl",
        "output_kind": "video",
    },
    "audio": {
        "records": "04_generation/audio_briefs.jsonl",
        "output_kind": "audio",
    },
}

WORKFLOW_PREFERENCES_REL = "00_project/workflow_preferences.json"
MEDIA_WORKFLOW_CATEGORIES = {
    "image": {"image", "image-edit", "character-sheet", "orbit-sheet", "location-orbit", "prop-sheet", "storyboard", "upscale"},
    "video": {"video", "upscale", "frame-interpolation"},
    "audio": {"tts", "music", "sfx"},
}


class WorkflowPipelineError(RuntimeError):
    pass


def _root(project: str | Path) -> Path:
    root = Path(project).expanduser().resolve()
    if not (root / "00_project").is_dir():
        raise WorkflowPipelineError("workflow pipeline requires a Story-Film project with 00_project")
    return root




def _resolve_comfyui_url(root: Path, explicit: str = "") -> str:
    requested = explicit.strip()
    if requested:
        return comfyui_control.resolve_url(requested)
    policy = root / "00_project/resource_policy.json"
    if policy.is_file():
        try:
            obj = json.loads(policy.read_text(encoding="utf-8"))
            comfy = obj.get("comfyui") if isinstance(obj, dict) else None
            value = comfy.get("url") if isinstance(comfy, dict) else None
            if isinstance(value, str) and value.strip():
                return comfyui_control.resolve_url(value.strip())
        except (OSError, json.JSONDecodeError):
            pass
    return comfyui_control.resolve_url(None)


def _rel_path(root: Path, value: str, *, prefixes: tuple[str, ...] = ("04_generation/",)) -> Path:
    raw = str(value or "").strip().replace("\\", "/")
    if not raw or raw.startswith("/") or re.match(r"^[A-Za-z]:/", raw):
        raise WorkflowPipelineError("path must be project-relative")
    rel = Path(raw)
    if ".." in rel.parts:
        raise WorkflowPipelineError("path must not escape the project")
    text = rel.as_posix()
    if prefixes and not any(text.startswith(prefix) for prefix in prefixes):
        raise WorkflowPipelineError("path is outside the allowed Story-Film generation area")
    out = (root / rel).resolve()
    try:
        out.relative_to(root)
    except ValueError as exc:
        raise WorkflowPipelineError("path escapes the Story-Film project") from exc
    return out


def _read_json(path: Path) -> dict[str, Any]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise WorkflowPipelineError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise WorkflowPipelineError(f"invalid JSON file: {path}: {exc}") from exc
    if not isinstance(obj, dict):
        raise WorkflowPipelineError(f"JSON file must contain an object: {path}")
    return obj


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe_name(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-.")
    return clean or "workflow"


def _load_records(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise WorkflowPipelineError(f"generation records do not exist: {path}")
    if path.suffix.lower() == ".jsonl":
        rows: list[dict[str, Any]] = []
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            text = line.strip()
            if not text:
                continue
            try:
                obj = json.loads(text)
            except json.JSONDecodeError as exc:
                raise WorkflowPipelineError(f"invalid JSONL at {path}:{lineno}: {exc}") from exc
            if not isinstance(obj, dict):
                raise WorkflowPipelineError(f"generation record at {path}:{lineno} must be an object")
            rows.append(obj)
        if not rows:
            raise WorkflowPipelineError(f"generation records are empty: {path}")
        return rows
    obj = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(obj, list) and all(isinstance(row, dict) for row in obj):
        return [dict(row) for row in obj]
    if isinstance(obj, dict) and isinstance(obj.get("records"), list) and all(isinstance(row, dict) for row in obj["records"]):
        return [dict(row) for row in obj["records"]]
    raise WorkflowPipelineError("generation records must be JSONL or a JSON array/object with records")




def _records_from_existing_batch(root: Path) -> list[dict[str, Any]]:
    path = root / DEFAULT_BATCH_REL
    if not path.is_file():
        return []
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    jobs = obj.get("jobs") if isinstance(obj, dict) else None
    if not isinstance(jobs, list):
        return []
    rows: list[dict[str, Any]] = []
    for index, job in enumerate(jobs, 1):
        if not isinstance(job, dict):
            continue
        source_ids = [str(x) for x in job.get("source_ids", []) if isinstance(x, str) and x.strip()]
        shot = next((x for x in source_ids if re.fullmatch(r"SHOT-\d{3,}", x, re.I)), "")
        if not shot:
            candidate = str(job.get("job_id") or "")
            shot = candidate if re.fullmatch(r"SHOT-\d{3,}", candidate, re.I) else f"SHOT-{index:03d}"
        rows.append({
            "shot_id": shot,
            "source_ids": source_ids or [shot],
            "_story_film_job": {
                "job_id": str(job.get("job_id") or f"JOB-{index:03d}"),
                "blocked_by": [str(x) for x in job.get("blocked_by", []) if isinstance(x, str)],
                "output_dir": str(job.get("output_dir") or f"04_generation/comfyui/outputs/{shot}"),
                "timeout_s": int(job.get("timeout_s", 1800) or 1800),
                "max_transient_retries": int(job.get("max_transient_retries", 1) or 0),
            },
        })
    return rows


def _discover_records(root: Path, media: str, records_path: str) -> tuple[list[dict[str, Any]], str]:
    explicit = records_path.strip()
    if explicit:
        path = _rel_path(root, explicit)
        return _load_records(path), path.relative_to(root).as_posix()

    existing = _records_from_existing_batch(root)
    if existing:
        return existing, DEFAULT_BATCH_REL

    default_rel = str(MEDIA_DEFAULTS[media]["records"])
    default_path = _rel_path(root, default_rel)
    if default_path.is_file():
        return _load_records(default_path), default_rel

    prompt_root = root / "04_generation/prompts"
    rows: list[dict[str, Any]] = []
    if prompt_root.is_dir():
        seen: set[str] = set()
        for path in sorted(prompt_root.rglob("*.md")):
            text = path.read_text(encoding="utf-8", errors="replace")
            match = re.search(r"(?mi)^SOURCE_ID:\s*([^\r\n]+)", text)
            source_id = match.group(1).strip() if match else path.stem
            shot = source_id if re.fullmatch(r"SHOT-\d{3,}", source_id, re.I) else ""
            key = shot or source_id
            if not key or key in seen:
                continue
            seen.add(key)
            rows.append({"shot_id": shot or f"SHOT-{len(rows)+1:03d}", "source_ids": [source_id]})
    if rows:
        return rows, "04_generation/prompts/**/<source-id>.md"

    raise WorkflowPipelineError(
        "no generation records were found; expected an existing offline batch, a media brief JSON/JSONL file, or prepared prompt artifacts"
    )


def _shot_id(record: dict[str, Any], index: int) -> str:
    for key in ("shot_id", "image_id", "video_id", "audio_id", "id"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            clean = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-.")
            if clean:
                return clean
    return f"SHOT-{index:03d}"


def _record_source_ids(record: dict[str, Any], index: int) -> list[str]:
    values: list[str] = []
    for value in record.get("source_ids", []) if isinstance(record.get("source_ids"), list) else []:
        if isinstance(value, str) and value.strip() and value.strip() not in values:
            values.append(value.strip())
    for key in ("image_id", "video_id", "audio_id", "shot_id", "source_id", "id"):
        value = record.get(key)
        if isinstance(value, str) and value.strip() and value.strip() not in values:
            values.append(value.strip())
    if not values:
        values.append(_shot_id(record, index))
    return values


def _parse_prompt_artifact(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip().upper() == "PROMPT:":
            start = i + 1
            break
    if start is None:
        return ""
    collected: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if re.fullmatch(r"[A-Z][A-Z0-9_ -]*:", stripped):
            break
        collected.append(line.rstrip())
    return "\n".join(collected).strip()


def _prepared_prompt(root: Path, record: dict[str, Any], index: int, query: str) -> tuple[str, str]:
    prompt_root = root / "04_generation/prompts"
    if not prompt_root.is_dir():
        return "", ""
    query_terms = set(re.findall(r"[a-z0-9]+", query.casefold()))
    candidates: list[tuple[int, str, Path]] = []
    for source_id in _record_source_ids(record, index):
        for path in prompt_root.rglob(f"{source_id}.md"):
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            path_terms = set(re.findall(r"[a-z0-9]+", rel.casefold()))
            score = len(query_terms & path_terms)
            candidates.append((score, rel.casefold(), path))
        if candidates:
            # Prefer the most-specific authoritative source ID before trying a
            # secondary ID such as SHOT-###.
            break
    if not candidates:
        return "", ""
    candidates.sort(key=lambda item: (-item[0], item[1]))
    best_score = candidates[0][0]
    best = [item for item in candidates if item[0] == best_score]
    if len(best) > 1:
        names = ", ".join(item[2].relative_to(root).as_posix() for item in best[:8])
        raise WorkflowPipelineError(
            "multiple prepared prompt artifacts match the same source with equal priority: " + names
        )
    path = best[0][2]
    prompt = _parse_prompt_artifact(path)
    if not prompt:
        raise WorkflowPipelineError(f"prepared prompt artifact has no PROMPT section: {path.relative_to(root).as_posix()}")
    return prompt, path.relative_to(root).as_posix()


def _prompt_text(record: dict[str, Any]) -> str:
    for key in ("prompt", "positive_prompt", "generation_prompt"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    fields = (
        ("subject", "subject_description"),
        ("framing", "framing"),
        ("movement", "movement"),
        ("lighting", "lighting"),
        ("palette", "palette_notes"),
        ("continuity", "continuity_constraints"),
    )
    parts = []
    for label, key in fields:
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(f"{label}: {value.strip()}")
    instructions = record.get("generation_instructions")
    if isinstance(instructions, dict):
        priority = instructions.get("quality_priority")
        if isinstance(priority, str) and priority.strip():
            parts.append(f"quality priority: {priority.strip()}")
    if not parts:
        raise WorkflowPipelineError("generation record has no deterministic prompt-bearing fields")
    return "; ".join(parts)


def _negative_text(record: dict[str, Any]) -> str:
    for key in ("negative_prompt", "avoid"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    instructions = record.get("generation_instructions")
    if isinstance(instructions, dict):
        value = instructions.get("avoid")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _replace_markers(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, dict):
        return {str(k): _replace_markers(v, replacements) for k, v in value.items()}
    if isinstance(value, list):
        return [_replace_markers(v, replacements) for v in value]
    if isinstance(value, str):
        out = value
        for marker, replacement in replacements.items():
            out = out.replace(marker, replacement)
        return out
    return value


def _marker_counts(value: Any) -> dict[str, int]:
    counts = {PROMPT_MARKER: 0, NEGATIVE_MARKER: 0, FILENAME_MARKER: 0}
    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            for item in obj.values():
                walk(item)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)
        elif isinstance(obj, str):
            for marker in counts:
                counts[marker] += obj.count(marker)
    walk(value)
    return counts


def _candidate_live_verdict(root: Path, comfyui_url: str, path: Path) -> dict[str, Any]:
    result = comfy_workflow_runtime.workflow_validate(
        root,
        comfyui_url,
        workflow_path=path.relative_to(root).as_posix(),
    )
    verdict = result.get("verdict") if isinstance(result, dict) else None
    if not isinstance(verdict, dict):
        raise WorkflowPipelineError("workflow validator returned an invalid verdict")
    return verdict


def _validate_candidate_contract(workflow: dict[str, Any]) -> None:
    nodes = comfy_workflow_runtime._workflow_nodes(workflow)
    if not nodes:
        raise WorkflowPipelineError("LLM candidate must be an API-format workflow object keyed by node id")
    counts = _marker_counts(workflow)
    if counts[PROMPT_MARKER] < 1:
        raise WorkflowPipelineError(
            f"LLM candidate must contain {PROMPT_MARKER} in at least one prompt-bearing string input"
        )
    if counts[PROMPT_MARKER] > 4:
        raise WorkflowPipelineError("LLM candidate contains an implausible number of prompt markers")
    # Negative and filename markers are optional because not every installed graph
    # exposes those concepts. If present, the deterministic compiler owns them.


def _workflow_source_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (str(row.get("source", "")), str(row.get("module", "")), str(row.get("name", "")))


def _source_candidate_path(index: int, row: dict[str, Any]) -> str:
    source, module, name = _workflow_source_key(row)
    joined = "-".join(x for x in (source, module, name) if x)
    return f"04_generation/comfyui/recovery/sources/{index:02d}-{_safe_name(joined)}.json"


def _selected_workflow_authority(root: Path, media: str, query: str) -> dict[str, Any] | None:
    preferences_path = root / WORKFLOW_PREFERENCES_REL
    if not preferences_path.is_file():
        return None
    obj = _read_json(preferences_path)
    selections = obj.get("selections")
    if not isinstance(selections, dict) or not selections:
        return None

    compatible = MEDIA_WORKFLOW_CATEGORIES[media]
    available = {
        str(category): dict(selection)
        for category, selection in selections.items()
        if str(category) in compatible and isinstance(selection, dict)
    }
    if not available:
        return None

    inferred = workflow_selection.infer_category(query)
    if inferred in available:
        category = inferred
    elif len(available) == 1:
        category = next(iter(available))
    else:
        choices = ", ".join(sorted(available))
        raise WorkflowPipelineError(
            f"multiple durable selected workflows can serve media_type={media}: {choices}; "
            "make the workflow/model query name the intended task category"
        )

    selected = available[category]
    if str(selected.get("source") or "") == "generate-new":
        return {"category": category, "selection": selected, "generate_new": True}

    materialized = str(selected.get("materialized_path") or "").strip()
    if not materialized:
        raise WorkflowPipelineError(
            f"durable selected workflow for {category} has not been materialized; "
            f"run workflow_catalog.py materialize PROJECT {category} before workflow preparation"
        )
    path = _rel_path(
        root,
        materialized,
        prefixes=("04_generation/comfyui/templates/selected/", "04_generation/comfyui/workflows/"),
    )
    if not path.is_file():
        raise WorkflowPipelineError(f"durable selected workflow is missing: {materialized}")
    return {
        "category": category,
        "selection": selected,
        "generate_new": False,
        "path": path.relative_to(root).as_posix(),
        "format": workflow_selection.detect_format(path),
    }


def prepare(
    project: str | Path,
    comfyui_url: str,
    *,
    query: str,
    media_type: str = "image",
    records_path: str = "",
    source_limit: int = 12,
) -> dict[str, Any]:
    root = _root(project)
    media = media_type.strip().lower() or "image"
    if media not in MEDIA_DEFAULTS:
        raise WorkflowPipelineError("media_type must be image, video, or audio")
    query = query.strip()
    if not query:
        raise WorkflowPipelineError("workflow-prepare requires a concrete workflow/model query")
    records, records_origin = _discover_records(root, media, records_path)

    client = comfyui_control.Client(comfyui_control.resolve_url(comfyui_url))
    live_schemas = client.object_info()
    if not isinstance(live_schemas, dict) or not live_schemas:
        raise WorkflowPipelineError("running ComfyUI returned no live node schemas")

    inventory = model_inventory.scan(root, comfyui_url)
    selected_workflow_authority = _selected_workflow_authority(root, media, query)
    if selected_workflow_authority is None:
        catalog = comfy_workflow_runtime.workflow_catalog(root, comfyui_url, query=query)
        rows = catalog.get("workflows", []) if isinstance(catalog, dict) else []
        rows = [dict(row) for row in rows if isinstance(row, dict)]
    elif selected_workflow_authority.get("generate_new"):
        # The user explicitly selected the live-schema generation fallback. Do not
        # independently choose a different existing graph here.
        rows = []
    else:
        selected = selected_workflow_authority["selection"]
        rows = [{
            "source": "project-workflow",
            "name": str(selected.get("name") or Path(selected_workflow_authority["path"]).name),
            "path": selected_workflow_authority["path"],
            "format": selected_workflow_authority.get("format", "unknown"),
            "selected_workflow_authority": True,
            "workflow_category": selected_workflow_authority["category"],
            "original_source": selected.get("source"),
        }]
    source_limit = max(1, min(int(source_limit), 30))

    source_results: list[dict[str, Any]] = []
    valid_existing: list[dict[str, Any]] = []
    finalizable_existing: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    # source_limit is a per-source cap, not a total cap. A pile of stale project
    # workflows must never starve saved-user/core/custom sources from discovery.
    per_source: dict[str, int] = {}
    selected_rows: list[dict[str, Any]] = []
    for row in rows:
        source_name = str(row.get("source", ""))
        if per_source.get(source_name, 0) >= source_limit:
            continue
        key = _workflow_source_key(row)
        if key in seen:
            continue
        seen.add(key)
        per_source[source_name] = per_source.get(source_name, 0) + 1
        selected_rows.append(row)

    for row in selected_rows:
        result = dict(row)
        source = str(row.get("source", ""))
        name = str(row.get("name", ""))
        module = str(row.get("module", ""))
        try:
            if source == "project-workflow":
                path = str(row.get("path") or f"04_generation/comfyui/workflows/{name}")
                verdict = comfy_workflow_runtime.workflow_validate(root, comfyui_url, workflow_path=path)["verdict"]
                result["path"] = path
                result["live_valid"] = bool(verdict.get("valid"))
                result["validation_errors"] = verdict.get("errors", [])
                if result["live_valid"]:
                    valid_existing.append(result)
                    try:
                        _validate_candidate_contract(_read_json(root / result["path"]))
                        finalizable_existing.append(result)
                    except Exception:
                        pass
            else:
                out_rel = _source_candidate_path(len(source_results) + 1, row)
                fetched = comfy_workflow_runtime.workflow_fetch(
                    root,
                    comfyui_url,
                    source=source,
                    name=name,
                    module=module,
                    out_path=out_rel,
                )
                result["path"] = fetched["path"]
                result["format"] = fetched.get("format")
                if fetched.get("format") == "api":
                    verdict = comfy_workflow_runtime.workflow_validate(root, comfyui_url, workflow_path=fetched["path"])["verdict"]
                    result["live_valid"] = bool(verdict.get("valid"))
                    result["validation_errors"] = verdict.get("errors", [])
                    if result["live_valid"]:
                        valid_existing.append(result)
                        try:
                            _validate_candidate_contract(_read_json(root / result["path"]))
                            finalizable_existing.append(result)
                        except Exception:
                            pass
                else:
                    result["live_valid"] = False
                    result["validation_errors"] = ["source is not API-format; LLM may adapt it into the candidate"]
        except Exception as exc:
            result["live_valid"] = False
            result["fetch_or_validation_error"] = str(exc)
        source_results.append(result)

    schema_snapshot = _rel_path(root, SCHEMA_SNAPSHOT_REL)
    _write_json(schema_snapshot, live_schemas)

    contract = {
        "schema_version": SCHEMA_VERSION,
        "query": query,
        "media_type": media,
        "records_path": records_origin,
        "record_count": len(records),
        "candidate_path": DEFAULT_CANDIDATE_REL,
        "canonical_path": DEFAULT_CANONICAL_REL,
        "offline_batch_path": DEFAULT_BATCH_REL,
        "markers": {
            "positive_prompt": PROMPT_MARKER,
            "negative_prompt": NEGATIVE_MARKER,
            "filename_prefix": FILENAME_MARKER,
        },
        "llm_role": [
            "Choose/adapt an existing source or author one canonical API-format workflow candidate.",
            "Use only class_type values and model choices present in the live ComfyUI schemas/inventory.",
            "Place the positive-prompt marker in the exact prompt-bearing string input(s).",
            "Optionally place the negative-prompt and filename-prefix markers in their exact string inputs.",
            "Return the candidate workflow to workflow-finalize. Do not fan out shots, build the offline batch, install nodes, launch ComfyUI, or scan model directories.",
        ],
        "script_role": [
            "Search and preserve existing workflow sources.",
            "Capture live installed node schemas and model inventory.",
            "Reject unknown nodes, invalid inputs/model choices, and incompatible links.",
            "Expand one accepted canonical workflow into per-record runnable workflows.",
            "Build and live-validate the deterministic offline batch.",
            "Preserve overwritten runnable workflows under recovery/quarantine.",
        ],
        "custom_node_policy": {
            "author_custom_nodes": False,
            "install_custom_nodes": False,
            "update_custom_nodes": False,
            "only_if_user_explicitly_requests_separate_action": True,
        },
        "installed_class_types": sorted(str(name) for name in live_schemas),
        "live_node_schemas": schema_snapshot.relative_to(root).as_posix(),
        "model_inventory": model_inventory.json_path(root).relative_to(root).as_posix(),
        "model_summary": model_inventory.inventory_summary(inventory),
        "selected_workflow_authority": selected_workflow_authority or {},
        "source_candidates": source_results,
        "source_limit_per_source": source_limit,
        "source_counts": per_source,
        "valid_existing_sources": valid_existing,
        "direct_finalizable_sources": finalizable_existing,
    }
    if selected_workflow_authority:
        if selected_workflow_authority.get("generate_new"):
            contract["llm_role"][0] = "Author one canonical API-format workflow candidate from the live schemas because the user selected generate-new."
        else:
            contract["llm_role"][0] = "Adapt only the durable selected workflow source when adaptation is required; do not choose another workflow."
    contract_path = _rel_path(root, CONTRACT_REL)
    _write_json(contract_path, contract)
    return {
        "ok": True,
        "action": "prepare",
        "status": "direct-finalizable-source-available" if finalizable_existing else "llm-candidate-required",
        "query": query,
        "media_type": media,
        "record_count": len(records),
        "records_origin": records_origin,
        "contract": contract_path.relative_to(root).as_posix(),
        "candidate_path": DEFAULT_CANDIDATE_REL,
        "live_node_schemas": schema_snapshot.relative_to(root).as_posix(),
        "valid_existing_sources": valid_existing,
        "direct_finalizable_sources": finalizable_existing,
        "source_candidates": source_results,
        "selected_workflow_authority": selected_workflow_authority or {},
        "source_limit_per_source": source_limit,
        "source_counts": per_source,
        "next_step": (
            "Call workflow-finalize with a direct_finalizable_sources path if present. Otherwise adapt a preserved source or author one canonical workflow object using only the build contract, then pass that object to workflow-finalize."
        ),
    }


def _quarantine_existing(root: Path, paths: list[Path]) -> str:
    existing = [path for path in paths if path.is_file()]
    if not existing:
        return ""
    quarantine = _rel_path(root, f"{RECOVERY_ROOT_REL}/quarantine/{_now_stamp()}")
    quarantine.mkdir(parents=True, exist_ok=True)
    for path in existing:
        shutil.copy2(path, quarantine / path.name)
    return quarantine.relative_to(root).as_posix()


def _atomic_replace_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    _write_json(tmp, obj)
    tmp.replace(path)


def _batch_id(root: Path) -> str:
    current = root / DEFAULT_BATCH_REL
    if current.is_file():
        try:
            obj = json.loads(current.read_text(encoding="utf-8"))
            value = str(obj.get("batch_id", "")) if isinstance(obj, dict) else ""
            if re.fullmatch(r"BATCH-\d{3,}", value):
                return value
        except Exception:
            pass
    return "BATCH-001"


def finalize(
    project: str | Path,
    comfyui_url: str,
    *,
    workflow: dict[str, Any] | None = None,
    candidate_path: str = "",
    arm_handoff: bool = True,
) -> dict[str, Any]:
    root = _root(project)
    contract_path = _rel_path(root, CONTRACT_REL)
    contract = _read_json(contract_path)
    media = str(contract.get("media_type") or "image")
    if media not in MEDIA_DEFAULTS:
        raise WorkflowPipelineError("workflow build contract has an invalid media_type")
    records_origin = str(contract.get("records_path") or "")
    if records_origin == DEFAULT_BATCH_REL or records_origin.startswith("04_generation/prompts/"):
        records, _ = _discover_records(root, media, "")
    else:
        records, _ = _discover_records(root, media, records_origin)

    if workflow is not None:
        if not isinstance(workflow, dict):
            raise WorkflowPipelineError("workflow-finalize workflow must be a JSON object")
        candidate = _rel_path(root, str(contract.get("candidate_path") or DEFAULT_CANDIDATE_REL))
        _write_json(candidate, workflow)
    else:
        selected = candidate_path.strip()
        if not selected:
            valid = contract.get("direct_finalizable_sources") if isinstance(contract.get("direct_finalizable_sources"), list) else []
            if len(valid) == 1 and isinstance(valid[0], dict) and isinstance(valid[0].get("path"), str):
                selected = str(valid[0]["path"])
            else:
                selected = str(contract.get("candidate_path") or DEFAULT_CANDIDATE_REL)
        candidate = _rel_path(root, selected)
    canonical_workflow = _read_json(candidate)
    _validate_candidate_contract(canonical_workflow)

    canonical_verdict = _candidate_live_verdict(root, comfyui_url, candidate)
    if not canonical_verdict.get("valid"):
        raise WorkflowPipelineError(
            "LLM candidate failed live validation: " + "; ".join(str(x) for x in canonical_verdict.get("errors", []))
        )

    staging_dir = _rel_path(root, f"{RECOVERY_ROOT_REL}/compiled")
    staging_dir.mkdir(parents=True, exist_ok=True)
    client = comfyui_control.Client(comfyui_control.resolve_url(comfyui_url))
    compiled: list[tuple[str, Path, dict[str, Any]]] = []
    prompt_sources: dict[str, str] = {}
    errors: list[str] = []
    query = str(contract.get("query") or "")
    for index, record in enumerate(records, 1):
        sid = _shot_id(record, index)
        try:
            prepared_prompt, prepared_path = _prepared_prompt(root, record, index, query)
        except Exception as exc:
            errors.append(f"{sid}: prepared prompt resolution failed: {exc}")
            continue
        prompt = prepared_prompt or _prompt_text(record)
        prompt_sources[sid] = prepared_path or "generation-record-fields"
        workflow_obj = _replace_markers(
            canonical_workflow,
            {
                PROMPT_MARKER: prompt,
                NEGATIVE_MARKER: _negative_text(record),
                FILENAME_MARKER: f"story-film/{sid}",
            },
        )
        counts = _marker_counts(workflow_obj)
        unresolved = [marker for marker, count in counts.items() if count]
        if unresolved:
            errors.append(f"{sid}: unresolved workflow markers: {', '.join(unresolved)}")
            continue
        staged = staging_dir / f"{sid}.json"
        _write_json(staged, workflow_obj)
        try:
            verdict = _candidate_live_verdict(root, comfyui_url, staged)
            if not verdict.get("valid"):
                errors.append(f"{sid}: " + "; ".join(str(x) for x in verdict.get("errors", [])))
                continue
        except Exception as exc:
            errors.append(f"{sid}: live validation failed: {exc}")
            continue
        compiled.append((sid, staged, workflow_obj))

    if errors:
        raise WorkflowPipelineError("per-record workflow compilation failed: " + " | ".join(errors[:20]))
    if not compiled:
        raise WorkflowPipelineError("workflow-finalize produced no runnable workflows")

    targets = [root / "04_generation/comfyui/workflows" / f"{sid}.json" for sid, _, _ in compiled]

    # Validate the complete batch against the staged, already-live-validated files
    # before touching any runnable workflow. This keeps failures transactional.
    expected_kind = str(MEDIA_DEFAULTS[media]["output_kind"])
    validation_jobs = []
    for index, (sid, staged, _obj) in enumerate(compiled, 1):
        record = records[index - 1]
        old_job = record.get("_story_film_job") if isinstance(record.get("_story_film_job"), dict) else {}
        validation_jobs.append({
            "job_id": str(old_job.get("job_id") or f"JOB-{index:03d}"),
            "source_ids": [str(x) for x in record.get("source_ids", []) if isinstance(x, str)] or _record_source_ids(record, index),
            "workflow": staged.relative_to(root).as_posix(),
            "patches": [],
            "blocked_by": [str(x) for x in old_job.get("blocked_by", []) if isinstance(x, str)],
            "output_dir": str(old_job.get("output_dir") or f"04_generation/comfyui/outputs/{sid}"),
            "timeout_s": int(old_job.get("timeout_s", 1800) or 1800),
            "max_transient_retries": int(old_job.get("max_transient_retries", 1) or 0),
            "expected_output_kinds": [expected_kind],
        })
    validation_batch = {
        "schema_version": 1,
        "batch_id": _batch_id(root),
        "status": "prepared",
        "sequential": True,
        "uploads": [],
        "jobs": validation_jobs,
    }
    batch_errors = comfyui_batch.validate(root, validation_batch, live=client)
    if batch_errors:
        raise WorkflowPipelineError("compiled offline batch failed validation: " + "; ".join(batch_errors))

    quarantine = _quarantine_existing(root, targets)
    canonical_out = _rel_path(root, str(contract.get("canonical_path") or DEFAULT_CANONICAL_REL))
    _atomic_replace_json(canonical_out, canonical_workflow)
    for (sid, _staged, obj), target in zip(compiled, targets):
        _atomic_replace_json(target, obj)

    jobs = []
    for index, (sid, _staged, _obj) in enumerate(compiled, 1):
        record = records[index - 1]
        old_job = record.get("_story_film_job") if isinstance(record.get("_story_film_job"), dict) else {}
        jobs.append({
            "job_id": str(old_job.get("job_id") or f"JOB-{index:03d}"),
            "source_ids": [str(x) for x in record.get("source_ids", []) if isinstance(x, str)] or _record_source_ids(record, index),
            "workflow": f"04_generation/comfyui/workflows/{sid}.json",
            "patches": [],
            "blocked_by": [str(x) for x in old_job.get("blocked_by", []) if isinstance(x, str)],
            "output_dir": str(old_job.get("output_dir") or f"04_generation/comfyui/outputs/{sid}"),
            "timeout_s": int(old_job.get("timeout_s", 1800) or 1800),
            "max_transient_retries": int(old_job.get("max_transient_retries", 1) or 0),
            "expected_output_kinds": [expected_kind],
        })
    batch = {
        "schema_version": 1,
        "batch_id": validation_batch["batch_id"],
        "status": "prepared",
        "sequential": True,
        "uploads": [],
        "jobs": jobs,
    }
    final_batch_errors = comfyui_batch.validate(root, batch, live=client)
    if final_batch_errors:
        # This should be unreachable after staged validation. Restore the old
        # runnable files if filesystem replacement produced an inconsistency.
        quarantine_dir = root / quarantine if quarantine else None
        for target in targets:
            saved = quarantine_dir / target.name if quarantine_dir is not None else None
            if saved is not None and saved.is_file():
                shutil.copy2(saved, target)
            else:
                try:
                    target.unlink()
                except FileNotFoundError:
                    pass
        raise WorkflowPipelineError("final offline batch failed validation: " + "; ".join(final_batch_errors))
    batch_path = _rel_path(root, str(contract.get("offline_batch_path") or DEFAULT_BATCH_REL))
    _atomic_replace_json(batch_path, batch)

    handoff: dict[str, Any] = {"requested": bool(arm_handoff), "armed": False}
    status = "ready-for-resource-handoff"
    if arm_handoff:
        try:
            handoff_state = resource_handoff.arm(
                root,
                batch_path.relative_to(root).as_posix(),
                comfyui_url,
                True,
            )
            handoff = {
                "requested": True,
                "armed": True,
                "phase": handoff_state.get("phase"),
                "message": handoff_state.get("message"),
                "runner_pid": handoff_state.get("runner_pid"),
            }
            status = "waiting-for-agent-end"
        except Exception as exc:
            handoff = {
                "requested": True,
                "armed": False,
                "error": str(exc),
                "instruction": "Report this deterministic resource-handoff blocker. Do not work around it with bash or manual backend commands.",
            }
            status = "ready-handoff-blocked"

    result = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "media_type": media,
        "candidate": candidate.relative_to(root).as_posix(),
        "canonical": canonical_out.relative_to(root).as_posix(),
        "workflow_count": len(compiled),
        "offline_batch": batch_path.relative_to(root).as_posix(),
        "batch_id": batch["batch_id"],
        "quarantine": quarantine,
        "live_validated": True,
        "llm_authored_only_canonical_candidate": True,
        "script_owned_fanout_and_batch": True,
        "prompt_sources": prompt_sources,
        "resource_handoff": handoff,
    }
    result_path = _rel_path(root, f"{RECOVERY_ROOT_REL}/workflow_finalize_result.json")
    _write_json(result_path, result)
    return {"ok": True, "action": "finalize", **result, "result_path": result_path.relative_to(root).as_posix()}


def dispatch(request: dict[str, Any], *, project: str | Path, comfyui_url: str = "") -> dict[str, Any]:
    root = _root(project)
    comfyui_url = _resolve_comfyui_url(root, comfyui_url or str(request.get("comfyui_url") or ""))
    action = str(request.get("action") or "").strip().lower()
    if action == "prepare":
        return prepare(
            project,
            comfyui_url,
            query=str(request.get("query") or ""),
            media_type=str(request.get("media_type") or "image"),
            records_path=str(request.get("records_path") or ""),
            source_limit=int(request.get("source_limit") or 12),
        )
    if action == "finalize":
        supplied = request.get("workflow")
        if supplied is not None and not isinstance(supplied, dict):
            raise WorkflowPipelineError("workflow-finalize workflow must be an object")
        return finalize(
            project,
            comfyui_url,
            workflow=supplied,
            candidate_path=str(request.get("candidate_path") or ""),
            arm_handoff=bool(request.get("arm_handoff", True)),
        )
    if action == "status":
        contract = root / CONTRACT_REL
        result = root / f"{RECOVERY_ROOT_REL}/workflow_finalize_result.json"
        return {
            "ok": True,
            "action": "status",
            "prepared": contract.is_file(),
            "finalized": result.is_file(),
            "contract": CONTRACT_REL if contract.is_file() else "",
            "result": json.loads(result.read_text(encoding="utf-8")) if result.is_file() else {},
        }
    raise WorkflowPipelineError(f"unsupported workflow pipeline action: {action}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Bounded Story-Film ComfyUI workflow orchestration")
    ap.add_argument("command", choices=["request"])
    ap.add_argument("--project", required=True)
    ap.add_argument("--url", default="")
    args = ap.parse_args()
    try:
        request = json.loads(__import__("sys").stdin.read() or "{}")
        if not isinstance(request, dict):
            raise WorkflowPipelineError("request must be a JSON object")
        result = dispatch(request, project=args.project, comfyui_url=args.url)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result.get("ok", True) else 1
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc), "type": type(exc).__name__}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
