# Pi Install and Project Isolation

[Documentation home](../README.md) | [Up: Install](install.md) | [Next: Quick start](quick-start.md)

## Table of contents

- [What Pi installs](#what-pi-installs)
- [Install for all Pi projects](#install-for-all-pi-projects)
- [Install for one project only](#install-for-one-project-only)
- [Test an unpushed local checkout](#test-an-unpushed-local-checkout)
- [Test for one Pi process only](#test-for-one-pi-process-only)
- [Pin a test revision](#pin-a-test-revision)
- [Remove a project-only install](#remove-a-project-only-install)
- [Share project settings with a team](#share-project-settings-with-a-team)
- [Avoid duplicate skill loading](#avoid-duplicate-skill-loading)
- [Security note](#security-note)

## What Pi installs

Story-Film Skills has a Pi package manifest in `package.json`.

The manifest loads:

- the direct Story-Film `SKILL.md` files; and
- `extensions/story-film-progress/index.ts`.

The manifest does not load `skills/story-film-suite`. That directory is a self-contained copy for `npx skills`. Excluding it prevents Pi from loading duplicate copies of the same Story-Film skills.

The shell installer is not required for a normal Pi package install.

## Install for all Pi projects

Use this only when you want Story-Film Skills in your normal Pi environment.

Private GitHub repository with SSH:

```bash
pi install git:git@github.com:YOUR_GITHUB_USER/Story-Film-Skills.git
```

HTTPS:

```bash
pi install https://github.com/YOUR_GITHUB_USER/Story-Film-Skills
```

Pi stores a user-wide Git package under its user package area and records the package in user settings.

## Install for one project only

This is the recommended beta-test method.

Assume your test project is `MyFilmProject`.

```bash
cd /path/to/MyFilmProject
pi install -l git:git@github.com:YOUR_GITHUB_USER/Story-Film-Skills.git
```

The important option is:

```text
-l
```

It means **project-local**.

Pi writes project package state under:

```text
MyFilmProject/.pi/
```

A Git package is cloned under:

```text
MyFilmProject/.pi/git/
```

The package declaration is stored in:

```text
MyFilmProject/.pi/settings.json
```

Your normal user-wide Pi package settings are not modified.

## Test an unpushed local checkout

You do not need to push every beta change to GitHub.

Keep the Story-Film Skills source checkout outside the film project. Then point the film project at it:

```bash
cd /path/to/MyFilmProject
pi install -l /absolute/path/to/Story-Film-Skills
```

Pi uses that package directory directly.

This is useful when you are changing Story-Film Skills and testing the changes immediately.

## Test for one Pi process only

Use the `-e` option for a throwaway test:

```bash
pi -e git:git@github.com:YOUR_GITHUB_USER/Story-Film-Skills.git
```

Or use a local checkout:

```bash
pi -e /absolute/path/to/Story-Film-Skills
```

The package is temporary for that Pi run. Use project-local `pi install -l` when you need the test setup to survive a restart.

## Pin a test revision

For repeatable testing, install a specific Git tag or commit.

Example shape:

```bash
pi install -l git:git@github.com:YOUR_GITHUB_USER/Story-Film-Skills.git@TAG_OR_COMMIT
```

A pinned revision does not move to a different revision during normal package updates.

## Remove a project-only install

Run the remove command from the same project directory. Use the same package source identity that you installed.

Example:

```bash
cd /path/to/MyFilmProject
pi remove -l git:git@github.com:YOUR_GITHUB_USER/Story-Film-Skills.git
```

Then inspect the project package state:

```bash
pi list
```

## Share project settings with a team

A team can commit:

```text
.pi/settings.json
```

This lets the project declare which Pi package it needs. A trusted project can install a missing declared package when Pi starts.

Do not commit downloaded package caches. Add these entries to the target project's `.gitignore` when needed:

```gitignore
.pi/git/
.pi/npm/
```

Do not ignore `.pi/settings.json` if you want to share the package declaration.

## Avoid duplicate skill loading

Do not install both the Pi package and a second copied Story-Film skill tree into the same Pi scope unless you are deliberately testing deduplication.

For Pi, prefer one of these:

```text
pi install ...
pi install -l ...
pi -e ...
```

Use `install.sh` only as a fallback.

## Security note

A Pi package can load extensions and skills that can perform powerful local actions. Review the package source before you install an untrusted third-party package.

Story-Film Skills is designed for local-first production, but it still runs with the permissions of the Pi process.

## Related pages

- [Install Story-Film Skills](install.md)
- [Quick start](quick-start.md)
- [Pi Todo and pipeline progress](../production/todo-and-progress.md)
- [GitHub repository checklist](../development/github-ready.md)
- [Common problems](../troubleshooting/common-problems.md)
