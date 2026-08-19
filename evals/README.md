# Badgids Story Film Evals

These evals are designed to expose failures that large frontier models often hide but small local models reveal quickly.

## Static suite

Run:

```bash
python scripts/run_evals.py
```

This validates package structure, standalone rules, case files, style rules, playbook references, project initialization, dependency behavior, and deterministic fixture checks. It does not call an LLM.

## Live weak-model suite

Use an external agent command that accepts the case prompt on stdin:

```bash
python scripts/run_evals.py --runner 'your-agent-command' --suite weak-model --work-root ./eval-work
```

Useful suites are:

- `weak-model`
- `standalone`
- `continuity`
- `adapter`
- `style`
- `security`

Run all live suites by omitting `--suite`.

Each case gets an isolated project workspace. The evaluator scores required files, stable IDs, exact payloads, model grammar separation, portable paths, forbidden shortcuts, and style rules.

## Score existing outputs

```bash
python scripts/run_evals.py --score-workspaces /path/to/workspaces
```

Each child directory must be named with the case ID.

## Case format

JSONL fields:

- `id`
- `suite`
- `task`
- `setup_files`
- `required_files`
- `forbidden_files`
- `required_patterns`
- `forbidden_patterns`
- `exact_files`
- `required_json_paths`
- `notes`

Keep one failure mode per case whenever practical. A good regression case is small enough that a weak local model cannot hide the failure inside unrelated work.
