#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Durable multi-step pipeline progress for Story-Film Skills.

The JSON ledger is authoritative. Pi UI is a renderer of this file, not a second
progress system. Checkpoints are written atomically and HANDOFF.md is replaced
last so a fresh session can recover without chat history.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import workflow_preflight

SCHEMA_VERSION = 1
OWNER = "story-film-skills"
LEGACY_OWNERS = {"badgids-story-film-skills"}
STATUSES = {"pending", "current", "completed", "blocked", "skipped"}
PIPELINE_STATUSES = {"inactive", "active", "paused", "blocked", "complete"}
ROOT = Path(__file__).resolve().parents[1]
PLAYBOOK_DIR = ROOT / "skills" / "story-film" / "playbooks"
NUMBERED = re.compile(r"^\s*(\d+)\.\s+(.+?)\s*$")
BACKTICK = re.compile(r"`([^`]+)`")


def workflow_preflight_item(playbook: Path) -> str | None:
    profile = workflow_preflight.PLAYBOOK_PROFILES.get(playbook.stem, "")
    if not profile:
        return None
    return (
        f"`generation-workflow-setup`: complete the `{profile}` workflow preflight before creative production. "
        "Do not advance until `scripts/workflow_preflight.py status` reports `complete`."
    )


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug_label(stem: str) -> str:
    return " ".join(word.capitalize() for word in stem.replace("_", "-").split("-"))


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def atomic_json(path: Path, value: Any) -> None:
    atomic_text(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def project_root(value: str | Path) -> Path:
    root = Path(value).expanduser().resolve()
    if not (root / "00_project").is_dir():
        raise SystemExit(f"not a Story-Film project: {root}")
    return root


def playbook_path(value: str) -> Path:
    name = value.strip()
    if name.endswith(".md"):
        name = name[:-3]
    candidate = PLAYBOOK_DIR / f"{name}.md"
    if not candidate.is_file():
        raise SystemExit(f"unknown story-film playbook: {value}")
    return candidate


def numbered_items(path: Path) -> list[str]:
    items: list[str] = []
    in_fence = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = NUMBERED.match(raw)
        if match:
            items.append(match.group(2).strip())
    return items


def referenced_playbooks(text: str) -> list[Path]:
    result: list[Path] = []
    seen: set[Path] = set()
    for token in BACKTICK.findall(text):
        base = token.strip()
        if base.endswith(".md"):
            base = base[:-3]
        # Specialist names intentionally do not resolve here. Only files in the
        # playbook directory become nested pipeline nodes.
        p = PLAYBOOK_DIR / f"{base}.md"
        if p.is_file() and p not in seen:
            seen.add(p)
            result.append(p)
    return result


def make_node(node_id: str, label: str, position: int, total: int, source: str, children_key: str | None = None, children: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    node: dict[str, Any] = {
        "id": node_id,
        "label": label,
        "position": position,
        "total": total,
        "status": "pending",
        "source": source,
    }
    if children_key and children:
        node[children_key] = children
    return node


def compile_children(path: Path, parent_id: str, depth: int, max_depth: int) -> list[dict[str, Any]]:
    items = numbered_items(path)
    result: list[dict[str, Any]] = []
    prefix = "STEP" if depth == 1 else "SUB"
    source_token = re.sub(r"[^A-Za-z0-9]+", "-", path.stem).strip("-").upper()
    for index, text in enumerate(items, 1):
        node_id = f"{parent_id}.{prefix}-{source_token}-{index:02d}"
        nested: list[dict[str, Any]] = []
        if depth < max_depth:
            refs = referenced_playbooks(text)
            # Multiple playbooks in one line remain separate nested records. To
            # keep three UI levels bounded, concatenate their numbered items.
            for ref in refs:
                nested.extend(compile_children(ref, node_id, depth + 1, max_depth))
        result.append(make_node(
            node_id,
            text,
            index,
            len(items),
            str(path.relative_to(ROOT)),
            "substeps" if depth == 1 else None,
            nested if depth == 1 else None,
        ))
    return result


def compile_pipeline(playbook: Path, max_depth: int = 3) -> dict[str, Any]:
    items = numbered_items(playbook)
    preflight = workflow_preflight_item(playbook)
    if preflight:
        items = [preflight, *items]
    stages: list[dict[str, Any]] = []
    for index, text in enumerate(items, 1):
        stage_id = f"PST-{index:03d}"
        steps: list[dict[str, Any]] = []
        if max_depth >= 2:
            for ref in referenced_playbooks(text):
                steps.extend(compile_children(ref, stage_id, 1, max_depth - 1))
        stages.append(make_node(stage_id, text, index, len(items), str(playbook.relative_to(ROOT)), "steps", steps))
    value = {
        "schema_version": SCHEMA_VERSION,
        "owner": OWNER,
        "pipeline_id": playbook.stem,
        "label": slug_label(playbook.stem),
        "source_playbook": str(playbook.relative_to(ROOT)),
        "status": "active" if stages else "complete",
        "stages": stages,
        "cursor": {},
        "next_action": "",
        "blocker": "",
        "last_completed": "",
        "updated_at": now(),
    }
    if stages:
        first = flatten_leaves(value)[0]
        first[1]["status"] = "current"
        value["cursor"] = cursor_for(first[0])
        value["next_action"] = first[1]["label"]
        derive_container_statuses(value)
    return value


def iter_nodes(value: dict[str, Any]) -> Iterable[tuple[list[dict[str, Any]], dict[str, Any]]]:
    def walk(nodes: list[dict[str, Any]], ancestors: list[dict[str, Any]]):
        for node in nodes:
            chain = [*ancestors, node]
            yield chain, node
            for key in ("steps", "substeps"):
                children = node.get(key)
                if isinstance(children, list):
                    yield from walk(children, chain)
    yield from walk(value.get("stages") or [], [])


def children_of(node: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("steps", "substeps"):
        children = node.get(key)
        if isinstance(children, list) and children:
            return children
    return []


def flatten_leaves(value: dict[str, Any]) -> list[tuple[list[dict[str, Any]], dict[str, Any]]]:
    return [(chain, node) for chain, node in iter_nodes(value) if not children_of(node)]


def cursor_for(chain: list[dict[str, Any]]) -> dict[str, str]:
    result: dict[str, str] = {}
    if len(chain) > 0:
        result["stage_id"] = chain[0]["id"]
    if len(chain) > 1:
        result["step_id"] = chain[1]["id"]
    if len(chain) > 2:
        result["substep_id"] = chain[2]["id"]
    result["target_id"] = chain[-1]["id"]
    return result


def aggregate_status(children: list[dict[str, Any]]) -> str:
    states = [c.get("status", "pending") for c in children]
    if states and all(s in {"completed", "skipped"} for s in states):
        return "completed"
    if "blocked" in states:
        return "blocked"
    if "current" in states:
        return "current"
    if any(s == "completed" for s in states):
        return "current"
    return "pending"


def derive_container_statuses(value: dict[str, Any]) -> None:
    def walk(node: dict[str, Any]) -> str:
        children = children_of(node)
        if children:
            for child in children:
                walk(child)
            node["status"] = aggregate_status(children)
        return str(node.get("status", "pending"))
    for stage in value.get("stages") or []:
        walk(stage)


def find_chain(value: dict[str, Any], target_id: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    for chain, node in iter_nodes(value):
        if node.get("id") == target_id:
            return chain, node
    raise SystemExit(f"progress target not found: {target_id}")


def current_leaf(value: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]] | None:
    leaves = flatten_leaves(value)
    for item in leaves:
        if item[1].get("status") in {"current", "blocked"}:
            return item
    return None


def next_pending_leaf(value: dict[str, Any], after_id: str | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]] | None:
    leaves = flatten_leaves(value)
    start = 0
    if after_id:
        for i, (_, node) in enumerate(leaves):
            if node.get("id") == after_id:
                start = i + 1
                break
    for item in leaves[start:]:
        if item[1].get("status") == "pending":
            return item
    for item in leaves[:start]:
        if item[1].get("status") == "pending":
            return item
    return None


def load_progress(root: Path) -> dict[str, Any]:
    path = root / "00_project" / "pipeline_progress.json"
    if not path.is_file():
        return inactive_progress()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid pipeline progress JSON: {exc}") from exc
    validate_progress(value)
    return value


def inactive_progress() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "owner": OWNER,
        "pipeline_id": "",
        "label": "",
        "source_playbook": "",
        "status": "inactive",
        "stages": [],
        "cursor": {},
        "next_action": "",
        "blocker": "",
        "last_completed": "",
        "updated_at": now(),
    }


def validate_progress(value: dict[str, Any]) -> None:
    if value.get("schema_version") != SCHEMA_VERSION:
        raise SystemExit("pipeline progress schema_version must be 1")
    if value.get("owner") not in ({OWNER} | LEGACY_OWNERS):
        raise SystemExit(f"pipeline progress owner must be {OWNER}")
    if value.get("status") not in PIPELINE_STATUSES:
        raise SystemExit(f"invalid pipeline status: {value.get('status')!r}")
    ids: set[str] = set()
    current = 0
    for chain, node in iter_nodes(value):
        node_id = str(node.get("id") or "")
        if not node_id or node_id in ids:
            raise SystemExit(f"invalid or duplicate progress node id: {node_id!r}")
        ids.add(node_id)
        status = node.get("status")
        if status not in STATUSES:
            raise SystemExit(f"{node_id}: invalid status {status!r}")
        if status == "current":
            current += 1
        if len(chain) > 3:
            raise SystemExit(f"{node_id}: progress tree exceeds stage/step/substep depth")
    if current > 3:
        # Parent containers can also be derived as current. Leaf uniqueness is checked below.
        pass
    leaf_current = [node for _, node in flatten_leaves(value) if node.get("status") in {"current", "blocked"}]
    if value.get("status") in {"active", "blocked", "paused"} and value.get("stages") and len(leaf_current) != 1:
        raise SystemExit(f"active/blocked/paused progress requires exactly one current or blocked leaf; found {len(leaf_current)}")
    if value.get("status") == "complete":
        unfinished = [node["id"] for _, node in flatten_leaves(value) if node.get("status") not in {"completed", "skipped"}]
        if unfinished:
            raise SystemExit(f"complete pipeline still has unfinished leaves: {', '.join(unfinished[:10])}")


def event(root: Path, kind: str, value: dict[str, Any], note: str = "", files: list[str] | None = None) -> None:
    record = {
        "timestamp": now(),
        "event": kind,
        "pipeline_id": value.get("pipeline_id"),
        "status": value.get("status"),
        "cursor": value.get("cursor") or {},
        "note": note,
        "files": files or [],
    }
    path = root / "00_project" / "progress_events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def handoff_text(root: Path, value: dict[str, Any], last_action: str = "", files: list[str] | None = None) -> str:
    current = current_leaf(value)
    current_id = current[1]["id"] if current else "none"
    current_label = current[1]["label"] if current else "none"
    files = files or []
    file_lines = "\n".join(f"- `{f}`" for f in files) if files else "- none recorded for this checkpoint"
    blocker = value.get("blocker") or "none"
    next_action = value.get("next_action") or ("Pipeline complete" if value.get("status") == "complete" else "No next action recorded")
    return (
        "# Story-Film Pipeline Handoff\n\n"
        f"Pipeline: {value.get('label') or value.get('pipeline_id') or 'none'}\n"
        f"Status: {value.get('status')}\n"
        f"Current target: {current_id} - {current_label}\n"
        f"Last completed: {value.get('last_completed') or 'none'}\n"
        f"Last action: {last_action or 'none recorded'}\n"
        f"Blocker: {blocker}\n"
        f"Next action: {next_action}\n"
        f"Updated: {value.get('updated_at')}\n\n"
        "## Files changed in the latest checkpoint\n\n"
        f"{file_lines}\n\n"
        "## Resume\n\n"
        "Read `00_project/pipeline_progress.json`, then continue only the current target. "
        "Do not infer completion from file existence alone. After validation, checkpoint the target before moving on.\n\n"
        "```bash\n"
        "python <story-film-skill-root>/scripts/pipeline_progress.py status <project-root>\n"
        "```\n"
    )


def save_checkpoint(root: Path, value: dict[str, Any], kind: str, note: str = "", last_action: str = "", files: list[str] | None = None) -> None:
    derive_container_statuses(value)
    value["updated_at"] = now()
    validate_progress(value)
    atomic_json(root / "00_project" / "pipeline_progress.json", value)
    event(root, kind, value, note=note, files=files)
    # HANDOFF last, matching the recovery rule: if it is present it points at
    # already-written canonical progress state.
    atomic_text(root / "00_project" / "HANDOFF.md", handoff_text(root, value, last_action=last_action, files=files))


def initialize(root: Path, playbook: Path, force: bool, max_depth: int) -> dict[str, Any]:
    path = root / "00_project" / "pipeline_progress.json"
    if path.is_file() and not force:
        existing = load_progress(root)
        if existing.get("status") not in {"inactive", "complete"}:
            raise SystemExit("an active pipeline already exists; use --force only when intentionally replacing its progress ledger")
    profile = workflow_preflight.PLAYBOOK_PROFILES.get(playbook.stem, "")
    if profile:
        workflow_preflight.set_preflight(
            root,
            playbook=playbook.stem,
            profile=profile,
            categories=[],
        )
    value = compile_pipeline(playbook, max_depth=max_depth)
    save_checkpoint(root, value, "pipeline.initialized", note=f"source={playbook.name}", last_action="Initialized pipeline progress")
    return value


def checkpoint(root: Path, status: str, target: str | None, next_action: str | None, blocker: str | None, note: str, last_action: str, files: list[str]) -> dict[str, Any]:
    value = load_progress(root)
    if value.get("status") in {"inactive", "complete"}:
        raise SystemExit(f"cannot checkpoint pipeline in {value.get('status')} state")
    current = current_leaf(value)
    target_id = target or (current[1]["id"] if current else "")
    chain, node = find_chain(value, target_id)
    if children_of(node):
        raise SystemExit("checkpoint target must be a leaf step/substep, not a container")
    if status not in {"current", "completed", "blocked", "skipped"}:
        raise SystemExit("checkpoint status must be current, completed, blocked, or skipped")
    profile = workflow_preflight.PLAYBOOK_PROFILES.get(str(value.get("pipeline_id") or ""), "")
    if profile and status in {"completed", "skipped"}:
        preflight = workflow_preflight.status(root)
        if preflight.get("status") != "complete":
            missing = [str(x) for x in preflight.get("missing_categories", [])]
            suffix = f" Missing categories: {', '.join(missing)}." if missing else ""
            raise SystemExit(
                "workflow preflight is incomplete; do not complete or skip Story-Film pipeline work until "
                "`scripts/workflow_preflight.py status` reports `complete`."
                + suffix
            )
    if status == "skipped" and not note.strip():
        raise SystemExit("skipped checkpoints require --note explaining why the conditional step does not apply")
    previous_id = node["id"]
    if status == "blocked":
        node["status"] = "blocked"
        value["status"] = "blocked"
        value["blocker"] = blocker or note or "Blocked; reason not recorded"
        value["cursor"] = cursor_for(chain)
        value["next_action"] = next_action or f"Resolve blocker for {node['label']}"
    elif status == "current":
        node["status"] = "current"
        value["status"] = "active"
        value["blocker"] = ""
        value["cursor"] = cursor_for(chain)
        value["next_action"] = next_action or node["label"]
    else:
        node["status"] = status
        value["last_completed"] = node["id"]
        value["blocker"] = ""
        nxt = next_pending_leaf(value, after_id=previous_id)
        if nxt:
            nxt[1]["status"] = "current"
            value["status"] = "active"
            value["cursor"] = cursor_for(nxt[0])
            value["next_action"] = next_action or nxt[1]["label"]
        else:
            value["status"] = "complete"
            value["cursor"] = {}
            value["next_action"] = ""
    save_checkpoint(root, value, f"pipeline.{status}", note=note, last_action=last_action, files=files)
    return value


def pause(root: Path, note: str) -> dict[str, Any]:
    value = load_progress(root)
    if value.get("status") not in {"active", "blocked"}:
        raise SystemExit("only an active or blocked pipeline can be paused")
    value["status"] = "paused"
    save_checkpoint(root, value, "pipeline.paused", note=note, last_action="Paused pipeline")
    return value


def resume(root: Path, note: str) -> dict[str, Any]:
    value = load_progress(root)
    if value.get("status") not in {"paused", "blocked"}:
        raise SystemExit("only a paused or blocked pipeline can be resumed")
    cur = current_leaf(value)
    if not cur:
        raise SystemExit("pipeline has no resumable current target")
    cur[1]["status"] = "current"
    value["status"] = "active"
    value["blocker"] = ""
    value["cursor"] = cursor_for(cur[0])
    value["next_action"] = cur[1]["label"]
    save_checkpoint(root, value, "pipeline.resumed", note=note, last_action="Resumed pipeline")
    return value


def reset_target(root: Path, target_id: str, note: str) -> dict[str, Any]:
    value = load_progress(root)
    chain, target = find_chain(value, target_id)
    leaf_ids: set[str] = set()
    def collect(node: dict[str, Any]):
        kids = children_of(node)
        if not kids:
            leaf_ids.add(node["id"])
        else:
            for child in kids:
                collect(child)
    collect(target)
    leaves = flatten_leaves(value)
    for _, leaf in leaves:
        if leaf["id"] in leaf_ids:
            leaf["status"] = "pending"
    # Clear any other active marker before activating the reset scope.
    for _, leaf in leaves:
        if leaf["id"] not in leaf_ids and leaf.get("status") in {"current", "blocked"}:
            leaf["status"] = "pending"
    first = next((item for item in leaves if item[1]["id"] in leaf_ids), None)
    if not first:
        raise SystemExit("reset target contains no actionable leaf")
    first[1]["status"] = "current"
    value["status"] = "active"
    value["blocker"] = ""
    value["cursor"] = cursor_for(first[0])
    value["next_action"] = first[1]["label"]
    save_checkpoint(root, value, "pipeline.reset", note=note or f"Reset only {target_id}", last_action=f"Reset {target_id}")
    return value


def summary(value: dict[str, Any]) -> dict[str, Any]:
    leaves = flatten_leaves(value)
    counts = {key: 0 for key in STATUSES}
    for _, node in leaves:
        counts[node.get("status", "pending")] += 1
    current = current_leaf(value)
    return {
        "pipeline_id": value.get("pipeline_id"),
        "label": value.get("label"),
        "status": value.get("status"),
        "cursor": value.get("cursor") or {},
        "current": ({"id": current[1]["id"], "label": current[1]["label"], "status": current[1]["status"]} if current else None),
        "next_action": value.get("next_action"),
        "blocker": value.get("blocker"),
        "counts": counts,
        "total": len(leaves),
        "updated_at": value.get("updated_at"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Manage durable Story-Film multi-step pipeline progress.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init")
    p.add_argument("project")
    p.add_argument("--playbook", required=True)
    p.add_argument("--force", action="store_true")
    p.add_argument("--max-depth", type=int, default=3, choices=(1, 2, 3))

    p = sub.add_parser("checkpoint")
    p.add_argument("project")
    p.add_argument("--status", required=True, choices=("current", "completed", "blocked", "skipped"))
    p.add_argument("--target")
    p.add_argument("--next", dest="next_action")
    p.add_argument("--blocker")
    p.add_argument("--note", default="")
    p.add_argument("--last-action", default="")
    p.add_argument("--file", action="append", default=[])

    p = sub.add_parser("pause"); p.add_argument("project"); p.add_argument("--note", default="")
    p = sub.add_parser("resume"); p.add_argument("project"); p.add_argument("--note", default="")
    p = sub.add_parser("reset"); p.add_argument("project"); p.add_argument("target"); p.add_argument("--note", default="")
    p = sub.add_parser("status"); p.add_argument("project"); p.add_argument("--full", action="store_true")
    p = sub.add_parser("validate"); p.add_argument("project")

    args = ap.parse_args()
    root = project_root(args.project)
    if args.cmd == "init":
        value = initialize(root, playbook_path(args.playbook), args.force, args.max_depth)
        print(json.dumps(summary(value), indent=2)); return 0
    if args.cmd == "checkpoint":
        value = checkpoint(root, args.status, args.target, args.next_action, args.blocker, args.note, args.last_action, args.file)
        print(json.dumps(summary(value), indent=2)); return 0
    if args.cmd == "pause":
        print(json.dumps(summary(pause(root, args.note)), indent=2)); return 0
    if args.cmd == "resume":
        print(json.dumps(summary(resume(root, args.note)), indent=2)); return 0
    if args.cmd == "reset":
        print(json.dumps(summary(reset_target(root, args.target, args.note)), indent=2)); return 0
    value = load_progress(root)
    if args.cmd == "validate":
        validate_progress(value); print("OK pipeline progress"); return 0
    print(json.dumps(value if args.full else summary(value), indent=2)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
