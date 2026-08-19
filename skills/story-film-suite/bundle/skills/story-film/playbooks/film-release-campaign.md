# Film Release Campaign

Use when the requested endpoint is a finished film plus trailers and a social-media campaign.

1. If the film has not been created yet, run the appropriate story and screenplay playbooks, then `screenplay-to-film-package` and actual generation.
2. Run `film-finishing` until the verified main film master exists.
3. Run `trailer-campaign` for the requested official trailer, teaser, vertical cutdowns, or other trailer classes.
4. Run `social-campaign` for the requested platform and placement matrix.
5. Run `release-package` to reconcile the film master, audio master, subtitles, trailers, artwork, social masters, copy, campaign metadata, QC reports, and checksums.
6. Run project, standalone, style, and release validators.

Done when the requested release package contains actual verified master media plus the portable source manifests needed to rebuild the film, trailers, and campaign.

7. When the release includes press, festival, sponsor, production, or archival documents, run `production-documents` and include approved `DOC-###` outputs in the release package.
8. Use `evidence-research` for any factual public claims in press kits, filmmaker notes, historical context, or campaign material.

