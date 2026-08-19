#!/usr/bin/env bash
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_ROOT="${PI_SKILLS_DIR:-$HOME/.pi/agent/skills}"
EXTENSIONS_ROOT="${PI_EXTENSIONS_DIR:-$HOME/.pi/agent/extensions}"
DEST="$SKILLS_ROOT/story-film-skills"
EXT_DEST="$EXTENSIONS_ROOT/story-film-progress.ts"
SKILLS_ONLY=0

usage() {
  cat <<'TXT'
Usage: bash install.sh [--skills-only]

Fallback installer for Story-Film Skills. Prefer native `pi install` when Pi package management is available.
This script copies Story-Film Skills into configured Pi directories and also installs the optional Todo/resource-status extension by default.

Environment variables:
  PI_SKILLS_DIR      Override the Pi skills directory.
  PI_EXTENSIONS_DIR  Override the Pi extensions directory.
TXT
}

for arg in "$@"; do
  case "$arg" in
    --skills-only) SKILLS_ONLY=1 ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$arg" >&2; usage >&2; exit 2 ;;
  esac
done

mkdir -p "$SKILLS_ROOT"
rm -rf "$DEST"
cp -a "$SRC" "$DEST"

# Remove known legacy product install paths to prevent duplicate discovery.
rm -rf "$SKILLS_ROOT/badgids-story-film-skills"

if [[ "$SKILLS_ONLY" -eq 0 ]]; then
  mkdir -p "$EXTENSIONS_ROOT"
  cp "$SRC/extensions/story-film-progress/index.ts" "$EXT_DEST"
  rm -f "$EXTENSIONS_ROOT/badgids-story-film-progress.ts"
fi

DISPLAY_VERSION="$(python3 "$SRC/scripts/version_display.py")"
CANONICAL_VERSION="$(cat "$SRC/VERSION")"
printf 'Installed Story-Film Skills %s (canonical %s) to %s\n' "$DISPLAY_VERSION" "$CANONICAL_VERSION" "$DEST"
if [[ "$SKILLS_ONLY" -eq 0 ]]; then
  printf 'Installed optional Pi pipeline Todo/resource extension to %s\n' "$EXT_DEST"
fi
printf 'Restart Pi or start a new Pi session, then use /skill:story-film\n'
printf 'Read docs/README.md for the complete manual.\n'
