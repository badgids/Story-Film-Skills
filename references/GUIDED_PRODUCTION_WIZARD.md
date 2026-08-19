# Guided Production Wizard

A production wizard is for manual steps only a human must perform, such as granting access, choosing a license, confirming a legal/rights decision, completing a third-party dashboard action, connecting removable media, approving a paid service, or performing an irreversible external submission.

The agent should do everything it can do itself before creating a wizard.

A repeatable wizard should:

- show stage N of total stages
- keep one focused human action on screen at a time
- explain exactly where to go and what to do
- never invent current third-party UI labels without verification
- hide secret input
- avoid echoing secrets into logs
- confirm before irreversible actions
- be resumable/idempotent where practical
- record only non-secret completion state
- end with a concise summary and the exact next Story-Film action

Prefer Markdown instructions when no executable automation is needed. Use a shell wizard only when deterministic local checks, file writes, or command execution materially improve the procedure.
