# Generation Prompts Only


> Workflow preflight gate: before step 1, record the explicit ComfyUI task categories required by this prompt scope and complete workflow selection for every missing category. Later steps reuse those durable selections and do not ask again unless the user explicitly changes one.

1. Read the supplied model-neutral brief and canon.
2. Read `WORKFLOW_SELECTION.md` and `MODEL_ROUTING.md`.
3. Use the workflow selected during playbook-entry preflight for the target task. A missing selection here is a preflight blocker; do not postpone the workflow question until prompt generation.
4. Determine the prompt adapter from that selected workflow/model family when the workflow needs model-specific prompt grammar. Do not ask for a separate checkpoint/VAE/LoRA selection.
5. When the adapter is `minimax-h3`, always read `skills/h3-prompt-writing/SKILL.md`, run `scripts/minimax_h3_skill_router.py` against the brief, read the returned style skill when one is selected, then apply `skills/minimax-h3/SKILL.md`. `h3-prompt-writing` controls final H3 syntax; the style skill only enriches content; Story-Film canon/reference/dialogue/timing authority remains higher.
6. Record `h3_base_skill: h3-prompt-writing` and `h3_style_skill: <name-or-none>` outside the final H3 model prompt for auditability.
7. Run `prompt-qc`.
8. Do not create new story facts to make the prompt more colorful.

Done when each source brief has a self-contained prompt compatible with its selected workflow.
