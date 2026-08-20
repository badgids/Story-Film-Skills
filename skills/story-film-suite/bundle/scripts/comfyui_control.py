#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any
from datetime import datetime, timezone

from comfyui_workflow import api_nodes, detect_format, load_json, validate_offline

DEFAULT_URL = "http://127.0.0.1:8188"
TOKEN_RE = re.compile(r'(api_key_comfy_org|auth_token_comfy_org|access_token|refresh_token)(["\s:=]+)([^"\s,}]+)', re.I)
BEARER_RE = re.compile(r'Bearer\s+[^\s"\']+', re.I)




def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def project_comfy_dir(project: str | Path | None) -> Path | None:
    if project is None:
        return None
    root = Path(project).expanduser().resolve()
    target = root / "04_generation/comfyui"
    for child in ("workflows", "templates", "fragments", "blueprints", "inputs", "runs", "outputs"):
        (target / child).mkdir(parents=True, exist_ok=True)
    return target


def project_relative(project: str | Path | None, value: str | Path) -> str:
    p = Path(value).expanduser().resolve()
    if project is None:
        return str(p)
    root = Path(project).expanduser().resolve()
    try:
        return p.relative_to(root).as_posix()
    except ValueError:
        return str(p)


def sanitize_obj(value: Any) -> Any:
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            low = str(key).lower()
            if any(token in low for token in ("api_key", "auth_token", "access_token", "refresh_token")):
                out[key] = "***"
            else:
                out[key] = sanitize_obj(item)
        return out
    if isinstance(value, list):
        return [sanitize_obj(x) for x in value]
    if isinstance(value, tuple):
        return [sanitize_obj(x) for x in value]
    if isinstance(value, str):
        return redact(value)
    return value


def save_snapshot(project: str | Path | None, snapshot: dict[str, Any]) -> None:
    target = project_comfy_dir(project)
    if target is None:
        return
    clean = sanitize_obj(snapshot)
    system = clean.get("system_stats", {}).get("system") if isinstance(clean.get("system_stats"), dict) else None
    if isinstance(system, dict):
        system.pop("argv", None)
    clean["captured_at"] = now_iso()
    (target / "server_snapshot.json").write_text(json.dumps(clean, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_record_path(project: str | Path | None, prompt_id: str) -> Path | None:
    target = project_comfy_dir(project)
    if target is None:
        return None
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", prompt_id)
    return target / "runs" / f"{safe}.json"


def load_run_record(project: str | Path | None, prompt_id: str) -> dict[str, Any]:
    path = run_record_path(project, prompt_id)
    if path is None or not path.is_file():
        return {"schema_version": 1, "prompt_id": prompt_id}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {"schema_version": 1, "prompt_id": prompt_id}
    except (OSError, json.JSONDecodeError):
        return {"schema_version": 1, "prompt_id": prompt_id}


def save_run_record(project: str | Path | None, prompt_id: str, updates: dict[str, Any]) -> None:
    path = run_record_path(project, prompt_id)
    if path is None:
        return
    record = load_run_record(project, prompt_id)
    record.update(sanitize_obj(updates))
    record["schema_version"] = 1
    record["prompt_id"] = prompt_id
    record["last_updated"] = now_iso()
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_run_event(project: str | Path | None, event: dict[str, Any]) -> None:
    target = project_comfy_dir(project)
    if target is None:
        return
    row = sanitize_obj(event)
    row["timestamp"] = now_iso()
    with (target / "run_index.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def redact(text: str) -> str:
    if not text:
        return text
    text = BEARER_RE.sub("Bearer ***", text)
    return TOKEN_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}***", text)


def resolve_url(explicit: str | None) -> str:
    raw = explicit or os.getenv("BADGIDS_COMFYUI_URL") or os.getenv("COMFY_LOCAL_URL") or os.getenv("COMFYUI_URL") or DEFAULT_URL
    raw = raw.strip().rstrip("/")
    if "://" not in raw:
        raw = "http://" + raw
    parsed = urllib.parse.urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"invalid ComfyUI URL: {raw!r}")
    if parsed.username or parsed.password:
        raise ValueError("do not embed credentials in the ComfyUI URL")
    return raw


class ComfyError(RuntimeError):
    def __init__(self, status: int | None, message: str, body: str = ""):
        clean_body = redact(body)
        clean_message = redact(message)
        super().__init__(f"HTTP {status}: {clean_message}" if status is not None else clean_message)
        self.status = status
        self.body = clean_body


class Client:
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = resolve_url(base_url)
        self.timeout = timeout

    def url(self, path: str, query: dict[str, Any] | None = None) -> str:
        base = self.base_url + "/" + path.lstrip("/")
        if query:
            clean = {k: v for k, v in query.items() if v is not None and v != ""}
            if clean:
                return base + "?" + urllib.parse.urlencode(clean)
        return base

    def _request(self, method: str, path: str, *, body: Any = None, headers: dict[str, str] | None = None, raw: bool = False, query: dict[str, Any] | None = None, timeout: float | None = None) -> Any:
        data = None
        req_headers = {"Accept": "application/json", "Comfy-Usage-Source": "Story-Film Skills"}
        if headers:
            req_headers.update(headers)
        if body is not None and not isinstance(body, (bytes, bytearray)):
            data = json.dumps(body).encode("utf-8")
            req_headers["Content-Type"] = "application/json"
        elif isinstance(body, (bytes, bytearray)):
            data = bytes(body)
        req = urllib.request.Request(self.url(path, query), data=data, method=method, headers=req_headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout or self.timeout) as resp:
                payload = resp.read()
                if raw:
                    return payload, dict(resp.headers)
                if not payload:
                    return None
                text = payload.decode("utf-8", errors="replace")
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return {"text": text}
        except urllib.error.HTTPError as exc:
            body_text = ""
            try:
                body_text = exc.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            raise ComfyError(exc.code, exc.reason or "HTTP error", body_text) from exc
        except urllib.error.URLError as exc:
            raise ComfyError(None, f"cannot reach ComfyUI at {self.base_url}: {exc.reason}") from exc

    def get(self, path: str, **kwargs: Any) -> Any:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, body: Any = None, **kwargs: Any) -> Any:
        return self._request("POST", path, body=body, **kwargs)

    def probe(self) -> dict[str, Any]:
        result: dict[str, Any] = {"server": self.base_url, "reachable": False}
        stats = self.get("system_stats")
        result["reachable"] = True
        result["system_stats"] = stats
        try:
            result["features"] = self.get("features")
        except ComfyError as exc:
            result["features_error"] = str(exc)
        try:
            result["queue_info"] = self.get("prompt")
        except ComfyError as exc:
            result["queue_info_error"] = str(exc)
        return result

    def object_info(self, node_class: str | None = None) -> dict[str, Any]:
        path = "object_info" if not node_class else "object_info/" + urllib.parse.quote(node_class, safe="")
        out = self.get(path)
        return out if isinstance(out, dict) else {}

    def model_types(self) -> list[str]:
        out = self.get("models")
        return [str(x) for x in out] if isinstance(out, list) else []

    def models(self, folder: str) -> list[str]:
        out = self.get("models/" + urllib.parse.quote(folder, safe=""))
        return [str(x) for x in out] if isinstance(out, list) else []

    def _get_first(self, paths: list[str], *, query: dict[str, Any] | None = None) -> Any:
        failures: list[str] = []
        for path in paths:
            try:
                return self.get(path, query=query)
            except ComfyError as exc:
                if exc.status not in {404, 405}:
                    raise
                failures.append(str(exc))
        raise ComfyError(404, f"none of the compatible ComfyUI endpoints are available: {', '.join(paths)}", "; ".join(failures))

    def user_workflows(self) -> list[dict[str, Any]]:
        out = self._get_first(
            ["userdata", "api/userdata"],
            query={"dir": "workflows", "recurse": "true", "full_info": "true"},
        )
        rows: list[dict[str, Any]] = []
        if not isinstance(out, list):
            return rows
        for item in out:
            if isinstance(item, str):
                path = item
                meta: dict[str, Any] = {}
            elif isinstance(item, dict):
                path = str(item.get("path", ""))
                meta = dict(item)
            else:
                continue
            if not path.lower().endswith(".json"):
                continue
            rows.append({
                "source": "user",
                "name": path,
                "path": f"workflows/{path}" if not path.startswith("workflows/") else path,
                "size": meta.get("size"),
                "modified": meta.get("modified"),
            })
        return rows

    def template_catalog(self) -> tuple[list[dict[str, Any]], list[str]]:
        entries: list[dict[str, Any]] = []
        warnings: list[str] = []
        try:
            core = self.get("templates/index.json")
            if isinstance(core, list):
                for group in core:
                    if not isinstance(group, dict):
                        continue
                    for item in group.get("templates", []) if isinstance(group.get("templates"), list) else []:
                        if not isinstance(item, dict) or not item.get("name"):
                            continue
                        entries.append({
                            "source": "core",
                            "name": str(item["name"]),
                            "title": item.get("title"),
                            "category": group.get("category") or group.get("title"),
                            "media_type": group.get("type") or item.get("mediaType"),
                            "description": item.get("description"),
                            "models": item.get("models", []),
                            "tags": item.get("tags", []),
                        })
        except ComfyError as exc:
            if exc.status not in {404, 405}:
                raise
            warnings.append(f"core template index unavailable: {exc}")

        try:
            custom = self._get_first(["workflow_templates", "api/workflow_templates"])
            if isinstance(custom, dict):
                for module, names in custom.items():
                    if not isinstance(names, list):
                        continue
                    for name in names:
                        if isinstance(name, str) and name:
                            entries.append({"source": "custom", "module": str(module), "name": name})
        except ComfyError as exc:
            if exc.status not in {404, 405}:
                raise
            warnings.append(f"custom-node workflow template index unavailable: {exc}")
        return entries, warnings

    def workflow_catalog(
        self,
        project: str | Path | None = None,
        *,
        query: str | None = None,
        source: str | None = None,
    ) -> dict[str, Any]:
        entries: list[dict[str, Any]] = []
        warnings: list[str] = []
        if project is not None:
            root = Path(project).expanduser().resolve()
            for source_name, rel in (
                ("project-workflow", "04_generation/comfyui/workflows"),
                ("project-template", "04_generation/comfyui/templates"),
            ):
                folder = root / rel
                if not folder.is_dir():
                    continue
                for path in sorted(folder.rglob("*.json")):
                    try:
                        data = load_json(path)
                        fmt = detect_format(data)
                    except (OSError, json.JSONDecodeError):
                        fmt = "invalid"
                    entries.append({
                        "source": source_name,
                        "name": path.name,
                        "path": path.relative_to(root).as_posix(),
                        "format": fmt,
                    })
        try:
            entries.extend(self.user_workflows())
        except ComfyError as exc:
            if exc.status not in {404, 405}:
                raise
            warnings.append(f"ComfyUI user workflow listing unavailable: {exc}")
        remote_templates, template_warnings = self.template_catalog()
        entries.extend(remote_templates)
        warnings.extend(template_warnings)
        if source:
            entries = [x for x in entries if x.get("source") == source]
        if query:
            needle = query.lower()
            entries = [
                x for x in entries
                if needle in json.dumps(x, ensure_ascii=False, sort_keys=True).lower()
            ]
        priority = {"project-workflow": 0, "project-template": 1, "user": 2, "core": 3, "custom": 4}
        entries.sort(key=lambda x: (priority.get(str(x.get("source")), 99), str(x.get("name", "")).lower()))
        return {"count": len(entries), "workflows": entries, "warnings": warnings}

    @staticmethod
    def _safe_template_segment(value: str, label: str) -> str:
        clean = value.strip()
        if clean.lower().endswith(".json"):
            clean = clean[:-5]
        if not clean or clean in {".", ".."} or "/" in clean or "\\" in clean:
            raise ValueError(f"{label} must be a single workflow/template name, not a path")
        return clean

    def fetch_workflow_source(self, source: str, name: str, *, module: str | None = None) -> dict[str, Any]:
        if source == "user":
            rel = name.strip().replace("\\", "/")
            if not rel:
                raise ValueError("user workflow name is required")
            if not rel.startswith("workflows/"):
                rel = "workflows/" + rel
            if not rel.lower().endswith(".json"):
                rel += ".json"
            encoded = urllib.parse.quote(rel, safe="")
            out = self._get_first([f"userdata/{encoded}", f"api/userdata/{encoded}"])
        elif source == "core":
            clean = self._safe_template_segment(name, "core template name")
            out = self.get(f"templates/{urllib.parse.quote(clean, safe='')}.json")
        elif source == "custom":
            clean = self._safe_template_segment(name, "custom template name")
            mod = self._safe_template_segment(module or "", "custom template module")
            route = f"workflow_templates/{urllib.parse.quote(mod, safe='')}/{urllib.parse.quote(clean, safe='')}.json"
            out = self._get_first([f"api/{route}", route])
        else:
            raise ValueError("workflow source must be one of: user, core, custom")
        if not isinstance(out, dict):
            raise ValueError(f"{source} workflow/template did not return a JSON object")
        return out

    def validate_workflow(self, workflow: dict[str, Any]) -> dict[str, Any]:
        errors = validate_offline(workflow)
        fmt = detect_format(workflow)
        if fmt != "api":
            return {"format": fmt, "valid": False, "errors": errors, "warnings": []}
        live = self.object_info()
        warnings: list[str] = []
        nodes = api_nodes(workflow)
        output_nodes: list[str] = []
        for node_id, node in nodes.items():
            cls = str(node.get("class_type", ""))
            schema = live.get(cls)
            if not isinstance(schema, dict):
                errors.append(f"node {node_id}: class {cls!r} is not installed on the live server")
                continue
            inputs = node.get("inputs") if isinstance(node.get("inputs"), dict) else {}
            schema_input = schema.get("input") if isinstance(schema.get("input"), dict) else {}
            required = schema_input.get("required") if isinstance(schema_input.get("required"), dict) else {}
            optional = schema_input.get("optional") if isinstance(schema_input.get("optional"), dict) else {}
            for name in required:
                if name not in inputs:
                    errors.append(f"node {node_id} ({cls}): missing required input {name!r}")
            for name, value in inputs.items():
                spec = required.get(name, optional.get(name))
                if not isinstance(spec, (list, tuple)) or not spec:
                    continue
                choices = spec[0]
                linked = isinstance(value, list) and len(value) == 2 and isinstance(value[1], int)
                if isinstance(choices, list) and choices and not linked and value not in choices:
                    errors.append(f"node {node_id} ({cls}): input {name!r} value {value!r} is not in the live server choices")
            if schema.get("output_node"):
                output_nodes.append(str(node_id))
            if schema.get("deprecated"):
                warnings.append(f"node {node_id} ({cls}) is marked deprecated by the live server")
            if schema.get("experimental"):
                warnings.append(f"node {node_id} ({cls}) is marked experimental by the live server")
        if not output_nodes:
            warnings.append("workflow has no node marked output_node by the live server; generated media or text may not be retrievable")
        return {
            "format": fmt,
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
            "node_count": len(nodes),
            "output_nodes": output_nodes,
        }

    def submit(self, workflow: dict[str, Any], *, client_id: str | None = None, api_key_env: str | None = None) -> dict[str, Any]:
        if detect_format(workflow) != "api":
            raise ValueError("native submission requires API-format workflow JSON")
        payload: dict[str, Any] = {"prompt": workflow, "client_id": client_id or uuid.uuid4().hex}
        if api_key_env:
            key = os.getenv(api_key_env)
            if key:
                payload["extra_data"] = {"api_key_comfy_org": key, "comfy_usage_source": "Story-Film Skills"}
        return self.post("prompt", payload) or {}

    def history(self, prompt_id: str | None = None) -> dict[str, Any]:
        path = "history" if prompt_id is None else "history/" + urllib.parse.quote(prompt_id, safe="")
        out = self.get(path)
        return out if isinstance(out, dict) else {}

    def queue(self) -> dict[str, Any]:
        out = self.get("queue")
        return out if isinstance(out, dict) else {}

    def cancel(self, prompt_id: str) -> dict[str, Any]:
        encoded = urllib.parse.quote(prompt_id, safe="")
        try:
            out = self.post(f"api/jobs/{encoded}/cancel", {})
            if isinstance(out, dict):
                return {"method": "api_job_cancel", **out}
            return {"method": "api_job_cancel", "cancelled": True}
        except ComfyError as exc:
            if exc.status not in {404, 405}:
                raise
        q = self.queue()
        pending = q.get("queue_pending") if isinstance(q.get("queue_pending"), list) else []
        running = q.get("queue_running") if isinstance(q.get("queue_running"), list) else []
        if any(isinstance(x, list) and len(x) > 1 and str(x[1]) == prompt_id for x in pending):
            self.post("queue", {"delete": [prompt_id]})
            return {"method": "queue_delete", "cancelled": True}
        if any(isinstance(x, list) and len(x) > 1 and str(x[1]) == prompt_id for x in running):
            self.post("interrupt", {"prompt_id": prompt_id})
            return {"method": "targeted_interrupt", "cancelled": True}
        return {"method": "none", "cancelled": False, "reason": "job not running or pending"}

    def wait(self, prompt_id: str, *, timeout: float = 600.0, poll_interval: float = 2.0) -> dict[str, Any]:
        start = time.time()
        consecutive_errors = 0
        while True:
            try:
                hist = self.history(prompt_id)
                consecutive_errors = 0
            except ComfyError as exc:
                if exc.status == 429 or (exc.status is not None and 500 <= exc.status < 600):
                    consecutive_errors += 1
                    if consecutive_errors >= 5:
                        raise
                    time.sleep(min(2 ** consecutive_errors, 30))
                    continue
                raise
            record = hist.get(prompt_id) if prompt_id in hist else None
            if isinstance(record, dict):
                status = record.get("status") or record.get("execution_status") or {}
                has_status_signal = False
                if isinstance(status, dict):
                    has_status_signal = "completed" in status or "status_str" in status
                    if status.get("completed") is True or status.get("status_str") in {"success", "error", "failed", "cancelled", "canceled"}:
                        return record
                if record.get("outputs") and not has_status_signal:
                    return record
            if time.time() - start >= timeout:
                raise TimeoutError(f"workflow {prompt_id} did not finish within {timeout} seconds")
            time.sleep(poll_interval + random.uniform(0, min(poll_interval, 0.5)))

    def upload_image(self, path: Path, *, subfolder: str = "", overwrite: bool = False, upload_type: str = "input") -> dict[str, Any]:
        if not path.is_file():
            raise FileNotFoundError(path)
        boundary = "----BadgidsStoryFilm" + uuid.uuid4().hex
        fields = {
            "type": upload_type,
            "subfolder": subfolder,
            "overwrite": "true" if overwrite else "false",
        }
        content = path.read_bytes()
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        parts: list[bytes] = []
        for key, value in fields.items():
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}\r\n".encode())
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{path.name}\"\r\nContent-Type: {mime}\r\n\r\n".encode()
            + content
            + b"\r\n"
        )
        parts.append(f"--{boundary}--\r\n".encode())
        body = b"".join(parts)
        out = self.post("upload/image", body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        return out if isinstance(out, dict) else {}

    def upload_mask(
        self,
        path: Path,
        *,
        original_filename: str,
        original_subfolder: str = "",
        original_type: str = "output",
        subfolder: str = "",
        overwrite: bool = False,
        upload_type: str = "input",
    ) -> dict[str, Any]:
        if not path.is_file():
            raise FileNotFoundError(path)
        if not original_filename or Path(original_filename).name != original_filename:
            raise ValueError("original filename must be a plain filename")
        original_ref = {
            "filename": original_filename,
            "subfolder": original_subfolder,
            "type": original_type,
        }
        boundary = "----BadgidsStoryFilm" + uuid.uuid4().hex
        fields = {
            "type": upload_type,
            "subfolder": subfolder,
            "overwrite": "true" if overwrite else "false",
            "original_ref": json.dumps(original_ref, separators=(",", ":")),
        }
        content = path.read_bytes()
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        parts: list[bytes] = []
        for key, value in fields.items():
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}\r\n".encode())
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{path.name}\"\r\nContent-Type: {mime}\r\n\r\n".encode()
            + content
            + b"\r\n"
        )
        parts.append(f"--{boundary}--\r\n".encode())
        body = b"".join(parts)
        out = self.post("upload/mask", body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
        return out if isinstance(out, dict) else {}

    @staticmethod
    def output_entries(record: dict[str, Any]) -> tuple[list[dict[str, str]], dict[str, list[str]]]:
        files: list[dict[str, str]] = []
        texts: dict[str, list[str]] = {}
        seen: set[tuple[str, str, str, str]] = set()
        outputs = record.get("outputs")
        if not isinstance(outputs, dict):
            return files, texts
        for node_id, node_output in outputs.items():
            if not isinstance(node_output, dict):
                continue
            text_items = node_output.get("text")
            if isinstance(text_items, list):
                strings = [x for x in text_items if isinstance(x, str)]
                if strings:
                    texts[str(node_id)] = strings
            for key, items in node_output.items():
                if key == "animated" or not isinstance(items, list):
                    continue
                for item in items:
                    if isinstance(item, dict) and "filename" in item:
                        entry = {
                            "node_id": str(node_id),
                            "filename": str(item.get("filename", "")),
                            "subfolder": str(item.get("subfolder", "")),
                            "type": str(item.get("type", "output")),
                        }
                        sig = (entry["node_id"], entry["filename"], entry["subfolder"], entry["type"])
                        if sig not in seen:
                            seen.add(sig)
                            files.append(entry)
        return files, texts

    def outputs(self, prompt_id: str) -> dict[str, Any]:
        hist = self.history(prompt_id)
        record = hist.get(prompt_id) if isinstance(hist.get(prompt_id), dict) else hist
        if not isinstance(record, dict):
            return {"prompt_id": prompt_id, "files": [], "text": {}}
        files, texts = self.output_entries(record)
        for entry in files:
            entry["url"] = self.url("view", {
                "filename": entry["filename"],
                "subfolder": entry["subfolder"],
                "type": entry["type"],
            })
        return {"prompt_id": prompt_id, "files": files, "text": texts}

    def download_outputs(self, prompt_id: str, out_dir: Path) -> dict[str, Any]:
        data = self.outputs(prompt_id)
        out_dir.mkdir(parents=True, exist_ok=True)
        written: list[dict[str, str]] = []
        for i, entry in enumerate(data["files"], start=1):
            safe = Path(entry["filename"]).name
            if not safe:
                safe = f"output-{i}.bin"
            target = out_dir / safe
            if target.exists():
                stem, suffix = target.stem, target.suffix
                n = 1
                while target.exists():
                    target = out_dir / f"{stem}-{n}{suffix}"
                    n += 1
            payload, headers = self._request("GET", "view", raw=True, query={
                "filename": entry["filename"],
                "subfolder": entry["subfolder"],
                "type": entry["type"],
            })
            target.write_bytes(payload)
            written.append({"node_id": entry["node_id"], "path": str(target), "content_type": str(headers.get("Content-Type", ""))})
        return {"prompt_id": prompt_id, "written": written, "text": data["text"]}

    def free(self, *, unload_models: bool, free_memory: bool) -> dict[str, Any]:
        self.post("free", {"unload_models": unload_models, "free_memory": free_memory})
        return {"requested": True, "unload_models": unload_models, "free_memory": free_memory}


def emit(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def main() -> int:
    ap = argparse.ArgumentParser(description="Dependency-free ComfyUI native API controller.")
    ap.add_argument("--url", help="ComfyUI base URL. Defaults to BADGIDS_COMFYUI_URL, COMFY_LOCAL_URL, COMFYUI_URL, then 127.0.0.1:8188.")
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--project", help="Optional story-film project root. Records ComfyUI snapshots and runs under 04_generation/comfyui.")
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("probe")

    p = sub.add_parser("nodes")
    p.add_argument("--query")
    p.add_argument("--category")
    p.add_argument("--output-type")
    p.add_argument("--node-class")

    p = sub.add_parser("models")
    p.add_argument("--folder")
    p.add_argument("--query")

    p = sub.add_parser("workflow-catalog")
    p.add_argument("--query")
    p.add_argument("--source", choices=["project-workflow", "project-template", "user", "core", "custom"])

    p = sub.add_parser("workflow-fetch")
    p.add_argument("--source", required=True, choices=["user", "core", "custom"])
    p.add_argument("--name", required=True)
    p.add_argument("--module")
    p.add_argument("--out", required=True)

    p = sub.add_parser("workflow-promote")
    p.add_argument("--candidate", required=True)
    p.add_argument("--out", required=True)

    p = sub.add_parser("validate")
    p.add_argument("--workflow", required=True)

    p = sub.add_parser("submit")
    p.add_argument("--workflow", required=True)
    p.add_argument("--client-id")
    p.add_argument("--api-key-env", default="COMFY_API_KEY")
    p.add_argument("--no-validate", action="store_true")
    p.add_argument("--item-id", help="Optional stable story-film item ID such as SHOT-001, VOICE-001, MUS-001, or SFX-001.")

    p = sub.add_parser("wait")
    p.add_argument("prompt_id")
    p.add_argument("--wait-timeout", type=float, default=600.0)
    p.add_argument("--poll", type=float, default=2.0)

    sub.add_parser("queue")
    p = sub.add_parser("history")
    p.add_argument("--prompt-id")

    p = sub.add_parser("cancel")
    p.add_argument("prompt_id")

    p = sub.add_parser("upload")
    p.add_argument("path")
    p.add_argument("--subfolder", default="")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--type", default="input", choices=["input", "temp", "output"])

    p = sub.add_parser("upload-mask")
    p.add_argument("path")
    p.add_argument("--original-filename", required=True)
    p.add_argument("--original-subfolder", default="")
    p.add_argument("--original-type", default="output", choices=["input", "temp", "output"])
    p.add_argument("--subfolder", default="")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--type", default="input", choices=["input", "temp", "output"])

    p = sub.add_parser("outputs")
    p.add_argument("prompt_id")

    p = sub.add_parser("download")
    p.add_argument("prompt_id")
    p.add_argument("--out-dir", required=True)

    p = sub.add_parser("free")
    p.add_argument("--unload-models", action="store_true")
    p.add_argument("--free-memory", action="store_true")

    args = ap.parse_args()
    try:
        client = Client(resolve_url(args.url), timeout=args.timeout)
        if args.command == "probe":
            result = client.probe()
            save_snapshot(args.project, result)
            emit(result)
        elif args.command == "nodes":
            if args.node_class:
                emit(client.object_info(args.node_class))
            else:
                info = client.object_info()
                q = (args.query or "").lower()
                category = (args.category or "").lower()
                output_type = args.output_type or ""
                rows = []
                for cls, schema in info.items():
                    if not isinstance(schema, dict):
                        continue
                    hay = " ".join([
                        str(cls), str(schema.get("display_name", "")), str(schema.get("category", "")),
                        str(schema.get("description", "")), " ".join(map(str, schema.get("search_aliases", []) or [])),
                    ]).lower()
                    if q and q not in hay:
                        continue
                    if category and category not in str(schema.get("category", "")).lower():
                        continue
                    outputs = [str(x) for x in (schema.get("output") or [])]
                    if output_type and output_type not in outputs:
                        continue
                    rows.append({
                        "class_type": cls,
                        "display_name": schema.get("display_name"),
                        "category": schema.get("category"),
                        "outputs": outputs,
                        "deprecated": bool(schema.get("deprecated")),
                        "experimental": bool(schema.get("experimental")),
                        "api_node": schema.get("api_node"),
                    })
                emit({"count": len(rows), "nodes": rows})
        elif args.command == "models":
            if not args.folder:
                folders = client.model_types()
                if args.query:
                    q = args.query.lower()
                    folders = [x for x in folders if q in x.lower()]
                emit({"folders": folders})
            else:
                models = client.models(args.folder)
                if args.query:
                    q = args.query.lower()
                    models = [x for x in models if q in x.lower()]
                emit({"folder": args.folder, "models": models})
        elif args.command == "workflow-catalog":
            emit(client.workflow_catalog(args.project, query=args.query, source=args.source))
        elif args.command == "workflow-fetch":
            workflow = client.fetch_workflow_source(args.source, args.name, module=args.module)
            out = Path(args.out).expanduser()
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            fmt = detect_format(workflow)
            result: dict[str, Any] = {
                "written": project_relative(args.project, out),
                "source": args.source,
                "name": args.name,
                "module": args.module,
                "format": fmt,
            }
            if fmt == "api":
                result["validation"] = client.validate_workflow(workflow)
            emit(result)
        elif args.command == "workflow-promote":
            workflow = load_json(args.candidate)
            verdict = client.validate_workflow(workflow)
            if not verdict["valid"]:
                emit({"promoted": False, "validation": verdict})
                return 2
            out = Path(args.out).expanduser()
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            emit({
                "promoted": True,
                "candidate": project_relative(args.project, args.candidate),
                "written": project_relative(args.project, out),
                "validation": verdict,
            })
        elif args.command == "validate":
            wf = load_json(args.workflow)
            emit(client.validate_workflow(wf))
        elif args.command == "submit":
            wf = load_json(args.workflow)
            if not args.no_validate:
                verdict = client.validate_workflow(wf)
                if not verdict["valid"]:
                    emit({"submitted": False, "validation": verdict})
                    return 2
            result = client.submit(wf, client_id=args.client_id, api_key_env=args.api_key_env)
            prompt_id = str(result.get("prompt_id", ""))
            if prompt_id:
                save_run_record(args.project, prompt_id, {
                    "server": client.base_url,
                    "workflow_path": project_relative(args.project, args.workflow),
                    "submitted_at": now_iso(),
                    "status": "submitted",
                    "item_id": args.item_id,
                    "node_errors": result.get("node_errors", {}),
                })
                append_run_event(args.project, {
                    "event": "submit",
                    "item_id": args.item_id,
                    "prompt_id": prompt_id,
                    "workflow_path": project_relative(args.project, args.workflow),
                    "status": "submitted",
                })
            emit({"submitted": True, **result})
        elif args.command == "wait":
            result = client.wait(args.prompt_id, timeout=args.wait_timeout, poll_interval=args.poll)
            status_obj = result.get("status") or result.get("execution_status") or {} if isinstance(result, dict) else {}
            status = status_obj.get("status_str") if isinstance(status_obj, dict) else None
            files, texts = client.output_entries(result if isinstance(result, dict) else {})
            existing = load_run_record(args.project, args.prompt_id)
            save_run_record(args.project, args.prompt_id, {
                "completed_at": now_iso(),
                "status": status or "completed",
                "outputs": files,
                "text_outputs": texts,
                "execution_messages": status_obj.get("messages", []) if isinstance(status_obj, dict) else [],
            })
            append_run_event(args.project, {
                "event": "complete",
                "item_id": existing.get("item_id"),
                "prompt_id": args.prompt_id,
                "status": status or "completed",
                "output_count": len(files),
            })
            emit(result)
        elif args.command == "queue":
            emit(client.queue())
        elif args.command == "history":
            emit(client.history(args.prompt_id))
        elif args.command == "cancel":
            result = client.cancel(args.prompt_id)
            existing = load_run_record(args.project, args.prompt_id)
            save_run_record(args.project, args.prompt_id, {"cancel_requested_at": now_iso(), "cancel": result})
            append_run_event(args.project, {"event": "cancel", "item_id": existing.get("item_id"), "prompt_id": args.prompt_id, "cancelled": result.get("cancelled")})
            emit(result)
        elif args.command == "upload":
            emit(client.upload_image(Path(args.path), subfolder=args.subfolder, overwrite=args.overwrite, upload_type=args.type))
        elif args.command == "upload-mask":
            emit(client.upload_mask(
                Path(args.path),
                original_filename=args.original_filename,
                original_subfolder=args.original_subfolder,
                original_type=args.original_type,
                subfolder=args.subfolder,
                overwrite=args.overwrite,
                upload_type=args.type,
            ))
        elif args.command == "outputs":
            emit(client.outputs(args.prompt_id))
        elif args.command == "download":
            result = client.download_outputs(args.prompt_id, Path(args.out_dir))
            recorded = []
            for item in result.get("written", []):
                row = dict(item)
                if "path" in row:
                    row["path"] = project_relative(args.project, row["path"])
                recorded.append(row)
            existing = load_run_record(args.project, args.prompt_id)
            save_run_record(args.project, args.prompt_id, {
                "outputs_collected_at": now_iso(),
                "outputs": recorded,
                "text_outputs": result.get("text", {}),
            })
            append_run_event(args.project, {
                "event": "download",
                "item_id": existing.get("item_id"),
                "prompt_id": args.prompt_id,
                "output_count": len(recorded),
            })
            emit(result)
        elif args.command == "free":
            emit(client.free(unload_models=args.unload_models, free_memory=args.free_memory))
        return 0
    except (ComfyError, ValueError, FileNotFoundError, TimeoutError, json.JSONDecodeError) as exc:
        body = getattr(exc, "body", "")
        emit({"ok": False, "error": redact(str(exc)), "details": redact(body) if body else ""})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
