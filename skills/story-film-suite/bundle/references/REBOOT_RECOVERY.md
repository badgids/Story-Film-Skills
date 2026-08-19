# Reboot Recovery

[Feature-scale contract](FEATURE_SCALE_PRODUCTION.md) | [Pipeline progress](PIPELINE_PROGRESS.md) | [Documentation home](../docs/README.md)

Use a recovery checkpoint before a long generation run, before a machine reboot, and after an approved sequence boundary.

```bash
python scripts/recovery_checkpoint.py checkpoint PROJECT --note "SEQ-004 approved"
```

After a restart:

```bash
python scripts/recovery_checkpoint.py resume PROJECT
```

The checkpoint stores hashes and control cursors. It does not copy large media.

Resume modes are:

- `exact`: recorded control files match the checkpoint
- `dirty`: one or more control files changed after the checkpoint
- `resource-interrupted`: the project says a resource handoff was active when the process stopped

Do not reconstruct progress from chat memory after a restart. Read the recovery report and the durable project files.
