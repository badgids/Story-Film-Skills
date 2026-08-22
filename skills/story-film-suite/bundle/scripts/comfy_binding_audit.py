#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load_workflow(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def node_map(obj):
    out = {}
    if isinstance(obj, dict) and isinstance(obj.get("nodes"), list):
        for n in obj["nodes"]:
            if isinstance(n, dict) and n.get("id") is not None:
                out[str(n["id"])] = {"type": n.get("type"), "ui": n}
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, dict) and isinstance(v.get("class_type"), str):
                out[str(k)] = {"type": v.get("class_type"), "api": v}
    return out

def read_rows(path: Path):
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

def _actual_binding_value(node, record):
    if "api" in node and isinstance(record.get("input_name"), str):
        inputs = node["api"].get("inputs", {})
        if isinstance(inputs, dict):
            return inputs.get(record["input_name"])
    if "ui" in node and isinstance(record.get("widget_index"), int):
        values = node["ui"].get("widgets_values", [])
        if isinstance(values, list) and 0 <= record["widget_index"] < len(values):
            return values[record["widget_index"]]
    return None

def validate_project(root: Path):
    errors = []
    path = root / "04_generation/comfyui/reference_bindings.jsonl"
    try:
        rows = read_rows(path)
    except Exception as exc:
        return [f"{path.relative_to(root)}: {exc}"]
    seen_ordinals = {}
    for n, rec in enumerate(rows, 1):
        workflow = rec.get("workflow")
        node_id = str(rec.get("node_id", ""))
        expected_type = rec.get("node_type")
        if not workflow:
            errors.append(f"row {n}: workflow required")
            continue
        workflow_path = (root / workflow).resolve()
        if root.resolve() not in workflow_path.parents:
            errors.append(f"row {n}: workflow escapes project")
            continue
        if not workflow_path.exists():
            errors.append(f"row {n}: workflow missing {workflow}")
            continue
        try:
            nodes = node_map(load_workflow(workflow_path))
        except Exception as exc:
            errors.append(f"row {n}: invalid workflow: {exc}")
            continue
        node = nodes.get(node_id)
        if node is None:
            errors.append(f"row {n}: node_id {node_id} missing from workflow")
        elif expected_type and node["type"] != expected_type:
            errors.append(f"row {n}: node type mismatch {node['type']!r} != {expected_type!r}")
        if node is not None and "expected_value" in rec:
            actual = _actual_binding_value(node, rec)
            if actual != rec.get("expected_value"):
                errors.append(f"row {n}: graph binding value mismatch {actual!r} != {rec.get('expected_value')!r}")
        ordinal = rec.get("ordinal")
        if ordinal is not None:
            if not isinstance(ordinal, int) or ordinal < 1:
                errors.append(f"row {n}: ordinal must be a positive integer")
            else:
                label = rec.get("prompt_label")
                expected_label = f"<Picture {ordinal}>"
                if label is not None and label != expected_label:
                    errors.append(f"row {n}: prompt_label {label!r} does not match ordinal {ordinal}")
                key = (workflow, ordinal)
                if key in seen_ordinals:
                    errors.append(f"row {n}: duplicate reference ordinal {ordinal} for {workflow}")
                seen_ordinals[key] = n
        asset = rec.get("staged_path")
        expected_hash = rec.get("sha256")
        if asset:
            asset_path = (root / asset).resolve()
            if root.resolve() not in asset_path.parents:
                errors.append(f"row {n}: staged_path escapes project")
            elif not asset_path.exists():
                errors.append(f"row {n}: staged asset missing")
            elif expected_hash and digest(asset_path) != expected_hash:
                errors.append(f"row {n}: staged asset sha256 mismatch")
        if not (rec.get("ref_id") or rec.get("media_id")):
            errors.append(f"row {n}: ref_id or media_id required")
    return errors

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_dir")
    args = ap.parse_args()
    errors = validate_project(Path(args.project_dir).resolve())
    for error in errors:
        print("ERROR", error)
    print("OK ComfyUI reference bindings" if not errors else f"FAILED {len(errors)}")
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
