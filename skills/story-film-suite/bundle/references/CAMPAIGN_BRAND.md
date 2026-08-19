# Campaign Brand and Content Lineage

A campaign needs durable voice rules and traceable repurposing, not a fresh tone guess for every post.

## Brand voice

Use `06_release/social/brand_voice.json`.

Recommended fields:

- `schema_version`
- project or campaign name
- audience segments
- 3 to 5 voice attributes
- perspective and formality
- vocabulary to prefer
- vocabulary to avoid
- title and character naming rules
- CTA style
- humor rules
- spoiler rules
- prohibited claims
- accessibility tone
- approved examples
- source sample references

The voice profile describes the project. It must not overwrite character dialogue style or story canon.

## Content lineage

Use `06_release/social/content_lineage.jsonl` with stable `CONTENT-###` IDs.

```json
{"content_id":"CONTENT-001","source_ids":["TRL-001"],"destination":"instagram/reel","format":"caption","copy_id":"COPY-001","claim_ids":["CLAIM-004"],"transformation":"short hook from trailer premise","status":"draft"}
```

Every derived public asset should record what it came from, what was changed, and which factual claims it uses. This prevents a repurposed post from slowly drifting away from the film or inventing release facts.

## Repurposing

Repurposing is adaptation, not blind duplication. Preserve the central promise and verified facts while changing length, hook, pacing, visual crop, CTA, and context for the destination.

Use `scripts/campaign_content.py` to validate voice, lineage, claim references, and copy linkage.
