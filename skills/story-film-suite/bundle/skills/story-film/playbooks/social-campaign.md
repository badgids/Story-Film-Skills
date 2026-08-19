# Social Campaign

Use for coordinated social release assets, not an isolated one-off caption.

1. Run `social-campaign`: define `CAMP-###`, verified release facts, audience segments, platforms, placements, content pillars, spoiler rules, accessibility, and the `SOC-###` deliverable matrix.
2. Run `social-copy` for required captions, hooks, CTAs, accessibility descriptions, hashtags, and keywords.
3. Run `marketing-art` for key art, posters, thumbnails, banners, title cards, and campaign stills.
4. Run `social-cutdown` for each video deliverable. Reuse approved film/trailer media where it fits the job.
5. Run `social-reframe` only when destination composition differs and a safe deterministic reframe is possible. Prefer destination-native pickups when cropping would damage the shot.
6. Generate any required social pickups, music, or SFX through existing adapters and route them through `asset-approval`.
7. Run `campaign-delivery`. Use `scripts/render_promos.py --scope social` for deterministic video masters when actual rendering is requested.
8. Run delivery QC for all final media and reconcile the campaign calendar, copy, artwork, subtitles, and output paths.

Done when every required `SOC-###` is ready or explicitly blocked, and marketing copy contains no invented release claims.

9. Run `campaign-brand` when a reusable campaign voice is needed, then validate public factual claims through `evidence-research`.
10. Run `content-repurpose` for cross-platform adaptations and preserve `CONTENT-###` lineage from source media/copy to each destination.
11. Run `design-system` before producing a family of coordinated posters, thumbnails, title cards, social stills, or motion graphics.

