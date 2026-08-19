# Creative Collaboration Protocols

Use collaboration only when independent scrutiny can improve a consequential choice. Do not create extra roles for routine work.

These protocols work in a single-agent harness. If the harness can spawn agents, roles may run separately. If one model performs every role, keep passes isolated in separate files or fresh contexts and do not describe them as independent model opinions.

## Critique-Correct-Verify

Use for an artifact that has a clear creator and review criteria: story scene, screenplay scene, storyboard stage, motion brief, dialogue pass, or continuity repair.

1. **Create**: produce the scoped artifact.
2. **Critique**: identify concrete failures against explicit criteria. Do not rewrite yet.
3. **Correct**: change only what the accepted critique requires.
4. **Verify**: check each critique item against the corrected artifact.
5. Stop on PASS. If still failing, repeat only the unresolved items.

Maximum: 3 correction rounds for one scope. After the third failed verification, stop and record the unresolved decision for the user or producer. Never loop until the reviewer becomes agreeable.

A verification verdict must be one of:

- `PASS`
- `FAIL_FIXABLE`: specific remaining faults exist
- `ESCALATE`: the choice depends on taste, missing facts, user intent, or a conflict the current authority order cannot settle

## Debate-Judge

Use when two materially different approaches could both work and a choice matters enough to compare them. Typical uses: camera strategy, scene order, ending approach, difficult adaptation choice, or competing visual concepts.

1. Write Proposal A from one stated objective.
2. Write Proposal B independently from a different stated objective or method.
3. Compare the proposals only on the decision criteria.
4. Record the strongest case against each proposal.
5. Judge with a short decision that names the winning criteria, retained ideas from the losing proposal, and unresolved risks.

Do not manufacture disagreement. If both proposals converge, record convergence and stop.

Maximum: 2 comparison rounds before judgment.

## Evidence hierarchy

A critic or judge may not overrule:

1. the current explicit user instruction
2. canon and locked facts
3. approved upstream artifacts
4. verified production constraints

Creative debate happens inside those boundaries.

## Review record

For work that must survive context loss, store review material under:

```text
00_project/reviews/<scope-id>/
  brief.md
  round-01-proposal.md
  round-01-critique.md
  round-01-correction.md
  round-01-verdict.json
  decision.md
```

Create only the files the chosen protocol needs. Each verdict records scope ID, round, criteria, disposition, unresolved items, and affected artifact paths.

## Escalation rule

Escalation is a successful outcome when the system has reached a real choice it cannot settle from existing authority. State exactly what decision is needed. Do not hide the uncertainty by picking the easiest option.
