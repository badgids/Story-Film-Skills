# Quick Start

[Documentation home](../README.md) | [Up: Install](install.md) | [Next: How it works](how-it-works.md)

## Table of contents

- [Start a project](#start-a-project)
- [Ask Pi to work](#ask-pi-to-work)
- [Watch progress](#watch-progress)
- [Validate the project](#validate-the-project)

## Start a project

Create a project folder.

```bash
python scripts/init_story_project.py /path/to/MyFilm --title "My Film" --format feature-film
```

This creates the durable Story-Film folder structure.

## Ask Pi to work

Use the main router.

```text
/skill:story-film Create a feature film from this story idea: ...
```

The router selects a playbook.

The playbook selects specialist skills.

## Watch progress

For a multi-step process, the pipeline progress files record the current task.

If you installed the Pi extension, use:

```text
/story-todo status
```

For command-line status, use:

```bash
python scripts/pipeline_progress.py status /path/to/MyFilm
```

## Validate the project

Run:

```bash
python scripts/validate_story_project.py /path/to/MyFilm
```

A validation error is a blocker. Fix the error before you mark that step complete.

## Related pages

- [Story to film](../workflows/story-to-film.md)
- [Feature film](../workflows/feature-film.md)
- [Pi Todo](../production/todo-and-progress.md)
