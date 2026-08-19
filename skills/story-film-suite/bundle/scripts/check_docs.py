# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Check Story-Film Skills Markdown navigation and controlled-documentation basics."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LINK_RX = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def target_exists(page: Path, target: str) -> bool:
    if target.startswith(("http://", "https://", "mailto:")):
        return True
    path_part = target.split("#", 1)[0]
    if not path_part:
        return True
    dest = (page.parent / path_part).resolve()
    try:
        dest.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return dest.exists()


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    pages = sorted(DOCS.rglob("*.md"))
    if not pages:
        errors.append("docs: no Markdown pages found")
    for page in pages:
        rel = page.relative_to(ROOT)
        text = page.read_text(encoding="utf-8")
        if chr(0x2014) in text:
            errors.append(f"{rel}: contains forbidden em dash U+2014")
        if page != DOCS / "README.md":
            first = "\n".join(text.splitlines()[:8])
            if "Documentation home" not in first:
                errors.append(f"{rel}: top navigation must link to Documentation home")
            if "## Table of contents" not in text:
                errors.append(f"{rel}: missing Table of contents")
            if "## Related pages" not in text:
                errors.append(f"{rel}: missing Related pages")
        for target in LINK_RX.findall(text):
            if not target_exists(page, target):
                errors.append(f"{rel}: broken relative link {target}")
        # Controlled-English heuristic. It is a warning, not a certification gate.
        for lineno, line in enumerate(text.splitlines(), 1):
            if line.startswith(("```", "|", "    ")) or not line.strip() or line.lstrip().startswith(('#','-','*','>')):
                continue
            words = re.findall(r"\b[\w'-]+\b", line)
            if len(words) > 42:
                warnings.append(f"{rel}:{lineno}: long prose line ({len(words)} words)")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    required_top = [
        "# Story-Film Skills",
        "**Author/Developer:** Alan Guice (Badgids)",
        "**License:** Apache License 2.0",
        "*Copyright © 2026 Alan Guice (Badgids).*",
    ]
    positions = [readme.find(x) for x in required_top]
    if any(x < 0 for x in positions) or positions != sorted(positions):
        errors.append("README.md: required title/author/license/copyright header is missing or out of order")
    if "## Table of contents" not in readme:
        errors.append("README.md: missing Table of contents")
    if "docs/README.md" not in readme:
        errors.append("README.md: documentation home is not linked")

    for warning in warnings[:50]:
        print("WARN", warning)
    if len(warnings) > 50:
        print(f"WARN documentation: {len(warnings)-50} additional long-line warnings")
    if errors:
        for error in errors:
            print("ERROR", error)
        return 1
    print(f"OK documentation: {len(pages)} linked pages, {len(warnings)} readability warnings")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
