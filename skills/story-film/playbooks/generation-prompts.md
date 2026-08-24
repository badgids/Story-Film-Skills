# Generation Prompts Only


> Workflow preflight gate: before step 1, record the explicit ComfyUI task categories required by this prompt scope and complete workflow selection for every missing category. Later steps reuse those durable selections and do not ask again unless the user explicitly changes one.

1. Read the supplied model-neutral brief and canon.
2. Read `WORKFLOW_SELECTION.md` and `MODEL_ROUTING.md`.
3. Use the workflow selected during playbook-entry preflight for the target task. A missing selection here is a preflight blocker; do not postpone the workflow question until prompt generation.
4. Determine the prompt adapter from that selected workflow/model family when the workflow needs model-specific prompt grammar. Do not ask for a separate checkpoint/VAE/LoRA selection.
5. When the adapter is `minimax-h3`, automatically run the Story-Film H3 stack; the user does not need to invoke its sub-skills separately. Read `skills/h3-prompt-writing/SKILL.md`, run `scripts/minimax_h3_skill_router.py` against the brief, read and apply the returned style skill when one is selected, then apply `skills/minimax-h3/SKILL.md`. An explicit user selection of a specialist H3 style skill overrides automatic style selection but still rejoins this same H3 stack.
6. `h3-prompt-writing` controls final H3 syntax; the style skill only enriches content; the selected workflow plus Story-Film canon/reference/dialogue/audio/timing authority remain higher.
7. Record `h3_base_skill: h3-prompt-writing` and `h3_style_skill: <name-or-none>` outside the final H3 model prompt for auditability.
8. Before `prompt-qc`, run `scripts/minimax_h3_prompt_validator.py` against the final H3 model-prompt body using the actual workflow mode and requested duration. A validator failure is a generation blocker; repair the prompt and rerun validation rather than submitting malformed H3 syntax.
9. Run `prompt-qc`.
10. Do not create new story facts to make the prompt more colorful.

Done when each source brief has a self-contained prompt compatible with its selected workflow.
