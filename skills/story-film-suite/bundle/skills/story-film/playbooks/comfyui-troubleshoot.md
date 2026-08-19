# Playbook: Troubleshoot ComfyUI

Use when ComfyUI is unreachable, rejects a workflow, reports missing nodes/models, fails during execution, or runs out of resources.

## Steps

1. Read `comfyui`, `comfyui-discover`, and `comfyui-troubleshoot`.
2. Confirm the intended target URL and whether it is local or remote. Do not assume a server at a personal path.
3. Probe system stats, features, queue state, live node schemas, and model lists relevant to the failing workflow.
4. Read `comfyui-workflow` and validate the exact failing workflow without altering its source copy.
5. Separate failure classes: connection, workflow format, unknown node class, missing required input, unavailable model file, invalid input, execution error, output retrieval, or resource exhaustion.
6. Prefer non-mutating diagnosis first. Installing or updating custom nodes, downloading models, switching ComfyUI versions, clearing queues/history, or changing server exposure requires explicit user intent.
7. If the official CLI is installed and its lifecycle/dependency tooling materially helps, read `comfyui-cli`. Otherwise keep using native APIs and direct evidence.
8. Revalidate after any approved repair before rerunning generation.

## Done

The root cause is tied to live evidence and the proposed or completed fix is scoped, reversible where possible, and revalidated.
