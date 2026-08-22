# Regression and Local Smoke Test Plan

[Documentation home](../docs/README.md) | [Testing guide](../docs/development/testing.md)

v0.0.11 closes the initial prototype phase. The next development phase can run local-model smoke tests in addition to deterministic regression tests.

## Deterministic regression

Run:

```bash
python scripts/regression_suite.py
```

This gate runs skill validation, standalone validation, static future-eval validation, and the deterministic unit/integration suite.

## Local-model smoke tests

Start an OpenAI-compatible local model server first. Then run:

```bash
python scripts/regression_suite.py --local-smoke --llm-url http://127.0.0.1:8080 --llm-model YOUR_MODEL_ALIAS
```

You can also run one case:

```bash
python scripts/local_smoke.py --case SMOKE-001 --model YOUR_MODEL_ALIAS
```

The local smoke suite is intentionally small. It tests high-risk weak-model behaviors. It does not replace an end-to-end film production trial.
