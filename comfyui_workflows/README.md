# Built-in ComfyUI workflows

Story-Film Skills uses complete ComfyUI workflows as the generation authority. A selected workflow owns its checkpoint/diffusion model, VAE, text encoder, LoRA, sampler, audio model, upscaler, node graph, and other concrete ComfyUI settings.

Built-in workflows are organized **task first, then model family**:

```text
comfyui_workflows/
  image/<model>/
  image-edit/<model>/
  video/<model>/
  tts/<model>/
  music/<model>/
  sfx/<model>/
  character-sheet/<model>/
  orbit-sheet/<model>/
  location-orbit/<model>/
  prop-sheet/<model>/
  storyboard/<model>/
  upscale/<model>/
  frame-interpolation/<model>/
  llm/<model>/
  custom/<task>/<model>/
  research/<model>/
```

The JSON files in this directory are the supplied workflows themselves. They are **not sanitized blueprints** and are not rewritten to remove their configured model/resource choices. Open any workflow in ComfyUI, make changes, and save a customized copy if you want a different model stack or graph.

The library contains at least 29 baseline workflow JSON files: 26 production/reference workflows and 3 research sources. Users may add any number of additional Story-Film workflows under `comfyui_workflows/custom/<task>/<model>/`; Story-Film does not impose a catalog maximum.

## Custom Story-Film defaults

To add your own package-level defaults, place workflow JSON files under:

```text
comfyui_workflows/custom/<task>/<model>/
```

Package custom workflows take priority over built-ins when Story-Film constructs a numbered workflow menu.

Story-Film does not discover selectable workflows anywhere else. Project workflow/template directories remain production outputs/staging only, and the connected ComfyUI instance is used for live node/model validation and execution rather than workflow discovery.

Explicit workflow creation is still supported. When a user asks Story-Film to author a new workflow, Story-Film may build and validate it from live ComfyUI schemas; reusable authored JSON should then be placed under `comfyui_workflows/custom/<task>/<model>/` so it becomes a normal catalog choice.

## Research sources

`research/` contains the three source workflows supplied in the replacement workflow archive. They are retained for inspection and provenance but are excluded from normal production workflow menus.
