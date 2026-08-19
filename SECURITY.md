# Security Policy

## Supported development line

Security fixes are applied to the current development line unless the project owner states otherwise.

## Report a security problem

For a private repository, report the problem to the repository owner through a private GitHub channel or another private contact method that the owner provides.

Do not publish API keys, access tokens, private model endpoints, personal paths, or sensitive project media in a public issue.

## Security design rules

Story-Film Skills:

- uses project-relative reusable paths;
- avoids shell execution when structured argv execution is available;
- keeps secrets out of handoff documents;
- treats external files as untrusted input;
- respects ImageMagick security policy;
- validates ComfyUI workflows before resource-safe handoff;
- does not let the no-LLM runner make semantic repairs;
- records deterministic state before model unload and machine restart boundaries.
