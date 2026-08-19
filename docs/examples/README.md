# Examples and Test Prompts

[Documentation home](../README.md) | [Quick start](../getting-started/quick-start.md) | [Testing](../development/testing.md)

Use these examples to learn Story-Film Skills or test a new model, machine, ComfyUI setup, or release.

## Table of contents

- [Choose a production level](#choose-a-production-level)
- [Choose a test depth](#choose-a-test-depth)
- [Recommended test order](#recommended-test-order)
- [How to start a test](#how-to-start-a-test)
- [What to check](#what-to-check)
- [Related pages](#related-pages)

## Choose a production level

- [About 5-minute video examples](video-examples.md): 3 compact tests.
- [About 20-minute short-film examples](short-film-examples.md): 3 medium tests.
- [90+ minute movie examples](movie-examples.md): 3 feature-scale tests.

The source prompt files are also available in [`examples/`](../../examples/README.md).

## Choose a test depth

**Planning-only** is the best first test. It builds and validates the project but stops before expensive generation.

Add this before the selected prompt:

```text
TEST MODE: Complete and validate all planning, story, screenplay, preproduction, production-state, and generation-ready artifacts. Stop before executing image, audio, or video generation. Report the exact next action.
```

**Generation-ready** tests the resource handoff. It stops after deterministic ComfyUI work is fully prepared.

```text
TEST MODE: Continue through validated, fully prepared ComfyUI offline batches and resource-handoff state. Do not start the expensive generation jobs. Stop only when the local LLM could be unloaded safely.
```

**Full production** uses the example prompt without a prefix. It can run generation and continue toward the final master.

## Recommended test order

1. Run one 5-minute prompt in planning-only mode.
2. Fix any model or environment problem.
3. Run the same prompt in generation-ready mode.
4. Run a full 5-minute production when resources are ready.
5. Move to a 20-minute prompt.
6. Use a 90+ minute movie prompt only after the smaller tests are stable.

## How to start a test

For beta isolation, install Story-Film Skills only in the test project. See [Pi install and project isolation](../getting-started/pi-install.md).

Start Pi in an empty test-project directory. Then copy one complete prompt into Pi. Do not split one example across multiple messages.

For a native Pi installation, you can explicitly route with:

```text
/skill:story-film
```

Then paste the example prompt.

## What to check

Check the Pi Todo. Check validation failures. Check durable state after restart. For generation tests, check batch recovery and resource handoff. For completed productions, check delivery QC and the final completeness audit.

Do not judge only whether the story is entertaining. These examples also test whether Story-Film Skills keeps its production contracts.

## Related pages

- [Testing guide](../development/testing.md)
- [Feature film workflow](../workflows/feature-film.md)
- [Feature-scale production](../production/feature-scale.md)
- [Resource-safe generation](../generation/resource-safe.md)
- [Recovery](../operations/recovery.md)
