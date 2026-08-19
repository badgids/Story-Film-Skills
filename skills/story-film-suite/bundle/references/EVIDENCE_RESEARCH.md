# Evidence Research

Evidence-backed projects need stronger bookkeeping than ordinary creative research.

## Claim ledger

Use `01_story/research/claims.jsonl` for factual claims that may affect documentary narration, historical scenes, technical exposition, publicity, press kits, festival packets, captions, or campaign copy.

Each record uses a stable `CLAIM-###` ID.

```json
{"claim_id":"CLAIM-001","statement":"","status":"verified","confidence":"high","sources":[{"source_id":"SRC-001","source_type":"primary","citation":"","url":"","notes":""}],"adopted":false,"adoption_note":"","used_by":[]}
```

Allowed status values:

- `verified`
- `supported`
- `contested`
- `anecdotal`
- `inspiration`
- `project-decision`
- `unresolved`

Confidence values are `high`, `medium`, `low`, or `unknown`.

A `verified` claim must have at least one concrete source record. A public-facing claim should normally resolve to `verified`, `supported`, or `project-decision`. `contested`, `anecdotal`, and `unresolved` material can still inform creative work, but must not be presented publicly as settled fact.

## Research gap workflow

For every research scope:

1. state the exact question;
2. state what the project currently assumes;
3. identify the evidence needed to answer it;
4. record sources and disagreements;
5. add or update claim records;
6. identify gaps that remain;
7. adopt only the claims the project actually chooses to use;
8. connect adopted claims to scenes, narration, documents, or campaign records through `used_by`.

## Source discipline

Prefer original records, official documentation, standards, primary datasets, practitioner material, and scholarship appropriate to the question. Record when a source is secondary, anecdotal, promotional, or interpretive.

A citation is evidence metadata, not permission to copy protected expression. Summarize or quote only within applicable limits.

## Publicity gate

Marketing, press-kit, documentary, and educational claims must not silently inherit weak research. If a public claim lacks sufficient evidence, omit it, qualify it, or keep it unresolved.

Use `scripts/claim_ledger.py` to validate claim structure and public-use readiness.
