#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any

from comfyui_workflow import detect_format, load_json

DEFAULT_URL = "http://127.0.0.1:8189"


def resolve_url(explicit: str | None) -> str:
    raw = explicit or os.getenv("COMFY_API_V2_URL") or DEFAULT_URL
    raw = raw.strip().rstrip("/")
    if "://" not in raw:
        raw = "http://" + raw
    parsed = urllib.parse.urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"invalid v2 URL: {raw!r}")
    if parsed.username or parsed.password:
        raise ValueError("do not embed credentials in the v2 URL")
    return raw


class V2Error(RuntimeError):
    def __init__(self, status: int | None, message: str, body: str = ""):
        super().__init__(f"HTTP {status}: {message}" if status is not None else message)
        self.status = status
        self.body = body


class V2Client:
    def __init__(self, base_url: str, *, token_env: str = "COMFY_API_V2_TOKEN", timeout: float = 30.0):
        self.base_url = resolve_url(base_url)
        self.token_env = token_env
        self.timeout = timeout

    def url(self, path: str) -> str:
        return self.base_url + "/" + path.lstrip("/")

    def request(self, method: str, path: str, *, body: Any = None, raw_body: bytes | None = None, headers: dict[str, str] | None = None, raw_response: bool = False) -> Any:
        hdr = {"Accept": "application/json"}
        token = os.getenv(self.token_env)
        if token:
            hdr["Authorization"] = "Bearer " + token
        if headers:
            hdr.update(headers)
        data = raw_body
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            hdr["Content-Type"] = "application/json"
        req = urllib.request.Request(self.url(path), data=data, method=method, headers=hdr)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = resp.read()
                if raw_response:
                    return payload, dict(resp.headers), resp.status
                if not payload:
                    return None
                text = payload.decode("utf-8", errors="replace")
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return {"text": text}
        except urllib.error.HTTPError as exc:
            try:
                body_text = exc.read().decode("utf-8", errors="replace")
            except Exception:
                body_text = ""
            raise V2Error(exc.code, exc.reason or "HTTP error", body_text) from exc
        except urllib.error.URLError as exc:
            raise V2Error(None, f"cannot reach Comfy API v2 at {self.base_url}: {exc.reason}") from exc

    def health(self) -> Any:
        return self.request("GET", "api/v2/health")

    def submit(self, workflow: dict[str, Any], *, idempotency_key: str | None = None, api_key_env: str | None = "COMFY_API_KEY") -> Any:
        if detect_format(workflow) != "api":
            raise ValueError("Comfy API v2 requires API-format workflow JSON")
        body: dict[str, Any] = {"workflow": workflow}
        if api_key_env:
            key = os.getenv(api_key_env)
            if key:
                body["extra_data"] = {"api_key_comfy_org": key}
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else None
        return self.request("POST", "api/v2/jobs", body=body, headers=headers)

    def job(self, job_id: str) -> Any:
        return self.request("GET", "api/v2/jobs/" + urllib.parse.quote(job_id, safe=""))

    def cancel(self, job_id: str) -> Any:
        return self.request("POST", "api/v2/jobs/" + urllib.parse.quote(job_id, safe="") + "/cancel", body={})

    def wait(self, job_id: str, *, timeout: float = 600.0, poll: float = 2.0) -> Any:
        start = time.time()
        while True:
            job = self.job(job_id)
            if isinstance(job, dict):
                status = str(job.get("status", "")).lower()
                if status in {"completed", "failed", "cancelled", "canceled", "error"}:
                    return job
            if time.time() - start >= timeout:
                raise TimeoutError(f"job {job_id} did not finish within {timeout} seconds")
            time.sleep(poll)

    def upload_asset(self, path: Path, *, file_path: str | None = None, tags: list[str] | None = None, expected_hash: str | None = None, idempotency_key: str | None = None) -> Any:
        if not path.is_file():
            raise FileNotFoundError(path)
        boundary = "----BadgidsV2" + uuid.uuid4().hex
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        fields: list[tuple[str, str]] = [
            ("content_type", mime),
            ("file_path", file_path or path.name),
        ]
        if expected_hash:
            fields.append(("expected_hash", expected_hash))
        parts: list[bytes] = []
        for key, value in fields:
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}\r\n".encode())
        for tag in tags or []:
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"tags\"\r\n\r\n{tag}\r\n".encode())
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{path.name}\"\r\nContent-Type: {mime}\r\n\r\n".encode()
            + path.read_bytes()
            + b"\r\n"
        )
        parts.append(f"--{boundary}--\r\n".encode())
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return self.request("POST", "api/v2/assets", raw_body=b"".join(parts), headers=headers)

    def asset(self, asset_id: str) -> Any:
        return self.request("GET", "api/v2/assets/" + urllib.parse.quote(asset_id, safe=""))

    def download_asset(self, asset_id: str, out: Path) -> dict[str, Any]:
        payload, headers, status = self.request("GET", "api/v2/assets/" + urllib.parse.quote(asset_id, safe="") + "/content", raw_response=True)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(payload)
        return {"asset_id": asset_id, "path": str(out), "bytes": len(payload), "status": status, "content_type": headers.get("Content-Type", "")}


def emit(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def main() -> int:
    ap = argparse.ArgumentParser(description="Small Comfy API v2 client for proxy or compatible endpoint.")
    ap.add_argument("--url")
    ap.add_argument("--token-env", default="COMFY_API_V2_TOKEN")
    ap.add_argument("--timeout", type=float, default=30.0)
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("health")

    p = sub.add_parser("submit")
    p.add_argument("--workflow", required=True)
    p.add_argument("--idempotency-key")
    p.add_argument("--api-key-env", default="COMFY_API_KEY")

    p = sub.add_parser("job")
    p.add_argument("job_id")
    p = sub.add_parser("wait")
    p.add_argument("job_id")
    p.add_argument("--wait-timeout", type=float, default=600.0)
    p.add_argument("--poll", type=float, default=2.0)
    p = sub.add_parser("cancel")
    p.add_argument("job_id")

    p = sub.add_parser("upload")
    p.add_argument("path")
    p.add_argument("--file-path")
    p.add_argument("--tag", action="append", default=[])
    p.add_argument("--expected-hash")
    p.add_argument("--idempotency-key")

    p = sub.add_parser("asset")
    p.add_argument("asset_id")
    p = sub.add_parser("download-asset")
    p.add_argument("asset_id")
    p.add_argument("--out", required=True)

    args = ap.parse_args()
    try:
        c = V2Client(resolve_url(args.url), token_env=args.token_env, timeout=args.timeout)
        if args.command == "health":
            emit(c.health())
        elif args.command == "submit":
            emit(c.submit(load_json(args.workflow), idempotency_key=args.idempotency_key, api_key_env=args.api_key_env))
        elif args.command == "job":
            emit(c.job(args.job_id))
        elif args.command == "wait":
            emit(c.wait(args.job_id, timeout=args.wait_timeout, poll=args.poll))
        elif args.command == "cancel":
            emit(c.cancel(args.job_id))
        elif args.command == "upload":
            emit(c.upload_asset(Path(args.path), file_path=args.file_path, tags=args.tag, expected_hash=args.expected_hash, idempotency_key=args.idempotency_key))
        elif args.command == "asset":
            emit(c.asset(args.asset_id))
        elif args.command == "download-asset":
            emit(c.download_asset(args.asset_id, Path(args.out)))
        return 0
    except (V2Error, ValueError, FileNotFoundError, TimeoutError, json.JSONDecodeError) as exc:
        body = getattr(exc, "body", "")
        emit({"ok": False, "error": str(exc), "details": body})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
