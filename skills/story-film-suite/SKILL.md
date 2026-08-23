---
name: story-film-suite
description: Self-contained Story-Film Skills bundle for story, book, screenplay, image, audio, video, film, postproduction, and release work. Use this entry point when Story-Film Skills was installed with npx skills.
author: Alan Guice (Badgids)
license: Apache-2.0
---

# Story-Film Skills Suite

This is the self-contained installation entry point.

1. Read `bundle/skills/story-film/SKILL.md` as the main router.
2. When that router names another Story-Film skill, read it from `bundle/skills/<skill-name>/SKILL.md`.
3. Run shared tools from `bundle/scripts/`.
4. Read shared contracts from `bundle/references/`.
5. Use `bundle/docs/README.md` for the user manual.
6. Bundled ComfyUI workflows are under `bundle/comfyui_workflows/<task>/<model>/`.
7. Do not assume that any files exist outside this skill directory.

For Pi's optional interactive Todo extension, install `bundle/extensions/story-film-progress/index.ts` into the Pi extensions directory, or use the Git clone installer instead.
