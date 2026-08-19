---
name: production-documents
description: Create and validate professional film-production and release documents in XLSX, DOCX, and PDF formats, including trackers, call sheets, schedules, budgets, cue sheets, director books, press kits, festival packets, and campaign calendars.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Production Documents

1. Read `../../references/PRODUCTION_DOCUMENTS.md` and the authoritative project artifacts for the requested document.
2. Add a `DOC-###` record to `00_project/document_manifest.json`.
3. Use project-relative source and output paths.
4. Use XLSX for structured tracking/calculation, DOCX for editable prose/tables, and PDF for fixed delivery/review.
5. Keep formulas as formulas and label assumptions.
6. Create documents with `scripts/production_documents.py`; it must also create the same-basename Markdown companion beside every XLSX, DOCX, or PDF output.
7. Read `../../references/DOCUMENT_COMPANIONS.md` and run `scripts/document_companions.py audit` before delivery. Run structural QC and, where available, recalc or visual preview checks.
8. Add public-facing documents to the release manifest when requested.

Done when the rich document and its human-readable Markdown companion both exist, the document opens structurally, and both are traceable to the same project sources.
