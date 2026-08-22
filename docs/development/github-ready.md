# GitHub Repository Checklist

[Documentation home](../README.md) | [Up: Contributing](contributing.md) | [Next: Common problems](../troubleshooting/common-problems.md)

## Table of contents

- [Before the first push](#before-the-first-push)
- [Private repository](#private-repository)
- [Pi package install](#pi-package-install)
- [Continuous integration](#continuous-integration)
- [Release check](#release-check)

## Before the first push

Confirm these files exist:

```text
README.md
LICENSE
NOTICE
AUTHORS.md
ATTRIBUTION.md
CONTRIBUTING.md
SECURITY.md
CODE_OF_CONDUCT.md
CITATION.cff
.gitignore
.gitattributes
.github/workflows/validate.yml
```

## Private repository

Create a private GitHub repository. Then push this project with normal Git commands.

Do not commit local secrets, generated model files, large temporary media, or private machine configuration.

## Pi package install

`package.json` contains the Pi package manifest. It loads the direct Story-Film skills and the `story-film-progress` extension. It excludes the self-contained `story-film-suite` copy so Pi does not discover duplicate skill names.

After the private repository exists, test both scopes:

```bash
pi install git:git@github.com:badgids/Story-Film-Skills.git
```

Use a disposable test project for project-local verification:

```bash
cd /path/to/TestFilmProject
pi install -l git:git@github.com:badgids/Story-Film-Skills.git
```

For an unpushed checkout:

```bash
cd /path/to/TestFilmProject
pi install -l /absolute/path/to/Story-Film-Skills
```

Read [Pi install and project isolation](../getting-started/pi-install.md).

## Continuous integration

The included GitHub Actions workflow runs repository validation and deterministic tests. It installs the public command-line dependencies needed by the regression suite.

GPU generation is not required for CI.

## Release check

Before you tag a release:

1. set `VERSION` to the canonical fixed-width value;
2. update `CHANGELOG.md`;
3. rebuild the `story-film-suite` bundle;
4. run the regression suite;
5. run documentation checks;
6. build the archive;
7. extract the archive into a clean directory;
8. run the checks again on that exact extraction.

## Related pages

- [Install](../getting-started/install.md)
- [Testing](testing.md)
- [License](../reference/licensing.md)
