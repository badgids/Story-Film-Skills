# Contributing

[Documentation home](../README.md) | [Up: Testing](testing.md) | [Next: GitHub checklist](github-ready.md)

## Table of contents

- [Before a change](#before-a-change)
- [While changing](#while-changing)
- [Before a pull request](#before-a-pull-request)
- [Compatibility](#compatibility)

## Before a change

1. Read the related skill and reference contract.
2. Find the durable source of truth.
3. Check dependency effects.
4. Decide how the change will be verified.

## While changing

Keep reusable paths project-relative.

Do not add personal machine paths.

Do not add an em dash character to project text.

Keep public creative behavior useful without optional runtimes.

When you add a rich document output, also add the meaningful Markdown companion.

## Before a pull request

Run:

```bash
python scripts/regression_suite.py
python scripts/check_docs.py
```

If the change affects local-model behavior, run the relevant smoke cases too.

## Compatibility

Do not silently change a stable schema or stable ID meaning.

If a migration is required, document it and preserve a clear upgrade path.

## Related pages

- [Root CONTRIBUTING.md](../../CONTRIBUTING.md)
- [Testing](testing.md)
- [Architecture](architecture.md)
