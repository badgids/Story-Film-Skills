# Sanitized ComfyUI Workflow Blueprints

These JSON files are portable topology references derived from production workflows.
They are not runnable defaults and they do not select model files for the user.

Before use:

1. Read `../COMFYUI_WORKFLOW_CONTRACTS.md`.
2. Read `../../docs/generation/sanitized-workflows.md`.
3. Check `../comfyui_workflow_dependencies.json` for optional node packages.
4. Resolve model resources from the live ComfyUI server and the project model preferences.
5. Validate all node classes and links against the live `/object_info` schema.
6. Audit reference bindings after conversion or patching.
7. Promote only the resulting live-validated project copy.

Story-Film does not install optional custom nodes automatically and does not submit these
blueprints directly.
