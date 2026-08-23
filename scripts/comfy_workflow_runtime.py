#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Deterministic workflow and live-node discovery for Story-Film's ComfyUI bridge.

This module deliberately does not install or author custom nodes. It discovers
workflows/templates and node schemas from the running ComfyUI instance, validates
candidate API graphs against those live schemas, and only promotes validated
project-owned workflows.
"""
from __future__ import annotations

import json
import re
from collections import deque
from pathlib import Path
from typing import Any

STOP_WORDS = {"a", "an", "and", "for", "from", "in", "local", "of", "on", "or", "the", "to", "with", "workflow", "template"}
MAX_PATH_DEPTH = 8
MAX_PATHS = 20


class WorkflowRuntimeError(RuntimeError):
    pass


def _control_module():
    import comfyui_control  # type: ignore
    return comfyui_control


def _client(comfyui_url: str):
    mod = _control_module()
    return mod.Client(mod.resolve_url(comfyui_url))


def _project_root(project: str | Path) -> Path:
    root = Path(project).expanduser().resolve()
    if not (root / "00_project").is_dir():
        raise WorkflowRuntimeError("workflow operations require a Story-Film project with 00_project")
    return root


def _project_path(root: Path, value: str, *, allowed_prefix: str = "04_generation/comfyui/") -> Path:
    raw = value.strip().replace("\\", "/")
    if not raw or raw.startswith("/") or re.match(r"^[A-Za-z]:/", raw):
        raise WorkflowRuntimeError("workflow path must be a project-relative path")
    rel = Path(raw)
    if ".." in rel.parts:
        raise WorkflowRuntimeError("workflow path must not escape the project")
    if not rel.as_posix().startswith(allowed_prefix):
        raise WorkflowRuntimeError(f"workflow path must stay under {allowed_prefix}")
    out = (root / rel).resolve()
    try:
        out.relative_to(root)
    except ValueError as exc:
        raise WorkflowRuntimeError("workflow path escapes the Story-Film project") from exc
    return out


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise WorkflowRuntimeError(f"workflow file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise WorkflowRuntimeError(f"workflow file is not valid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise WorkflowRuntimeError(f"workflow JSON must be an object: {path}")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _terms(query: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", query.casefold())
        if token not in STOP_WORDS and len(token) > 1
    }


def _rank_records(rows: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    terms = _terms(query)
    if not terms:
        return rows
    ranked: list[tuple[int, dict[str, Any]]] = []
    for row in rows:
        haystack = json.dumps(row, ensure_ascii=False, sort_keys=True).casefold()
        matched = sorted(term for term in terms if term in haystack)
        threshold = max(1, (len(terms) + 1) // 2)
        if len(matched) < threshold:
            continue
        item = dict(row)
        item["match_terms"] = matched
        ranked.append((len(matched), item))
    ranked.sort(key=lambda item: (-item[0], str(item[1].get("name", item[1].get("class_type", ""))).casefold()))
    return [row for _, row in ranked]


def workflow_catalog(project: str | Path, comfyui_url: str, *, query: str = "", source: str = "") -> dict[str, Any]:
    root = _project_root(project)
    client = _client(comfyui_url)
    # Pull the complete catalog first. Story-Film does its own tokenized ranking so
    # a weak model cannot accidentally turn a model name into an MCP tool-name query.
    if source and source not in {"project-workflow", "user"}:
        raise WorkflowRuntimeError("workflow source must be project-workflow or user")
    result = client.workflow_catalog(root, source=source or None)
    rows = result.get("workflows", []) if isinstance(result, dict) else []
    rows = [
        dict(row)
        for row in rows
        if isinstance(row, dict) and row.get("source") in {"project-workflow", "user"}
    ]
    for row in rows:
        if row.get("source") == "project-workflow":
            row["runnable_state"] = "requires-live-validation"
        else:
            row["runnable_state"] = "source-only; fetch/adapt then live-validate"
    if query.strip():
        rows = _rank_records(rows, query)
    return {
        "ok": True,
        "action": "workflow-catalog",
        "query": query,
        "source": source,
        "count": len(rows),
        "workflows": rows,
        "warnings": result.get("warnings", []) if isinstance(result, dict) else [],
        "priority": ["project-workflow", "user"],
    }


def _safe_filename(value: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-.")
    return clean or "workflow"


def workflow_fetch(
    project: str | Path,
    comfyui_url: str,
    *,
    source: str,
    name: str,
    module: str = "",
    out_path: str = "",
) -> dict[str, Any]:
    root = _project_root(project)
    source = source.strip()
    client = _client(comfyui_url)
    if source == "project-workflow":
        candidate = _project_path(root, f"04_generation/comfyui/workflows/{name}")
        workflow = _load_json(candidate)
        original = candidate.relative_to(root).as_posix()
    elif source == "user":
        workflow = client.fetch_workflow_source("user", name, module=module or None)
        original = f"user:{name}"
    else:
        raise WorkflowRuntimeError("workflow source must be project-workflow or user; ComfyUI templates are not Story-Film workflow sources")

    if out_path:
        dest = _project_path(root, out_path)
    else:
        dest = _project_path(root, f"04_generation/comfyui/templates/imported/{source}-{_safe_filename(name)}.json")
    # Fetched material is preserved as a template/candidate. It may enter the
    # runnable workflows directory only through workflow-promote after live validation.
    if "/workflows/" in "/" + dest.relative_to(root).as_posix():
        raise WorkflowRuntimeError("workflow-fetch cannot write directly into the runnable workflows directory; fetch to templates/candidates then promote")
    _write_json(dest, workflow)
    fmt = "api" if _workflow_nodes(workflow) and "nodes" not in workflow else "ui" if isinstance(workflow.get("nodes"), list) else "unknown"
    return {
        "ok": True,
        "action": "workflow-fetch",
        "source": source,
        "name": name,
        "module": module,
        "source_reference": original,
        "path": dest.relative_to(root).as_posix(),
        "format": fmt,
        "runnable_state": "requires-live-validation",
    }


def _schema_record(class_type: str, schema: dict[str, Any]) -> dict[str, Any]:
    input_block = schema.get("input") if isinstance(schema.get("input"), dict) else {}
    required = input_block.get("required") if isinstance(input_block.get("required"), dict) else {}
    optional = input_block.get("optional") if isinstance(input_block.get("optional"), dict) else {}
    return {
        "class_type": class_type,
        "display_name": schema.get("display_name") or schema.get("name") or class_type,
        "category": schema.get("category", ""),
        "description": schema.get("description", ""),
        "required": required,
        "optional": optional,
        "outputs": list(schema.get("output", [])) if isinstance(schema.get("output"), (list, tuple)) else [],
        "output_names": list(schema.get("output_name", [])) if isinstance(schema.get("output_name"), (list, tuple)) else [],
        "output_node": bool(schema.get("output_node")),
        "deprecated": bool(schema.get("deprecated")),
        "experimental": bool(schema.get("experimental")),
    }


def node_search(comfyui_url: str, *, query: str = "", limit: int = 50) -> dict[str, Any]:
    live = _client(comfyui_url).object_info()
    rows = [_schema_record(str(name), schema) for name, schema in live.items() if isinstance(schema, dict)]
    rows.sort(key=lambda row: row["class_type"].casefold())
    if query.strip():
        rows = _rank_records(rows, query)
    limit = max(1, min(int(limit), 500))
    return {"ok": True, "action": "node-search", "query": query, "total": len(rows), "nodes": rows[:limit]}


def node_info(comfyui_url: str, *, class_type: str) -> dict[str, Any]:
    wanted = class_type.strip()
    if not wanted:
        raise WorkflowRuntimeError("node-info requires class_type")
    live = _client(comfyui_url).object_info(wanted)
    schema = live.get(wanted) if isinstance(live, dict) else None
    if not isinstance(schema, dict):
        # Some servers ignore /object_info/{class} and return the full map.
        all_live = _client(comfyui_url).object_info()
        schema = all_live.get(wanted) if isinstance(all_live, dict) else None
    if not isinstance(schema, dict):
        raise WorkflowRuntimeError(f"node class is not installed on the live ComfyUI server: {wanted}")
    return {"ok": True, "action": "node-info", "node": _schema_record(wanted, schema)}


def _input_types(schema: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    block = schema.get("input") if isinstance(schema.get("input"), dict) else {}
    for section in ("required", "optional"):
        fields = block.get(section) if isinstance(block.get(section), dict) else {}
        for spec in fields.values():
            if isinstance(spec, (list, tuple)) and spec and isinstance(spec[0], str):
                result.update(x.strip() for x in spec[0].split(",") if x.strip())
    return result


def _output_types(schema: dict[str, Any]) -> list[str]:
    values = schema.get("output")
    return [str(x) for x in values] if isinstance(values, (list, tuple)) else []


def _type_compatible(actual: str, expected: str) -> bool:
    if not actual or not expected:
        return True
    if actual == "*" or expected == "*" or actual == expected:
        return True
    return actual in {part.strip() for part in expected.split(",") if part.strip()}


def node_path(comfyui_url: str, *, from_type: str, to_type: str, max_depth: int = 6, max_paths: int = 10) -> dict[str, Any]:
    start = from_type.strip()
    target = to_type.strip()
    if not start or not target:
        raise WorkflowRuntimeError("node-path requires from_type and to_type")
    max_depth = max(1, min(int(max_depth), MAX_PATH_DEPTH))
    max_paths = max(1, min(int(max_paths), MAX_PATHS))
    live = _client(comfyui_url).object_info()
    schemas = {str(name): schema for name, schema in live.items() if isinstance(schema, dict)}
    queue: deque[tuple[str, list[dict[str, str]], tuple[str, ...]]] = deque([(start, [], ())])
    found: list[list[dict[str, str]]] = []
    while queue and len(found) < max_paths:
        current_type, path, used = queue.popleft()
        if len(path) >= max_depth:
            continue
        for class_type, schema in schemas.items():
            if class_type in used:
                continue
            inputs = _input_types(schema)
            if not any(_type_compatible(current_type, accepted) for accepted in inputs):
                continue
            for output_type in _output_types(schema):
                step = {"class_type": class_type, "input_type": current_type, "output_type": output_type}
                candidate = path + [step]
                if _type_compatible(output_type, target):
                    found.append(candidate)
                    if len(found) >= max_paths:
                        break
                else:
                    queue.append((output_type, candidate, used + (class_type,)))
            if len(found) >= max_paths:
                break
    return {
        "ok": True,
        "action": "node-path",
        "from_type": start,
        "to_type": target,
        "max_depth": max_depth,
        "paths": found,
        "count": len(found),
    }


def _workflow_nodes(workflow: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(k): v for k, v in workflow.items() if isinstance(v, dict) and isinstance(v.get("class_type"), str)}


def _link_errors(workflow: dict[str, Any], live: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    nodes = _workflow_nodes(workflow)
    for target_id, node in nodes.items():
        target_class = str(node.get("class_type", ""))
        target_schema = live.get(target_class)
        if not isinstance(target_schema, dict):
            continue
        input_block = target_schema.get("input") if isinstance(target_schema.get("input"), dict) else {}
        required = input_block.get("required") if isinstance(input_block.get("required"), dict) else {}
        optional = input_block.get("optional") if isinstance(input_block.get("optional"), dict) else {}
        inputs = node.get("inputs") if isinstance(node.get("inputs"), dict) else {}
        for input_name, value in inputs.items():
            if not (isinstance(value, list) and len(value) == 2 and isinstance(value[1], int)):
                continue
            source_id = str(value[0])
            output_index = value[1]
            source = nodes.get(source_id)
            if source is None:
                errors.append(f"node {target_id} ({target_class}): input {input_name!r} links to missing node {source_id}")
                continue
            source_class = str(source.get("class_type", ""))
            source_schema = live.get(source_class)
            if not isinstance(source_schema, dict):
                continue
            outputs = _output_types(source_schema)
            if output_index < 0 or output_index >= len(outputs):
                errors.append(f"node {target_id} ({target_class}): input {input_name!r} links to invalid output {output_index} of {source_id} ({source_class})")
                continue
            spec = required.get(input_name, optional.get(input_name))
            expected = spec[0] if isinstance(spec, (list, tuple)) and spec and isinstance(spec[0], str) else ""
            actual = outputs[output_index]
            if expected and not _type_compatible(actual, expected):
                errors.append(
                    f"node {target_id} ({target_class}): input {input_name!r} expects {expected}, "
                    f"but {source_id} ({source_class}) output {output_index} is {actual}"
                )
    return errors


def workflow_validate(project: str | Path, comfyui_url: str, *, workflow_path: str) -> dict[str, Any]:
    root = _project_root(project)
    path = _project_path(root, workflow_path)
    workflow = _load_json(path)
    client = _client(comfyui_url)
    verdict = client.validate_workflow(workflow)
    if not isinstance(verdict, dict):
        raise WorkflowRuntimeError("ComfyUI workflow validator returned an invalid result")
    live = client.object_info()
    link_errors = _link_errors(workflow, live)
    errors = list(verdict.get("errors", [])) if isinstance(verdict.get("errors"), list) else []
    errors.extend(error for error in link_errors if error not in errors)
    verdict = dict(verdict)
    verdict["errors"] = errors
    verdict["valid"] = not errors and bool(verdict.get("valid", True))
    return {
        "ok": True,
        "action": "workflow-validate",
        "workflow_path": path.relative_to(root).as_posix(),
        "verdict": verdict,
        "live_link_validation": True,
    }


def workflow_promote(project: str | Path, comfyui_url: str, *, workflow_path: str, out_path: str) -> dict[str, Any]:
    root = _project_root(project)
    source = _project_path(root, workflow_path)
    target = _project_path(root, out_path)
    target_rel = target.relative_to(root).as_posix()
    if not target_rel.startswith("04_generation/comfyui/workflows/"):
        raise WorkflowRuntimeError("workflow-promote output must be under 04_generation/comfyui/workflows/")
    checked = workflow_validate(root, comfyui_url, workflow_path=source.relative_to(root).as_posix())
    verdict = checked["verdict"]
    if not verdict.get("valid"):
        raise WorkflowRuntimeError("candidate workflow failed live validation: " + "; ".join(str(x) for x in verdict.get("errors", [])))
    workflow = _load_json(source)
    _write_json(target, workflow)
    return {
        "ok": True,
        "action": "workflow-promote",
        "candidate": source.relative_to(root).as_posix(),
        "path": target_rel,
        "verdict": verdict,
    }


def server_info(comfyui_url: str, *, mcp_error: str = "") -> dict[str, Any]:
    client = _client(comfyui_url)
    result = client.probe()
    return {
        "ok": True,
        "action": "server-info",
        "transport": "native-comfyui-fallback" if mcp_error else "native-comfyui",
        "comfyui_url": comfyui_url,
        "mcp_error": mcp_error,
        "result": result,
    }


def dispatch(request: dict[str, Any], *, project: str | Path, comfyui_url: str) -> dict[str, Any]:
    action = str(request.get("action") or "").strip().lower()
    if action == "workflow-catalog":
        return workflow_catalog(project, comfyui_url, query=str(request.get("query") or ""), source=str(request.get("source") or ""))
    if action == "workflow-fetch":
        return workflow_fetch(
            project,
            comfyui_url,
            source=str(request.get("source") or ""),
            name=str(request.get("name") or ""),
            module=str(request.get("module") or ""),
            out_path=str(request.get("out_path") or ""),
        )
    if action == "node-search":
        return node_search(comfyui_url, query=str(request.get("query") or ""), limit=int(request.get("limit") or 50))
    if action == "node-info":
        return node_info(comfyui_url, class_type=str(request.get("class_type") or ""))
    if action == "node-path":
        return node_path(
            comfyui_url,
            from_type=str(request.get("from_type") or ""),
            to_type=str(request.get("to_type") or ""),
            max_depth=int(request.get("max_depth") or 6),
            max_paths=int(request.get("max_paths") or 10),
        )
    if action == "workflow-validate":
        return workflow_validate(project, comfyui_url, workflow_path=str(request.get("workflow_path") or ""))
    if action == "workflow-promote":
        return workflow_promote(
            project,
            comfyui_url,
            workflow_path=str(request.get("workflow_path") or ""),
            out_path=str(request.get("out_path") or ""),
        )
    raise WorkflowRuntimeError(f"unsupported native workflow action: {action}")
