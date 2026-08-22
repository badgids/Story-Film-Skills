# Reference Development

1. Read brief, canon, continuity, planned scenes, and shot needs.
2. `reference-assets`: create the minimal reference manifest and missing-reference report.
3. `reference-authority`: assign only the authority scopes each `REF-###` is allowed to control and add `must_not_control` boundaries where accidental cross-control is a risk.
4. `reference-sheets`: create native character, location, or prop multi-view plans only where production needs them. Add functional/mechanical prop views when later action depends on how the prop works.
5. `visual-bible` when the reference set needs a shared visual language or moodboard brief.
6. Use the appropriate image, video, voice, or music adapter to write generation prompts. When one edit would overload composition, environment/style, and identity, use the staged grounding contract instead of making one reference control everything.
7. Create `contact_sheet_plan.json` when candidates need structured comparison. Atlas grid layout remains reference-only unless explicitly granted composition authority.
8. Run `prompt-qc` on generated prompt documents.
9. Approve reference versions only after continuity-critical traits are inspectable.

Done when every requested reference has a stable `REF-###`, explicit role, preserve rules, provenance, approval state, and a standalone generation or review plan.
