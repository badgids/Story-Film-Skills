#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / 'references/comfyui_workflow_contracts.json'
DEPENDENCIES = ROOT / 'references/comfyui_workflow_dependencies.json'


def node_types(obj) -> set[str]:
    if isinstance(obj, dict) and isinstance(obj.get('nodes'), list):
        return {node.get('type') for node in obj['nodes'] if isinstance(node, dict) and isinstance(node.get('type'), str)}
    if isinstance(obj, dict):
        return {node.get('class_type') for node in obj.values() if isinstance(node, dict) and isinstance(node.get('class_type'), str)}
    return set()


def load_contracts() -> dict:
    return json.loads(CONTRACTS.read_text(encoding='utf-8'))


def load_dependencies() -> dict:
    return json.loads(DEPENDENCIES.read_text(encoding='utf-8'))


def dependency_for_class(class_type: str, dependencies: dict) -> dict | None:
    packages = dependencies.get('packages', {})
    values = packages.values() if isinstance(packages, dict) else packages
    for package in values:
        if class_type in package.get('required_for', []):
            return package
    return None


def validate(workflow: str | Path, contract: dict, live: set[str] | None = None) -> list[str]:
    found = node_types(json.loads(Path(workflow).read_text(encoding='utf-8')))
    errors: list[str] = []
    for class_type in contract.get('required_node_classes', []):
        if class_type not in found:
            errors.append(f'missing required workflow node {class_type}')
    if live is not None:
        for class_type in contract.get('required_node_classes', []):
            if class_type not in live:
                errors.append(f'live ComfyUI missing node {class_type}')
    return errors


def live_nodes(url: str) -> set[str]:
    with urllib.request.urlopen(url.rstrip('/') + '/object_info', timeout=10) as response:
        return set(json.load(response))


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate a ComfyUI workflow against a reusable Story-Film workflow-family contract.')
    parser.add_argument('workflow')
    parser.add_argument('--contract', required=True)
    parser.add_argument('--url')
    args = parser.parse_args()

    database = load_contracts()
    contract = database.get('contracts', {}).get(args.contract)
    if contract is None:
        print('ERROR unknown contract')
        return 2
    live = live_nodes(args.url) if args.url else None
    errors = validate(args.workflow, contract, live)
    dependencies = load_dependencies()
    for error in errors:
        print('ERROR', error)
        prefix = 'live ComfyUI missing node '
        if error.startswith(prefix):
            class_type = error[len(prefix):]
            package = dependency_for_class(class_type, dependencies)
            if package:
                print(f"SUGGEST optional package: {package['name']} - {package['repository']}")
    print('OK workflow contract' if not errors else f'FAILED {len(errors)}')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
