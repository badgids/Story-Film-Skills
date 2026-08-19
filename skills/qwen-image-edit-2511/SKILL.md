---
name: qwen-image-edit-2511
description: Adapt controlled image-edit or multi-image composition tasks into Qwen Image Edit 2511 instructions that name source image roles, exact changes, preservation constraints, and exact text edits.
disable-model-invocation: true
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Qwen Image Edit 2511 Prompting

## Workflow

1. Read the edit brief, canon, and source-image role descriptions.
2. State the edit operation first with an explicit verb: add, remove, replace, move, recolor, relight, restyle, rotate, extend, or combine.
3. Name image roles as `Image 1`, `Image 2`, and so on when multiple images are supplied.
4. State what must remain unchanged immediately after the requested change.
5. For replacements, use a direct form such as `Replace <source> with <target>` and describe the target only as needed.
6. For text edits, quote exact old and new text. Keep supplied language and capitalization.
7. For identity-sensitive edits, explicitly preserve core person or character identity except for the named attribute being changed.
8. Resolve contradictory instructions before producing the final prompt.
9. Keep the final instruction compact, usually below about 200 words.
10. Save under `04_generation/prompts/qwen-image-edit-2511/<source-id>.md`.

## Done

The operator can tell exactly which input image contributes each retained or changed element, and the prompt names no unrequested visual change.
