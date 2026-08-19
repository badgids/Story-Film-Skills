---
name: production-diagrams
description: Create standalone film-production diagrams and semantic diagram records for character relationships, timelines, scene geography, blocking, eyelines, shot flow, reference inheritance, and artifact dependencies.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Production Diagrams

## Workflow

1. Read the standalone contract, core contract, production diagram rules, canon, and only the artifacts needed for the requested question.
2. State the one question the diagram must answer.
3. Choose one diagram type and keep within the complexity budget.
4. Use stable project IDs for every entity that has one.
5. Write `<name>.json` under `03_preproduction/diagrams/` with nodes, relationships, focal items, uncertainty, and source artifact IDs.
6. Write `<name>.md` beside it.
7. Use Mermaid for relationships, timelines, sequence flow, and dependencies when it communicates the structure accurately.
8. Use labeled coordinates, zones, or textual maps for geography and blocking when auto-layout would imply false spatial relationships.
9. Remove elements that do not help answer the stated question.

## Done

The package itself contains a readable production diagram and machine-readable semantic record that resolve the requested structural question without depending on another diagram skill.
