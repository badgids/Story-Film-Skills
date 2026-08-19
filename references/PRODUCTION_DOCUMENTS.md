# Production Documents

Film projects need professional office and print deliverables in addition to media.

Story-Film Skills can create project-controlled XLSX, DOCX, and PDF documents for production and release work through `scripts/production_documents.py`.

## Common production documents

- shot trackers
- scene breakdown sheets
- production schedules
- call sheets
- contact lists
- budgets and cost trackers
- prop, wardrobe, and continuity trackers
- voice, music, SFX, and cue sheets
- QC and approval logs
- director books
- production reports
- press kits
- festival packets
- campaign calendars
- deliverable matrices

## Manifest

Use `00_project/document_manifest.json` and stable `DOC-###` IDs.

```json
{"schema_version":1,"documents":[{"doc_id":"DOC-001","kind":"shot-tracker","format":"xlsx","title":"Shot Tracker","source_ids":["SHOT-001"],"data_path":"03_preproduction/documents/shot_tracker.json","path":"03_preproduction/documents/shot_tracker.xlsx","status":"planned"}]}
```

All paths remain project-relative.

## XLSX

Use workbooks for structured tracking and calculations. Preserve formulas as formulas. Inputs, formulas, notes, and assumptions should be visually distinguishable when practical. Never replace a requested formula with a hardcoded Python result simply because the current value is known.

## DOCX

Use Word documents for call sheets, production books, reports, press kits, and packets that need editable prose, headings, tables, page numbers, and print-friendly structure.

## PDF

Use PDF for fixed-layout review and delivery. A generated PDF should be rendered or parsed after creation so an unreadable file is not mistaken for a finished document.

## QA

The renderer performs structural checks for every produced document. When LibreOffice or a PDF renderer is available, visual or recalculation checks may be added. Missing optional office runtimes are reported, not hidden.

## Markdown companion

Every XLSX, DOCX, or PDF output must have the same-basename `.md` companion beside it. The Markdown version carries the meaningful human/agent-readable content and is required for sharing, diffing, retrieval, and recovery. `scripts/production_documents.py` writes the companion from the same structured source as the binary document. See `DOCUMENT_COMPANIONS.md`.
