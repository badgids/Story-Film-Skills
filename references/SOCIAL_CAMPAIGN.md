# Social Campaign

The social campaign system turns approved film and trailer material into a coordinated set of platform-ready videos, stills, copy, captions, thumbnails, key art, and delivery records.

## Project layout

```text
06_release/social/
  campaign.json
  deliverables.jsonl
  copy.jsonl
  delivery_report.json
  calendar.csv
  art_briefs.jsonl
  masters/
  qc/
```

## Campaign brief

`06_release/social/campaign.json` should include:

- `campaign_id` as `CAMP-###`
- objective
- audience segments
- verified release facts
- content pillars
- calls to action
- spoiler policy
- tone and voice
- platforms and placements
- required aspect ratios
- accessibility requirements
- forbidden claims

If a release date, URL, rating, award, review quote, cast credit, or availability claim is unknown, leave it unresolved. Never invent marketing facts.

## Deliverable record

```json
{
  "schema_version": 1,
  "social_id": "SOC-001",
  "platform": "instagram",
  "placement": "reel",
  "media_type": "video",
  "aspect_ratio": "9:16",
  "width": 1080,
  "height": 1920,
  "target_duration": 15.0,
  "duration_tolerance": 1.0,
  "source_ids": ["TRL-002"],
  "timeline_path": "06_release/social/SOC-001/timeline.json",
  "output_path": "06_release/social/masters/SOC-001.mp4",
  "copy_id": "COPY-001",
  "status": "planned"
}
```

## Supported aspect classes

The default portable profiles are:

- `16:9`: 1920x1080
- `9:16`: 1080x1920
- `1:1`: 1080x1080
- `4:5`: 1080x1350

Platform requirements change. Treat these as project defaults, not permanent platform law.

## Reframing

For landscape-to-vertical or square conversion:

1. prefer a source composed for the destination ratio;
2. otherwise use an approved focus point or region;
3. preserve faces, speaking characters, required props, and critical action;
4. use fit-with-padding when a fill crop would destroy required information;
5. never hide a continuity failure with an arbitrary crop.

## Copy

Each copy record should separate:

- hook
- body
- CTA
- caption accessibility text when needed
- hashtags/keywords
- verified facts used
- unresolved facts intentionally omitted

## Calendar

If exact release dates are unknown, use relative phases such as `T-14`, `T-7`, `T-1`, `Launch`, `T+1`, and `T+7` instead of inventing calendar dates.

## Delivery reconciliation

Run `scripts/promo_delivery.py PROJECT --scope social --reconcile` after social rendering, artwork production, copy approval, and QC. A required media deliverable is `ready` only when its output exists, its `SOC-###` approval group resolves to that output, media QC is non-blocking, required video QC exists, and any referenced `COPY-###` record resolves. Optional omissions become `optional-missing` rather than silently blocking the campaign.

The reconciliation report is written to `06_release/social/delivery_report.json`.
