---
name: guided-production-wizard
description: Build a safe step-by-step human procedure for Story-Film production actions the agent cannot perform itself, with progress, confirmation gates, resumability, and secret-safe handling.
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Guided Production Wizard

Read `../../references/GUIDED_PRODUCTION_WIZARD.md`.

Use for genuinely human-only production steps, not as a substitute for available tools.

Typical uses include:

- selecting and approving a model/license or paid generation route
- entering credentials locally without exposing them to chat
- performing a current third-party web dashboard step
- legal/rights or distribution confirmation
- connecting local storage or capture hardware
- final manual festival/distributor submission

Verify current external instructions before encoding them. Produce a Markdown guide alongside any executable wizard script. Run `bash -n` and `shellcheck` when available, but do not automatically execute a wizard that requires human interaction.
