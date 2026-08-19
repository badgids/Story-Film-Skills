# Choose the Video Generation Model

[Documentation home](../README.md) | [Up: ComfyUI generation](comfyui.md) | [Next: Resource-safe generation](resource-safe.md)

## Table of contents

- [Who chooses](#who-chooses)
- [Default model](#default-model)
- [Change the model](#change-the-model)
- [If the model is missing](#if-the-model-is-missing)

## Who chooses

You choose the video generation model.

Story-Film Skills must not silently change the model because another model looks better for one shot.

## Default model

If you do not choose a video model, Story-Film Skills uses **MiniMax H3**.

The adapter name is:

```text
minimax-h3
```

LTX 2.5 remains available, but it is not the default.

## Change the model

You can tell Pi in normal language:

```text
Use LTX 2.5 for video generation in this project.
```

Or record the choice with the helper:

```bash
python scripts/model_preferences.py set-video . ltx-2-5 --source user
```

Show the current choice:

```bash
python scripts/model_preferences.py show .
```

Return to the MiniMax H3 default:

```bash
python scripts/model_preferences.py reset-video .
```

## If the model is missing

Story-Film Skills must stop and tell you that the selected model is unavailable.

It may show alternatives.

It must not silently replace MiniMax H3 with LTX or another model.

## Related pages

- [ComfyUI generation](comfyui.md)
- [Resource-safe local generation](resource-safe.md)
- [RAM and VRAM generation budgets](memory-budget.md)
