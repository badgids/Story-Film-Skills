# Story-Film Pi Progress Extension

Optional Pi UI extension for `00_project/pipeline_progress.json`.

It renders the durable Story-Film pipeline ledger above the editor. It does not own pipeline truth and never marks work complete by itself.

Controls:

- `/story-todo status`
- `/story-todo up|down`
- `/story-todo page-up|page-down`
- `/story-todo current`
- `Ctrl+Alt+Shift+Up/Down`
- `Ctrl+Alt+PageUp/PageDown`
- `Ctrl+Alt+Shift+Home`

The extension refreshes after tool results and before agent turns, so checkpoints written by `scripts/pipeline_progress.py` appear without maintaining a second state store.
