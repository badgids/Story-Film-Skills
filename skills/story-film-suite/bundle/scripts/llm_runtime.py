#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Classify whether a configured LLM endpoint is local to this machine.

This helper is intentionally conservative. A loopback or local-interface endpoint is
local. A nonlocal endpoint is unknown unless the user or another trusted runtime
source explicitly proves that it is external.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import socket
from urllib.parse import urlparse

LOCAL_NAMES = {"localhost", "localhost.localdomain"}
ENV_ENDPOINTS = (
    "LLAMA_SERVER",
    "LLAMA_SERVER_URL",
    "OPENAI_BASE_URL",
    "OPENAI_API_BASE",
    "OLLAMA_HOST",
)


def _parse_endpoint(endpoint: str) -> tuple[str, str]:
    text = (endpoint or "").strip()
    if not text:
        return "", ""
    if text.startswith("unix://"):
        return "unix", ""
    candidate = text if "://" in text else "http://" + text
    parsed = urlparse(candidate)
    return parsed.scheme.lower(), (parsed.hostname or "").strip().lower()


def _local_addresses() -> set[str]:
    out = {"127.0.0.1", "::1"}
    for name in {socket.gethostname(), socket.getfqdn()}:
        try:
            for item in socket.getaddrinfo(name, None):
                out.add(str(item[4][0]).split("%", 1)[0])
        except OSError:
            pass
    return out


def classify_endpoint(endpoint: str) -> dict[str, object]:
    scheme, host = _parse_endpoint(endpoint)
    evidence: list[str] = []
    if not endpoint:
        return {"location": "unknown", "endpoint": "", "evidence": ["No endpoint was supplied."]}
    if scheme == "unix":
        return {"location": "local", "endpoint": endpoint, "evidence": ["Unix-domain socket endpoints are local to this machine."]}
    if not host:
        return {"location": "unknown", "endpoint": endpoint, "evidence": ["The endpoint host could not be parsed."]}
    if host in LOCAL_NAMES:
        return {"location": "local", "endpoint": endpoint, "evidence": [f"Host {host} is a loopback name."]}
    bare_host = host.split("%", 1)[0]
    try:
        ip = ipaddress.ip_address(bare_host)
        if ip.is_loopback or ip.is_unspecified:
            return {"location": "local", "endpoint": endpoint, "evidence": [f"Host {host} is a local-only address."]}
        if bare_host in _local_addresses():
            return {"location": "local", "endpoint": endpoint, "evidence": [f"Host {host} matches a local interface address."]}
        return {"location": "unknown", "endpoint": endpoint, "evidence": [f"Host {host} does not prove that the model is on this machine or off this machine."]}
    except ValueError:
        pass
    try:
        resolved = {str(item[4][0]).split("%", 1)[0] for item in socket.getaddrinfo(host, None)}
    except OSError:
        resolved = set()
    local = _local_addresses()
    overlap = sorted(resolved & local)
    if overlap:
        evidence.append(f"Host {host} resolves to local interface address {overlap[0]}.")
        return {"location": "local", "endpoint": endpoint, "evidence": evidence}
    evidence.append(f"Host {host} is not proven local. Do not call it external without explicit evidence.")
    return {"location": "unknown", "endpoint": endpoint, "evidence": evidence}


def discover(explicit: list[str]) -> dict[str, object]:
    candidates: list[dict[str, object]] = []
    seen: set[str] = set()
    for source, value in [("argument", x) for x in explicit]:
        if value and value not in seen:
            seen.add(value)
            row = classify_endpoint(value)
            row["source"] = source
            candidates.append(row)
    for key in ENV_ENDPOINTS:
        value = os.environ.get(key, "").strip()
        if value and value not in seen:
            seen.add(value)
            row = classify_endpoint(value)
            row["source"] = f"environment:{key}"
            candidates.append(row)
    local = [x for x in candidates if x.get("location") == "local"]
    location = "local" if local else "unknown"
    return {
        "schema_version": 1,
        "location": location,
        "candidates": candidates,
        "rule": "External is never inferred from API compatibility, provider name, or missing environment variables.",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Classify Story-Film local LLM endpoint evidence.")
    ap.add_argument("--endpoint", action="append", default=[], help="Candidate LLM base URL. May be repeated.")
    args = ap.parse_args()
    print(json.dumps(discover(args.endpoint), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
