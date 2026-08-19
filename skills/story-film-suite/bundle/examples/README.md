# Story-Film Skills Example and Test Prompts

These prompts are stable example inputs for Story-Film Skills v0.0.11.

They are not expected to produce the exact same creative result on every model. They are designed to test whether the production system keeps the correct structure, state, validation, recovery, and delivery behavior.

## Production levels

- [About 5-minute videos](../docs/examples/video-examples.md): 3 prompts.
- [About 20-minute short films](../docs/examples/short-film-examples.md): 3 prompts.
- [90+ minute movies](../docs/examples/movie-examples.md): 3 prompts.

## Test depth

Use one of these methods.

### Planning-only test

Add this line before an example prompt:

```text
TEST MODE: Complete and validate all planning, story, screenplay, preproduction, production-state, and generation-ready artifacts. Stop before executing image, audio, or video generation. Report the exact next action.
```

This is the cheapest first test for a new local model.

### Generation-ready handoff test

Add this line before an example prompt:

```text
TEST MODE: Continue through validated, fully prepared ComfyUI offline batches and resource-handoff state. Do not start the expensive generation jobs. Stop only when the local LLM could be unloaded safely.
```

This tests the LLM-to-ComfyUI boundary without rendering the whole production.

### Full production test

Use the example prompt without a test-mode prefix. Story-Film Skills should continue through the requested final master and release gates.

## Important

A 90+ minute full production test can require substantial storage, generation time, RAM, and VRAM. Start with planning-only mode when you test a new model or configuration.
