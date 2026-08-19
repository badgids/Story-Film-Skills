# Creative Decision Protocol

Use this protocol when a story, book, image, audio, video, film, trailer, or campaign decision needs explicit human judgment instead of an agent guess.

## Decision tree

A decision is a node whose answer may unlock later decisions. Store only decision-relevant state, never private chain-of-thought.

Each decision record may contain:

- stable `DEC-###` ID
- question
- why the decision matters
- prerequisites
- options
- recommended option and concise rationale
- user decision
- status: `open`, `decided`, `deferred`, or `out-of-scope`
- affected artifact IDs
- source/evidence IDs when factual claims matter

## Frontier interview

Ask only questions whose prerequisites are already settled. Ask the complete current frontier in one round when practical. Number the questions and include a recommended answer so the user can accept, reject, or modify it quickly.

Do not ask the user for facts the agent can retrieve from project files, connected sources, the live runtime, or public research. Facts are agent work. Creative and production choices belong to the user unless already established by canon or project constraints.

## Completion

The interview is complete when no in-scope open decision remains whose prerequisites are satisfied. A deferred decision must say what future fact or choice is required before it can reopen.

## Persistence

For a durable session write decisions to `00_project/creative_decisions.jsonl`. For large uncertain efforts also maintain `00_project/decision_map.json` and `00_project/decision_map.md`.
