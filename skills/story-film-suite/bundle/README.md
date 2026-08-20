# Story-Film Skills

**Author/Developer:** Alan Guice (Badgids)  
**License:** Apache License 2.0  
*Copyright © 2026 Alan Guice (Badgids).*

Story-Film Skills is a local-first Agent Skills suite for story writing, book development, screenwriting, image/audio/video generation, directing, feature-film production, postproduction, and release delivery. It uses durable project files, stable IDs, deterministic validators, and recoverable workflows so an AI agent does not have to remember a whole film inside one chat context.

**Display version:** `v0.0.21`
**Canonical version:** `00.00.21`

v0.0.11 completes the initial prototype-building phase. The project now includes deterministic regression tests and a local-model smoke-test harness for the next testing phase.

## Table of contents

- [What it can do](#what-it-can-do)
- [Feature-length production](#feature-length-production)
- [Choose generation models](#choose-generation-models)
- [Install](#install)
  - [Install with Pi](#install-with-pi-recommended)
  - [Project-only Pi install](#project-only-pi-install)
  - [One-session Pi test](#one-session-pi-test)
  - [Git clone and install.sh fallback](#git-clone-and-installsh-fallback)
  - [Install with npx skills](#install-with-npx-skills)
- [Use Story-Film Skills](#use-story-film-skills)
- [Example and test prompts](#example-and-test-prompts)
- [Video generation model choice](#video-generation-model-choice)
- [Local LLM and ComfyUI memory handoff](#local-llm-and-comfyui-memory-handoff)
- [Interactive Pi Todo](#interactive-pi-todo)
- [Documentation](#documentation)
- [Testing](#testing)
- [Repository development](#repository-development)
- [License, copyright, and attribution](#license-copyright-and-attribution)

## What it can do

Story-Film Skills can manage a project from a loose idea to a finished release package. Major capability groups include:

- story, novel, and book development;
- creative decision interviews and production specifications;
- screenplay writing and revision;
- character, world, location, visual, and continuity bibles;
- `SCN-###`, `LINE-###`, `SHOT-###`, `TAKE-###`, and other stable production identities;
- scene geography, blocking, shooting scripts, shot lists, storyboards, and previz;
- voice, dialogue, music, ambience, Foley, and SFX planning;
- ComfyUI workflow validation and execution;
- user-controlled per-process ComfyUI model stacks, including exact VAEs, text encoders, LoRAs, audio models, upscalers, and custom model choices;
- resource-safe offline ComfyUI batches for machines that cannot hold an LLM and generation model at the same time;
- deterministic media QC and take selection;
- FFmpeg/FFprobe, ImageMagick, optional MLT, Kdenlive, and Shotcut workflows;
- executable film, trailer, teaser, social, and release timelines;
- production documents with required Markdown equivalents;
- final delivery QC, checksums, release packages, and feature-film completeness auditing.

A plan is not a render. A generated file is not automatically approved. A master file is not automatically a complete film.

## Feature-length production

v0.0.11 adds nine controls for long films:

1. **Sequence production** uses `SEQ-###` units so the agent works on a manageable part of the film.
2. **Context shards** give the agent only the data needed for the current sequence.
3. **Production health reports** summarize deterministic blockers and warnings.
4. **Long-range continuity** checks facts that must remain correct across distant sequences.
5. **Generation budgets** schedule `JOB-###` work against declared RAM and VRAM limits.
6. **Reboot recovery** stores exact durable checkpoints instead of rebuilding state from chat memory.
7. **Partial batch recovery** preserves completed generation work and retries only affected jobs.
8. **Editorial reconciliation** checks selected shots, sequence order, duplicate events, and timeline coverage.
9. **Final completeness auditing** blocks a false completion claim until required production evidence is present.

Read the [Feature-scale production guide](docs/production/feature-scale.md).

## Choose generation models

Story-Film Skills polls the active ComfyUI server before model-specific generation. Pi can then show the installed choices for image generation, image editing, video, TTS, music, SFX/Foley, upscaling, frame interpolation, VAEs, text encoders, LoRAs, and other server-reported model folders.

The user owns these choices. MiniMax H3 is the default video adapter only when the user did not choose a video adapter. That default does not choose a concrete checkpoint, VAE, text encoder, or LoRA.

Read [Choose generation models and ComfyUI resources](docs/generation/model-selection.md).

## Install

### Install with Pi (recommended)

Story-Film Skills is a native Pi package. Pi can install the skills and the optional Todo/resource-status extension from the same repository. Pi packages can be installed from Git, HTTPS, SSH, or a local directory.

For a private GitHub repository over SSH:

```bash
pi install git:git@github.com:YOUR_GITHUB_USER/Story-Film-Skills.git
```

For an HTTPS repository:

```bash
pi install https://github.com/YOUR_GITHUB_USER/Story-Film-Skills
```

This is a user-wide install. Pi records it in the user package settings. Start a new Pi session after installation.

### Project-only Pi install

Use this mode for beta testing or when one project needs Story-Film Skills but your other Pi projects do not. Run the command **from the project that will use Story-Film Skills**:

```bash
cd /path/to/MyFilmProject
pi install -l git:git@github.com:YOUR_GITHUB_USER/Story-Film-Skills.git
```

The `-l` option uses project-local Pi settings and package storage under that project's `.pi/` directory. It does not add Story-Film Skills to the normal user-wide Pi package settings.

You can also test an unpushed local checkout without copying it into your Pi installation:

```bash
cd /path/to/MyFilmProject
pi install -l /absolute/path/to/Story-Film-Skills
```

For team projects, you can commit `.pi/settings.json` so Pi knows which package the project needs. Do not commit downloaded package caches such as `.pi/git/` or `.pi/npm/`.

Read the [Pi installation and project-isolation guide](docs/getting-started/pi-install.md).

### One-session Pi test

For a temporary test that should disappear when the Pi process exits:

```bash
pi -e git:git@github.com:YOUR_GITHUB_USER/Story-Film-Skills.git
```

From a local checkout:

```bash
pi -e /absolute/path/to/Story-Film-Skills
```

This is useful for a quick smoke test. Use `pi install -l` when you want the package to persist for one project.

### Git clone and install.sh fallback

`install.sh` remains available as a compatibility and recovery fallback. It is no longer the preferred Pi installation method.

```bash
git clone git@github.com:YOUR_GITHUB_USER/Story-Film-Skills.git
cd Story-Film-Skills
bash install.sh
```

The fallback installer uses configurable Pi paths and does not contain a personal machine path.

To install only the skill files with the fallback installer:

```bash
bash install.sh --skills-only
```

### Install with npx skills

The repository also contains a self-contained skill named `story-film-suite` for the open Agent Skills ecosystem.

For a private repository:

```bash
npx skills add git@github.com:YOUR_GITHUB_USER/Story-Film-Skills.git --skill story-film-suite -g -y
```

The `npx skills` route remains useful outside Pi. For Pi itself, prefer `pi install` because the Pi package can load both the direct Story-Film skills and the Pi Todo/resource-status extension together.

Full installation help: [docs/getting-started/install.md](docs/getting-started/install.md).

## Use Story-Film Skills

For the Git clone/Pi installation, start with:

```text
/skill:story-film Create a feature film from this story...
```

For the self-contained `npx skills` bundle, start with:

```text
/skill:story-film-suite Create a feature film from this story...
```

Create a new project directly with Python:

```bash
python scripts/init_story_project.py /path/to/MyFilm
```

Validate it:

```bash
python scripts/validate_story_project.py /path/to/MyFilm
```

For a feature film, the normal high-level path is:

```text
idea
  -> creative discovery
  -> story
  -> screenplay
  -> sequence plan
  -> context shards
  -> preproduction
  -> generation plans
  -> resource-safe media generation when needed
  -> take selection and QC
  -> editorial
  -> audio/video finishing
  -> feature reconciliation
  -> final master
  -> completeness audit
  -> trailers, campaign, and release package
```

Read the [Quick start](docs/getting-started/quick-start.md) or the [Feature film workflow](docs/workflows/feature-film.md).


## Example and test prompts

v0.0.11 includes nine copy-and-paste production prompts for examples and regression testing:

- 3 videos with a target runtime of about 5 minutes;
- 3 short films with a target runtime of about 20 minutes;
- 3 movies with a required runtime of at least 90 minutes.

Use a prompt unchanged for a full production test. For a cheaper first test, the documentation provides planning-only and generation-ready prefixes that stop before expensive rendering.

Start with the [Examples and test prompts guide](docs/examples/README.md). The raw prompt library is in [`examples/`](examples/README.md).

## Video generation model choice

The user owns the video-generation model choice. If the user does not choose a video model, Story-Film Skills uses **MiniMax H3** (`minimax-h3`). LTX 2.5 and other adapters remain optional choices. Story-Film Skills must not silently replace MiniMax H3 because another model appears to fit a shot better or because MiniMax H3 is missing.

See [Choose the video generation model](docs/generation/model-selection.md).

## Local LLM and ComfyUI memory handoff

Story-Film Skills is local-first. It supports computers where the local LLM and a large ComfyUI model cannot fit in RAM or VRAM at the same time.

Before the LLM is unloaded, Story-Film Skills can finish every creative decision, stage inputs, patch exact ComfyUI filenames, validate the final workflows, and arm a deterministic batch. A detached runner can then:

```text
unload local LLM
  -> execute prepared ComfyUI jobs without LLM calls
  -> update deterministic Pi status
  -> unload ComfyUI models and free memory
  -> reload and health-check the local LLM
  -> resume from durable state
```

The no-LLM runner cannot rewrite prompts or make creative decisions. If semantic repair is needed, it stops and returns the job to the LLM after resource cleanup.

Read [Resource-safe local generation](docs/generation/resource-safe.md).

## Interactive Pi Todo

Long workflows use durable progress files:

```text
00_project/pipeline_progress.json
00_project/progress_events.jsonl
00_project/HANDOFF.md
```

The optional Pi extension renders this state as a stage/step/substep Todo. The widget is not the source of truth.

Useful Pi commands:

```text
/story-todo status
/story-todo current
/story-todo up
/story-todo down
/story-todo page-up
/story-todo page-down
/story-resource
```

During exclusive ComfyUI generation, the extension can display deterministic runtime status without invoking the unloaded LLM or consuming its context window.

Read [Pi Todo and pipeline progress](docs/production/todo-and-progress.md).

## Documentation

The full documentation starts at:

**[Story-Film Skills Documentation](docs/README.md)**

The documentation uses controlled, simple English based on important ASD-STE100 principles and ELI5 teaching goals. It is not an official ASD-STE100 certification.

Main paths:

- [Overview](docs/getting-started/overview.md)
- [Installation](docs/getting-started/install.md)
- [Story to finished film](docs/workflows/story-to-film.md)
- [Feature-film workflow](docs/workflows/feature-film.md)
- [Feature-scale production](docs/production/feature-scale.md)
- [ComfyUI generation](docs/generation/comfyui.md)
- [Postproduction](docs/postproduction/editorial.md)
- [Final completeness audit](docs/release/completion.md)
- [Recovery](docs/operations/recovery.md)
- [Command reference](docs/reference/commands.md)
- [Glossary](docs/reference/glossary.md)
- [Testing](docs/development/testing.md)
- [Examples and test prompts](docs/examples/README.md)
- [Common problems](docs/troubleshooting/common-problems.md)

Every documentation section links back to the documentation home and to related pages.

## Testing

Run the deterministic regression suite:

```bash
python scripts/regression_suite.py
```

Check documentation links and structure:

```bash
python scripts/check_docs.py
```

Build or refresh the self-contained npx bundle:

```bash
python scripts/build_npx_bundle.py --check
```

The post-prototype local-model smoke harness is included:

```bash
python scripts/local_smoke.py --help
```

Smoke cases are in `tests/local_smoke_cases.jsonl`. They are designed for an OpenAI-compatible local endpoint such as a compatible llama.cpp server.

Read [Testing and local-model smoke tests](docs/development/testing.md).

## Repository development

Before a pull request:

```bash
python scripts/regression_suite.py
python scripts/check_docs.py
python scripts/build_npx_bundle.py --check
```

GitHub-ready files include CI, issue templates, pull-request guidance, security guidance, contribution rules, citation metadata, and repository ignore rules.

Read [Contributing](CONTRIBUTING.md) and the [GitHub repository checklist](docs/development/github-ready.md).

## License, copyright, and attribution

Story-Film Skills is licensed under the **Apache License 2.0**.

Copyright © 2026 Alan Guice (Badgids).

Alan Guice (Badgids) is the original Author/Developer of Story-Film Skills. The repository preserves this attribution in `NOTICE`, `AUTHORS.md`, `ATTRIBUTION.md`, source headers, and skill metadata. Redistributions and derivative works must preserve notices as required by Apache-2.0.

See:

- [LICENSE](LICENSE)
- [NOTICE](NOTICE)
- [AUTHORS.md](AUTHORS.md)
- [ATTRIBUTION.md](ATTRIBUTION.md)
- [License and attribution guide](docs/reference/licensing.md)
