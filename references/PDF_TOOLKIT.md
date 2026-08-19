# PDF Toolkit

PDF work appears throughout film production: scripts, director books, storyboards, contracts supplied as references, press kits, festival packets, cue sheets, and print proofs.

`scripts/pdf_toolkit.py` provides a standalone PDF layer using permissive Python/Poppler tools where available and an optional MuPDF `mutool` adapter when it is installed.

## Portable operations

- metadata and page inspection
- text extraction
- page rendering for visual review
- merge
- split
- rotate
- image extraction when a suitable runtime is present
- PDF rewrite/repair when `mutool clean` is present
- text search

## MuPDF boundary

MuPDF is not bundled. Its upstream project is AGPL with commercial licensing options. `mutool` is treated as an optional external runtime and must not become a hidden required dependency of Story-Film Skills.

If `mutool` is missing, use another supported local route when the operation is safely equivalent. If no equivalent exists, report the missing capability.

## Security

Imported PDFs are untrusted input. Do not execute embedded JavaScript, attachments, or external actions. Prefer parsing, rendering, or rewriting tools that do not execute document actions.
