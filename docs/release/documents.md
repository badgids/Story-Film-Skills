# Production Documents and Markdown Companions

[Documentation home](../README.md) | [Up: Release](campaign.md) | [Next: Licensing](../reference/licensing.md)

## Table of contents

- [Rich documents](#rich-documents)
- [Markdown companion rule](#markdown-companion-rule)
- [Examples](#examples)
- [Validation](#validation)

## Rich documents

Story-Film Skills can create production documents such as budgets, call sheets, cue sheets, trackers, director books, reports, press kits, and festival packets.

## Markdown companion rule

Every generated rich document must have a meaningful Markdown file with the same basename.

This rule applies to:

- PDF;
- DOCX and DOTX;
- XLSX, XLSM, and XLTX;
- PPTX and PPTM;
- ODT, ODS, and ODP.

The Markdown copy is for people, agents, source control, web sharing, and long-term readability.

## Examples

```text
budget.xlsx
budget.md

call_sheet.pdf
call_sheet.md

press_kit.docx
press_kit.md
```

The Markdown file must contain the useful content. A file that only says "See budget.xlsx" is not sufficient.

## Validation

Run:

```bash
python scripts/document_companions.py PROJECT audit
```

The project validator also checks this rule.

## Related pages

- [Final completeness](completion.md)
- [Document companion contract](../../references/DOCUMENT_COMPANIONS.md)
- [Production documents skill](../../skills/production-documents/SKILL.md)
