# Install Story-Film Skills

[Documentation home](../README.md) | [Up: Start here](overview.md) | [Next: Pi install and project isolation](pi-install.md)

## Table of contents

- [Requirements](#requirements)
- [Recommended Pi install](#recommended-pi-install)
- [Project-only install](#project-only-install)
- [Temporary one-session test](#temporary-one-session-test)
- [Install from a local checkout](#install-from-a-local-checkout)
- [Git clone and install.sh fallback](#git-clone-and-installsh-fallback)
- [Install with npx skills](#install-with-npx-skills)
- [Check the install](#check-the-install)

## Requirements

You need Pi if you use the native `pi install` method.

You need Git when Pi installs Story-Film Skills from a Git repository.

Python 3 is needed for deterministic Story-Film scripts and validators.

ComfyUI is optional until you want actual AI media generation.

## Recommended Pi install

Story-Film Skills is a Pi package. The package manifest loads the direct Story-Film skills and the Pi Todo/resource-status extension.

For a private GitHub repository that uses SSH authentication:

```bash
pi install git:git@github.com:YOUR_GITHUB_USER/Story-Film-Skills.git
```

For HTTPS:

```bash
pi install https://github.com/YOUR_GITHUB_USER/Story-Film-Skills
```

This install is user-wide. Use it only when you want Story-Film Skills available in all normal Pi projects.

## Project-only install

Use project-local mode for beta testing or for a project that is the only project that needs Story-Film Skills.

First, enter the target project directory. Then use `-l`:

```bash
cd /path/to/MyFilmProject
pi install -l git:git@github.com:YOUR_GITHUB_USER/Story-Film-Skills.git
```

Pi writes the package declaration to `.pi/settings.json` in that project. Git packages are stored under that project's `.pi/git/` directory. This does not add Story-Film Skills to the user-wide Pi package settings.

If a team must use the same package, you can commit `.pi/settings.json`. Pi can install a missing declared package when the trusted project starts. Do not commit package caches such as `.pi/git/` or `.pi/npm/`.

See [Pi install and project isolation](pi-install.md) for removal, pinning, and test examples.

## Temporary one-session test

Use `-e` when you want to load the package only for the current Pi process:

```bash
pi -e git:git@github.com:YOUR_GITHUB_USER/Story-Film-Skills.git
```

The temporary package is not added to persistent package settings.

## Install from a local checkout

You can test code that you have not pushed yet. From the target film project:

```bash
pi install -l /absolute/path/to/Story-Film-Skills
```

Pi points at the local package directory. It does not need a copy under the normal Pi installation.

For one process only:

```bash
pi -e /absolute/path/to/Story-Film-Skills
```

## Git clone and install.sh fallback

The shell installer remains a fallback for older setups or manual recovery.

```bash
git clone git@github.com:YOUR_GITHUB_USER/Story-Film-Skills.git
cd Story-Film-Skills
bash install.sh
```

To install only skills with the fallback installer:

```bash
bash install.sh --skills-only
```

## Install with npx skills

Story-Film Skills includes the self-contained `story-film-suite` skill for the open Agent Skills ecosystem.

```bash
npx skills add git@github.com:YOUR_GITHUB_USER/Story-Film-Skills.git --skill story-film-suite -g -y
```

Use this route for agents that use the `skills` CLI. For Pi, prefer `pi install`.

## Check the install

Run:

```bash
pi list
```

Start a new Pi session. Then use:

```text
/skill:story-film <your request>
```

For a repository checkout, you can also run:

```bash
python scripts/validate_skills.py
python scripts/validate_standalone.py
```

## Related pages

- [Pi install and project isolation](pi-install.md)
- [Quick start](quick-start.md)
- [Pi Todo and pipeline progress](../production/todo-and-progress.md)
- [Testing](../development/testing.md)
- [Common problems](../troubleshooting/common-problems.md)
