---
name: comfyui-troubleshoot
description: Diagnose ComfyUI connection failures, invalid workflows, unknown node classes, missing required inputs, missing models, queue and history problems, generation errors, VRAM pressure, remote-target confusion, and dependency issues without random installs or broad destructive changes.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# ComfyUI Troubleshoot

## Read

- `../../references/COMFYUI_OPERATIONS.md`
- `../../references/COMFYUI_NATIVE_API.md`
- `../../references/COMFYUI_WORKFLOWS.md`
- `../../references/COMFYUI_SECURITY.md`

## Order

1. Confirm the exact server URL and whether it is local or remote.
2. Probe system stats and queue state.
3. Capture the exact HTTP error, ComfyUI execution error, and `node_errors`.
4. Validate workflow format.
5. Compare required class types against live `/object_info`.
6. Compare loader selections against live input choices or model categories.
7. Check input uploads and server-returned filenames.
8. Check free VRAM for heavy execution failures.
9. Identify the smallest corrective action.
10. Revalidate before rerunning.

## Missing node

An unknown class does not justify guessing a repository. If comfy-cli or comfy-mcp can resolve workflow dependencies to a registry package, present that package and obtain approval before installation.

## Missing model

Report the exact loader node, required value, and live available choices. Do not rename a different model into place or download a large replacement without user intent.

## VRAM

`POST /free` can unload ComfyUI-held models and cache. It cannot free memory held by another application. Do not claim it can stop or unload an external LLM runtime.

## Connection

Do not solve a connection problem by exposing ComfyUI on all network interfaces without explicit user intent and an appropriate security boundary.

## Done

The root cause is tied to observed server/workflow evidence, and the proposed fix is the smallest change that addresses it.
