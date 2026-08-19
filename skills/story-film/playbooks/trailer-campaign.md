# Trailer Campaign

Use for one or more official trailers, teasers, or vertical trailer cutdowns.

1. Run `trailer-plan` from the approved screenplay, film edit intent, selected picture, campaign audience, and verified release facts.
2. Run `trailer-assets` for only the pickups, title cards, VO, music, and SFX the trailer plans actually need.
3. Generate required media through existing model adapters and ComfyUI when requested. Register all candidates with `asset-approval` and run `media-qc` where applicable.
4. Run `trailer-edit` separately for each `TRL-###`.
5. Validate trailer duration, source traceability, aspect, and spoiler policy with `scripts/promo_validate.py`.
6. Run `trailer-master` for actual trailer outputs. The deterministic renderer may batch them through `scripts/render_promos.py --scope trailers`.
7. Run `delivery-qc` and preserve checksums and QC reports.

Done when every requested trailer class exists as a verified master or has an explicit unresolved blocker.
