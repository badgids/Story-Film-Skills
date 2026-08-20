# Story-Film Pi Progress Extension

Optional Pi UI extension for `00_project/pipeline_progress.json`.

It renders the durable Story-Film pipeline ledger above the editor. It does not own pipeline truth and never marks work complete by itself.

Controls:

- `/story-todo status`
- `/story-todo up|down`
- `/story-todo page-up|page-down`
- `/story-todo current`
- `/story-todo help|keys`
- `Ctrl+Alt+End` toggles compact and expanded views
- `Ctrl+Alt+Up/Down` scrolls
- `Ctrl+Alt+PageUp/PageDown` pages
- `Ctrl+Alt+Home` follows the current item

The extension keeps the complete keyboard control set visible in both compact and expanded Todo views. It also listens to Pi's raw terminal-input hook and uses Pi's own key parser when normal extension shortcut dispatch does not receive the chord.

The extension refreshes after tool results and before agent turns, so checkpoints written by `scripts/pipeline_progress.py` appear without maintaining a second state store.

The control hints are split across short lines so scroll, page, and focus-current controls are not lost to terminal-width truncation.
