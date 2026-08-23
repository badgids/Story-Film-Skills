# Contributing to Story-Film Skills

Copyright 2026 Alan Guice (Badgids). Licensed under Apache-2.0.

Thank you for improving Story-Film Skills.

## Before you change code

1. Read [docs/development/contributing.md](docs/development/contributing.md).
2. Read the related skill and reference contract.
3. Identify the durable source of truth that the change affects.
4. Add or update deterministic tests for observable behavior.
5. Add a local-model smoke case when the change affects agent judgment or routing.

## Project rules

- Do not hardcode personal machine paths.
- Do not use the em dash character U+2014 in repository text outside ComfyUI workflow JSON. Workflow JSON is exempt so imported, vendor, user-authored, and embedded workflow text can be preserved exactly.
- Keep the project local-first.
- Do not claim that an optional runtime ran when it was unavailable.
- Preserve stable IDs and schemas unless a documented migration is provided.
- Every generated PDF, DOCX, XLSX, PPTX, ODT, ODS, ODP, and related rich document must have a meaningful same-basename Markdown companion.
- Preserve Apache-2.0 license and NOTICE obligations.

## Test before a pull request

```bash
python scripts/regression_suite.py
python scripts/check_docs.py
python scripts/build_npx_bundle.py --check
```

Run relevant local smoke cases after v0.0.11 when the change affects model behavior.

## Documentation

Use the rules in [docs/reference/documentation-style.md](docs/reference/documentation-style.md).

Keep navigation links valid. Explain the simple idea before technical detail.
