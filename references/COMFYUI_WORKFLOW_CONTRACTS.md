# ComfyUI Workflow Contracts

A ComfyUI graph can be structurally valid yet still be the wrong production workflow. Story-Film therefore supports reusable workflow-family contracts in addition to live `/object_info` validation.

A contract declares media type, required capabilities, required or optional node classes, required output capability, custom-node dependencies, and whether a workflow depends on a remote service.

Contracts do not grant permission to install nodes, download models, use credentials, or spend money. Story-Film detects capabilities and reports missing dependencies. Installation remains a user action.

## Workflow-first sources

Complete bundled workflows live under:

```text
comfyui_workflows/<task>/<model>/
```

They are real editable workflow sources, not sanitized topology blueprints.

Additional sources can come from project defaults, saved ComfyUI user workflows, ComfyUI core/custom templates, external workflow files/directories, or a new candidate generated from live schemas. See `WORKFLOW_SELECTION.md`.

## Contract validation

Before a selected workflow becomes runnable, the bounded workflow pipeline must:

1. preserve the selected source and work from a project-owned copy;
2. inspect the live node schemas;
3. validate the node classes, links, and required inputs;
4. verify that the concrete resource names already stored in the workflow can be satisfied by the active ComfyUI server;
5. report missing optional custom-node packages without installing them;
6. stage current project inputs and approved references;
7. audit reference bindings when the workflow is reference-driven;
8. convert or promote the validated graph through the normal bounded workflow path;
9. confirm a retrievable output path.

Workflow selection does not authorize Story-Film to silently rewrite the workflow's checkpoint, VAE, text encoder, LoRAs, or other model stack. If the selected graph cannot run, report the blocker and let the user edit it, restore dependencies, or choose another workflow.
