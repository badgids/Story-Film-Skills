# Human-Readable Document Companions

Every Story-Film rich/binary document artifact must have a Markdown companion beside it so humans and agents can read, diff, search, share, and archive its meaningful content without a specialized application.

Companion-required extensions include:

- `.pdf`
- `.docx`, `.dotx`
- `.xlsx`, `.xlsm`, `.xltx`
- `.pptx`, `.pptm`
- `.odt`, `.ods`, `.odp`

The default companion path is the same directory and basename with `.md` substituted for the document extension.

Examples:

- `call_sheet.pdf` -> `call_sheet.md`
- `budget.xlsx` -> `budget.md`
- `director_book.docx` -> `director_book.md`

## Equivalence rule

The Markdown file must communicate the meaningful text, tabular data, labels, assumptions, source references, and structure required to understand the artifact. For a highly visual artifact it must also describe the visual organization and preserve exact displayed text where practical.

A one-line statement saying only that a binary file exists is not an equivalent.

## Source of truth

When both files are generated from the same structured source, that source is authoritative. If an existing binary document is imported, `scripts/document_companions.py` can extract a best-effort Markdown representation. Review extraction when layout or visual meaning is important.
