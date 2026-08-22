# Testing and Local-Model Smoke Tests

[Documentation home](../README.md) | [Up: Architecture](architecture.md) | [Next: Contributing](contributing.md)

## Table of contents

- [Prototype milestone](#prototype-milestone)
- [Deterministic regression](#deterministic-regression)
- [Local-model smoke tests](#local-model-smoke-tests)
- [Test order](#test-order)
- [Failure rule](#failure-rule)

## Prototype milestone

v0.0.11 marks the end of the initial prototype-building phase.

After this release, regression testing and local-model smoke testing become normal development work.

## Deterministic regression

Run:

```bash
python scripts/regression_suite.py
```

This validates skills, standalone requirements, eval definitions, character-profile contracts, visible-dialogue synchronization contracts, and deterministic unit/integration tests.

Some media tests require installed public runtimes such as FFmpeg or ImageMagick. A test must state clearly when a runtime is unavailable.

## Local-model smoke tests

The local smoke harness uses an OpenAI-compatible local endpoint. It can work with compatible local servers without hardcoding one vendor.

See available options:

```bash
python scripts/local_smoke.py --help
```

Smoke cases are stored in:

```text
tests/local_smoke_cases.jsonl
```

These tests check whether a small model follows important Story-Film constraints. They are not replacements for deterministic validators.

## Test order

Use this order:

1. deterministic validators;
2. targeted deterministic tests;
3. complete deterministic regression;
4. local-model smoke tests;
5. real project tests;
6. release validation against a clean extracted archive.

## Failure rule

Do not weaken a contract because a test is inconvenient.

Fix the implementation or document a real runtime limitation.

## Production example prompts

Use the [Examples and test prompts](../examples/README.md) when you test an actual agent workflow. The library has three approximately 5-minute videos, three approximately 20-minute short films, and three 90+ minute feature movies.

Use planning-only mode first for a new local model. Use generation-ready mode next. Run a full render only after the smaller gates are stable.

## Related pages

- [Regression plan](../../tests/REGRESSION_PLAN.md)
- [Contributing](contributing.md)
- [GitHub-ready checklist](github-ready.md)
