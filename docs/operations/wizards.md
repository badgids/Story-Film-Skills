# Human-Only Production Wizards

[Documentation home](../README.md) | [Up: Session handoff](session-handoff.md) | [Next: Command reference](../reference/commands.md)

## Table of contents

- [When to use a wizard](#when-to-use-a-wizard)
- [When not to use one](#when-not-to-use-one)
- [Wizard behavior](#wizard-behavior)
- [Documentation](#documentation)

## When to use a wizard

Use a guided production wizard for a step that only a person can complete, such as a manual account action, a physical production step, or an interface action that has no usable automation path.

## When not to use one

Do not make the user perform work that the agent can safely perform itself.

Do not invent interface steps. Verify current instructions when an external interface can change.

## Wizard behavior

A wizard should:

1. show one stage at a time;
2. show progress;
3. explain the exact human action;
4. capture only the values that are required;
5. hide secrets when input is secret;
6. ask before an irreversible action;
7. support safe restart when possible.

## Documentation

A reusable wizard must have a Markdown sidecar that explains its purpose, prerequisites, stages, inputs, outputs, and recovery behavior.

## Related pages

- [Session handoff](session-handoff.md)
- [Documentation style](../reference/documentation-style.md)
