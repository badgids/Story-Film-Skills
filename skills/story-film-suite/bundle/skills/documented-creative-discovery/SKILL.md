---
name: documented-creative-discovery
description: Run a decision-tree creative interview while maintaining durable Story-Film decisions, terminology, canon implications, evidence links, and open questions as the discussion progresses.
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Documented Creative Discovery

Use `decision-tree-interview`, then persist the useful result rather than leaving it only in chat.

Maintain:

- `00_project/creative_decisions.jsonl` for `DEC-###` decisions
- `00_project/production_glossary.md` for project-specific production/story terms that an agent could misinterpret
- existing canon/story-state artifacts for facts that become canon or mutable narrative state
- `00_project/creative_production_spec.md` for durable project production conventions that are not story canon
- `SRC-###` and `CLAIM-###` when a decision depends on factual evidence
- `00_project/decision_map.*` when the effort is too large for one session

Do not duplicate entire bibles, specs, or research files. Link to the authoritative artifact and record only the decision, its concise rationale, and its consequences.

A decision record must never contain private chain-of-thought.
