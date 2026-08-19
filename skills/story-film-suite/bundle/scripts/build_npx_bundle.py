# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
"""Build the self-contained Story-Film Skills bundle used by `npx skills`."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "story-film-suite"
BUNDLE = SKILL_DIR / "bundle"

COPY_DIRS = ("scripts", "references", "docs", "examples", "extensions", "evals", "tests")
COPY_FILES = (
    "VERSION", "LICENSE", "NOTICE", "AUTHORS.md", "ATTRIBUTION.md", "README.md",
    "CHANGELOG.md", "SOURCES.md", "REVIEW_NOTES.md", "install.sh",
)

SKILL_MD = """---
name: story-film-suite
description: Self-contained Story-Film Skills bundle for story, book, screenplay, image, audio, video, film, postproduction, and release work. Use this entry point when Story-Film Skills was installed with npx skills.
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Story-Film Skills Suite

This is the self-contained installation entry point.

1. Read `bundle/skills/story-film/SKILL.md` as the main router.
2. When that router names another Story-Film skill, read it from `bundle/skills/<skill-name>/SKILL.md`.
3. Run shared tools from `bundle/scripts/`.
4. Read shared contracts from `bundle/references/`.
5. Use `bundle/docs/README.md` for the user manual.
6. Do not assume that any files exist outside this skill directory.

For Pi's optional interactive Todo extension, install `bundle/extensions/story-film-progress/index.ts` into the Pi extensions directory, or use the Git clone installer instead.
"""


def copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
    )


def build() -> Path:
    SKILL_DIR.mkdir(parents=True, exist_ok=True)
    (SKILL_DIR / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")
    if BUNDLE.exists():
        shutil.rmtree(BUNDLE)
    BUNDLE.mkdir(parents=True)

    # Copy all discoverable specialist skills except this bundle to avoid recursion.
    skills_dst = BUNDLE / "skills"
    skills_dst.mkdir()
    for child in sorted((ROOT / "skills").iterdir()):
        if not child.is_dir() or child.name == "story-film-suite":
            continue
        copy_tree(child, skills_dst / child.name)

    for name in COPY_DIRS:
        copy_tree(ROOT / name, BUNDLE / name)
    for name in COPY_FILES:
        src = ROOT / name
        if src.is_file():
            shutil.copy2(src, BUNDLE / name)
    return BUNDLE


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the self-contained npx skills bundle.")
    ap.add_argument("--check", action="store_true", help="Fail if the bundle is missing required files after build.")
    args = ap.parse_args()
    path = build()
    required = [
        path / "skills/story-film/SKILL.md",
        path / "scripts/init_story_project.py",
        path / "references/CORE_CONTRACT.md",
        path / "docs/README.md",
        path / "LICENSE",
        path / "NOTICE",
    ]
    missing = [str(p.relative_to(path)) for p in required if not p.is_file()]
    if args.check and missing:
        raise SystemExit("bundle missing: " + ", ".join(missing))
    print(path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
