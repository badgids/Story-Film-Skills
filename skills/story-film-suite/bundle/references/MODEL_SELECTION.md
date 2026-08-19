# Generation Model Selection

The user owns the generation-model choice.

## Video-model precedence

Use this order for film and video generation:

1. Use an explicit video-model choice from the current user request.
2. Otherwise use an existing user-approved project choice in `00_project/model_preferences.json`.
3. Otherwise use the Story-Film default: `minimax-h3`.

Do not select LTX or another video model only because its feature set appears to fit the shot better.

Do not treat adapter order, installed model files, an example eval, a ComfyUI workflow, or a previous agent preference as user approval.

## Default

The default video-generation adapter is `minimax-h3`.

The default lets an unattended planning workflow continue without forcing a question. It is not permission to replace MiniMax H3 silently.

If MiniMax H3 is unavailable at generation time, report the blocker and the available alternatives. Do not switch to LTX or another model unless the user selects it or explicitly delegates the choice.

## User delegation

The user can explicitly delegate model selection with instructions such as "choose the best video model for this project." In that case the agent may recommend and select a different adapter. Record the source as `delegated`.

## Project record

`00_project/model_preferences.json` records the current video-model choice.

A non-default model must have a selection source of `user`, `user-project`, or `delegated`, and `user_confirmed` must be true.

`allow_agent_substitution` must remain false.

Per-shot overrides are allowed only when they are also user-selected or delegated.

## Runtime availability

Model choice and runtime availability are different facts.

A selected model that is not installed is a blocker. It is not permission to silently substitute another model.
