# Media Registry and Approval

The media registry gives every generated or imported production file a durable identity and one approval state. It applies to reference images, voice candidates, dialogue takes, music, SFX, video takes, audio masters, film masters, trailer assets, social assets, key art, subtitles, and release files.

## Files

- `00_project/media_registry.jsonl`: append-friendly media records.
- `00_project/media_approvals.json`: current primary and alternate selections by approval group.

## Stable IDs

Use `MEDIA-###` for a concrete media file candidate. Preserve existing domain IDs such as `TAKE-###`, `VOICE-###`, `MUS-###`, `SFX-###`, `REF-###`, `TRL-###`, and `SOC-###` as source or group identities.

A media record does not replace a shot take record. It makes approval behavior consistent across media classes.

## Media record

```json
{
  "schema_version": 1,
  "media_id": "MEDIA-001",
  "kind": "video",
  "group_id": "SHOT-001",
  "source_ids": ["TAKE-001", "SHOT-001"],
  "path": "04_generation/comfyui/outputs/shot-001-v01.mp4",
  "status": "candidate",
  "qc_status": "not-checked",
  "created_by": "comfyui",
  "metadata": {}
}
```

Allowed statuses:

- `candidate`
- `primary`
- `alternate`
- `rejected`
- `superseded`
- `retired`

Allowed QC statuses:

- `pass`
- `warn`
- `fail`
- `not-checked`
- `not-applicable`

## Approval groups

`group_id` is the decision scope. Examples:

- `SHOT-014` for generated video alternatives
- `VOICE-003` for voice-design alternatives
- `MUS-005` for score alternatives
- `SFX-011` for effect alternatives
- `MASTER-001` for audio-master alternatives
- `TRL-001` for trailer-master alternatives
- `SOC-014` for one social deliverable

Exactly one primary is allowed per group. Any number of alternates may be retained.

## Selection rules

1. Never delete useful rejected candidates merely to simplify state.
2. A primary replacement demotes the old primary to `alternate` unless it has been explicitly rejected or superseded.
3. A QC-failed candidate cannot become primary unless the approval record contains `qc_override: true` and a concrete reason approved by the user.
4. A path must remain project-relative.
5. A new render receives a new `MEDIA-###` ID even when it targets the same group.
6. Changing a primary does not silently rewrite upstream creative artifacts. Run project impact from the affected group or source ID.

## Approval record

```json
{
  "schema_version": 1,
  "groups": {
    "SHOT-001": {
      "primary_media_id": "MEDIA-001",
      "alternate_media_ids": ["MEDIA-002"],
      "reason": "Best performance and clean continuity",
      "qc_override": false
    }
  }
}
```

## Resumability

The registry is durable production state. An agent resuming later should inspect it before generating replacements. Existing approved media should be preserved unless its dependency scope is stale or the user requests a new option.
