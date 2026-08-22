# Staged Reference Grounding

When a single image-edit operation would overload composition, environment, identity, and style constraints, Story-Film may build a storyboard/reference frame in bounded stages:

1. layout/composition pass;
2. environment/style grounding pass;
3. character/prop identity grounding pass.

Every pass records its seed when applicable, prompt, input `REF-###` bindings, authority scopes, and output candidate. A later pass may not silently promote a background reference into composition authority or a character atlas into camera authority.

Use this mode only when the selected local workflow supports iterative editing reliably. It is not a universal requirement.
