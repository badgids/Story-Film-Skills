# ComfyUI Workflow Contracts

A ComfyUI graph can be structurally valid yet still be the wrong production workflow. Story-Film therefore supports reusable workflow-family contracts in addition to live `/object_info` validation.

A contract declares media type, required capabilities, required or optional node classes, required output capability, custom-node dependencies, and whether a workflow depends on a remote service.

Contracts do not grant permission to install nodes, download models, use credentials, or spend money. Story-Film detects capabilities and reports missing dependencies. Installation remains a user action.

Sanitized workflow blueprints live under `references/comfyui_workflows/`. They are topology/reference sources, not executable defaults. Before promotion, the bounded workflow pipeline must:

1. inspect the live node schemas;
2. resolve the user's selected model resources;
3. replace sanitized placeholders;
4. validate class types and links;
5. audit reference bindings;
6. promote only the validated API graph.
