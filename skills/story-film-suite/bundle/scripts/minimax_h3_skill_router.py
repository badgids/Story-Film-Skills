#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BASE_SKILL = "h3-prompt-writing"

STYLE_RULES = (
    {
        "skill": "minimalist-product-ad-generator",
        "priority": 80,
        "phrases": (
            "minimalist product ad",
            "minimalist product film",
            "premium product ad",
            "product ad",
            "product launch",
            "e-commerce",
            "ecommerce",
            "apple-style product",
            "apple style product",
        ),
    },
    {
        "skill": "3d-animation-short-generator",
        "priority": 70,
        "phrases": (
            "3d animation short",
            "3d animated short",
            "stylized 3d animation",
            "stylized 3d short",
            "3d cartoon short",
            "pixar-inspired",
            "pixar inspired",
        ),
    },
    {
        "skill": "papercraft-stop-motion-explainer",
        "priority": 75,
        "phrases": (
            "papercraft stop-motion",
            "papercraft stop motion",
            "paper craft stop-motion",
            "paper craft stop motion",
            "pop-up-book explainer",
            "pop up book explainer",
            "paper diorama explainer",
            "cut-paper explainer",
            "cut paper explainer",
        ),
    },
    {
        "skill": "brand-promo-video-generator",
        "priority": 60,
        "phrases": (
            "brand promo",
            "brand promotional",
            "brand reel",
            "website promo",
            "app promo",
            "shop promo",
            "campaign promo",
            "brand launch video",
        ),
    },
    {
        "skill": "music-video-subtitle-generator",
        "priority": 90,
        "phrases": (
            "music video",
            "lyric typography",
            "lyric video",
            "subtitle mv",
            "lyrics mv",
            "beat-synced typography",
            "beat synced typography",
            "music aesthetics mv",
        ),
    },
    {
        "skill": "co-op-game-intro-generator",
        "priority": 95,
        "phrases": (
            "co-op game intro",
            "coop game intro",
            "co op game intro",
            "two-player game intro",
            "two player game intro",
            "co-op game menu",
            "coop game menu",
            "player 1 and player 2",
        ),
    },
    {
        "skill": "paper-collage-explainer-generator",
        "priority": 85,
        "phrases": (
            "paper collage explainer",
            "paper-collage explainer",
            "halftone paper collage",
            "collage explainer",
            "tactile paper collage",
        ),
    },
    {
        "skill": "handdrawn-live-video-generator",
        "priority": 100,
        "phrases": (
            "handdrawn live video",
            "hand-drawn live video",
            "hand drawn live video",
            "live-action hand-drawn",
            "live action hand drawn",
            "hand-drawn animation interacting with live action",
            "hand drawn animation interacting with live action",
            "rough glowing hand-drawn",
        ),
    },
)

STYLE_SKILLS = tuple(rule["skill"] for rule in STYLE_RULES)


def normalize(value: str) -> str:
    value = value.casefold().replace("_", " ")
    return re.sub(r"\s+", " ", value).strip()


def route(text: str, explicit_style_skill: str = "") -> dict:
    explicit = explicit_style_skill.strip()
    if explicit:
        if explicit not in STYLE_SKILLS:
            raise ValueError(
                f"unknown MiniMax H3 style skill {explicit!r}; "
                f"expected one of: {', '.join(STYLE_SKILLS)}"
            )
        return {
            "base_skill": BASE_SKILL,
            "style_skill": explicit,
            "reason": "explicit-style-skill",
            "candidates": [{"skill": explicit, "score": 1000, "hits": ["explicit"]}],
        }

    haystack = normalize(text)
    scored = []
    for rule in STYLE_RULES:
        hits = [phrase for phrase in rule["phrases"] if normalize(phrase) in haystack]
        if not hits:
            continue
        score = rule["priority"] + sum(len(normalize(p).split()) for p in hits)
        scored.append({"skill": rule["skill"], "score": score, "hits": hits})

    scored.sort(key=lambda row: (-row["score"], row["skill"]))
    return {
        "base_skill": BASE_SKILL,
        "style_skill": scored[0]["skill"] if scored else None,
        "reason": "matched-brief" if scored else "generic-h3",
        "candidates": scored,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Select the mandatory H3 prompt-writing skill and an optional Story-Film H3 style overlay."
    )
    ap.add_argument("--text", default="", help="Brief text to classify.")
    ap.add_argument("--brief", help="Optional UTF-8 brief file to classify.")
    ap.add_argument("--style-skill", default="", help="Explicit style skill override.")
    args = ap.parse_args()

    text = args.text
    if args.brief:
        text = Path(args.brief).read_text(encoding="utf-8")
    print(json.dumps(route(text, args.style_skill), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
