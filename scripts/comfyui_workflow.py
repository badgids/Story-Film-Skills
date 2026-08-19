#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def detect_format(data: Any) -> str:
    if not isinstance(data, dict):
        return "unknown"
    if isinstance(data.get("nodes"), list) and "links" in data:
        return "ui"
    candidates = [v for k, v in data.items() if k not in {"definitions", "extra", "version"}]
    if candidates and all(isinstance(v, dict) and "class_type" in v and "inputs" in v for v in candidates):
        return "api"
    if not candidates and data == {}:
        return "api-empty"
    return "unknown"


def api_nodes(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(k): v
        for k, v in data.items()
        if isinstance(v, dict) and "class_type" in v and "inputs" in v
    }


def ui_nodes(data: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = data.get("nodes", [])
    return [n for n in nodes if isinstance(n, dict)] if isinstance(nodes, list) else []


def inspect_workflow(data: Any) -> dict[str, Any]:
    fmt = detect_format(data)
    out: dict[str, Any] = {"format": fmt}
    if fmt.startswith("api"):
        nodes = api_nodes(data if isinstance(data, dict) else {})
        links: list[dict[str, Any]] = []
        output_nodes: list[str] = []
        for node_id, node in nodes.items():
            for input_name, value in (node.get("inputs") or {}).items():
                if isinstance(value, list) and len(value) == 2 and isinstance(value[0], (str, int)) and isinstance(value[1], int):
                    links.append({
                        "source_node": str(value[0]),
                        "source_output": value[1],
                        "target_node": node_id,
                        "target_input": str(input_name),
                    })
            meta = node.get("_meta") or {}
            if isinstance(meta, dict) and meta.get("output_node") is True:
                output_nodes.append(node_id)
        out.update({
            "node_count": len(nodes),
            "link_count": len(links),
            "classes": sorted({str(n.get("class_type")) for n in nodes.values()}),
            "links": links,
            "output_nodes_from_meta": output_nodes,
        })
    elif fmt == "ui":
        nodes = ui_nodes(data)
        links = data.get("links", []) if isinstance(data, dict) else []
        out.update({
            "node_count": len(nodes),
            "link_count": len(links) if isinstance(links, list) else 0,
            "classes": sorted({str(n.get("type", "")) for n in nodes if n.get("type")}),
            "has_subgraphs": bool(isinstance(data, dict) and isinstance(data.get("definitions"), dict)),
        })
    return out


def validate_offline(data: Any) -> list[str]:
    errors: list[str] = []
    fmt = detect_format(data)
    if fmt == "ui":
        errors.append("workflow is UI format; native /prompt submission requires API format")
        return errors
    if fmt not in {"api", "api-empty"}:
        errors.append("workflow format is not recognized")
        return errors
    nodes = api_nodes(data)
    for node_id, node in nodes.items():
        class_type = node.get("class_type")
        inputs = node.get("inputs")
        if not isinstance(class_type, str) or not class_type.strip():
            errors.append(f"node {node_id}: class_type must be a non-empty string")
        if not isinstance(inputs, dict):
            errors.append(f"node {node_id}: inputs must be an object")
            continue
        for input_name, value in inputs.items():
            if isinstance(value, list) and len(value) == 2 and isinstance(value[0], (str, int)) and isinstance(value[1], int):
                src = str(value[0])
                if src not in nodes:
                    errors.append(f"node {node_id} input {input_name}: source node {src} does not exist")
                if value[1] < 0:
                    errors.append(f"node {node_id} input {input_name}: output index must be non-negative")
    return errors


def parse_value(raw: str, as_json: bool) -> Any:
    if not as_json:
        return raw
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid --value JSON: {exc}") from exc


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Inspect and minimally edit ComfyUI workflow JSON.")
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("detect")
    p.add_argument("workflow")

    p = sub.add_parser("inspect")
    p.add_argument("workflow")

    p = sub.add_parser("classes")
    p.add_argument("workflow")

    p = sub.add_parser("validate")
    p.add_argument("workflow")

    p = sub.add_parser("patch")
    p.add_argument("workflow")
    p.add_argument("--node", required=True)
    p.add_argument("--input", required=True)
    p.add_argument("--value", required=True)
    p.add_argument("--json-value", action="store_true")
    p.add_argument("--out")
    p.add_argument("--in-place", action="store_true")
    p.add_argument("--confirm-in-place", action="store_true")

    args = ap.parse_args()
    data = load_json(args.workflow)

    if args.command == "detect":
        print(json.dumps({"format": detect_format(data)}))
        return 0
    if args.command == "inspect":
        result = inspect_workflow(data)
        result["offline_errors"] = validate_offline(data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.command == "classes":
        print(json.dumps({"format": detect_format(data), "classes": inspect_workflow(data).get("classes", [])}, indent=2))
        return 0
    if args.command == "validate":
        errors = validate_offline(data)
        print(json.dumps({"format": detect_format(data), "valid": not errors, "errors": errors}, indent=2))
        return 0 if not errors else 2
    if args.command == "patch":
        if detect_format(data) != "api":
            raise SystemExit("patch supports API-format workflow JSON only")
        node_id = str(args.node)
        nodes = api_nodes(data)
        if node_id not in nodes:
            raise SystemExit(f"node {node_id} not found")
        inputs = nodes[node_id].get("inputs")
        if not isinstance(inputs, dict):
            raise SystemExit(f"node {node_id} has no input object")
        if args.input not in inputs:
            raise SystemExit(f"input {args.input!r} not present on node {node_id}; inspect the live schema before adding a new input")
        patched = copy.deepcopy(data)
        patched[node_id]["inputs"][args.input] = parse_value(args.value, args.json_value)
        if args.in_place:
            if not args.confirm_in_place:
                raise SystemExit("--in-place requires --confirm-in-place")
            out = Path(args.workflow)
        else:
            if not args.out:
                raise SystemExit("patch requires --out unless --in-place is explicitly confirmed")
            out = Path(args.out)
        write_json(out, patched)
        print(json.dumps({"written": str(out), "node": node_id, "input": args.input}, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
