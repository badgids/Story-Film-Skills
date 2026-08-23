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
  custom/<task>/<model>/
  research/<model>/
```

The JSON files in this directory are the supplied workflows themselves. They are **not sanitized blueprints** and are not rewritten to remove their configured model/resource choices. Open any workflow in ComfyUI, make changes, and save a customized copy if you want a different model stack or graph.

## Custom Story-Film defaults

To add your own package-level defaults, place workflow JSON files under:

```text
comfyui_workflows/custom/<task>/<model>/
```

For a single Story-Film project, place custom defaults under:

```text
04_generation/comfyui/default_workflows/<task>/<model>/
```

Project defaults take priority over package custom defaults, which take priority over built-ins when Story-Film constructs a numbered workflow menu.

Story-Film can also discover workflows saved in the connected ComfyUI instance, ComfyUI core/custom-node templates, registered external workflow files/directories, and project workflows/templates.

## Research sources

`research/` contains the three source workflows supplied in the replacement workflow archive. They are retained for inspection and provenance but are excluded from normal production workflow menus.
