# Media Lifecycle Safety

Rejecting a candidate changes approval state. Physical deletion is a separate explicit operation.

Story-Film may delete a registered rejected/superseded media file only when all of these are true:

- the exact `MEDIA-###` record exists;
- its status is `rejected`, `superseded`, or `retired`;
- it is not the primary media for its approval group;
- its path is project-relative and resolves inside the project root;
- no other active media record points at the same path;
- the caller explicitly requested deletion.

Deletion writes a durable cleanup ledger. Directory sweeps, prefix globs, traversal outside the project, and deletion of unregistered files are forbidden.

If an approved project copy exists but a disposable Comfy/runtime copy has disappeared, Story-Film may repair that runtime copy from the approved source after verifying source identity and destination safety. Repair is never regeneration.
