# Model Adapter Contract

Every generation model skill converts a model-neutral brief into provider-specific prompt syntax.

## Inputs

- one stable source ID
- canon and continuity facts needed by that source
- exact dialogue or visible text when applicable
- named reference media and roles
- hard duration or frame constraints when applicable

## Adapter behavior

1. Read the source brief.
2. Read only the canon entries it references.
3. Select the model mode before writing the prompt.
4. Preserve the source intent and hard constraints.
5. Translate the brief into the model's preferred prompt grammar.
6. Put execution settings outside prose when they are not semantic prompt content.
7. Save the adapter output without modifying the source brief.
8. Run `prompt-qc`.

## Forbidden adapter behavior

- adding backstory or visual identity not present upstream
- silently changing dialogue
- silently changing clip duration
- referring to prior prompts instead of restating continuity
- copying another model's syntax just because it looks cinematic

## Done

A model operator can pair the adapter output with the named references and execute the task without needing the originating chat.
