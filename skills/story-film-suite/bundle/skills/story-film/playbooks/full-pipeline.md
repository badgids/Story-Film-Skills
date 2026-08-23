# Full Pipeline


> Workflow preflight gate: when the requested endpoint includes ComfyUI, complete the `film-production` workflow preflight before step 1 and before any story or canon artifact is created. Select every required workflow now. Later stages reuse those durable selections and do not ask again unless the user explicitly changes one.

1. Run all steps from `idea-to-story.md`.
2. Run `story-to-screenplay.md`, using the new story as source.
3. Run `screenplay-to-film-package.md`.
4. If the project format is `feature-film`, run `feature-scale-production` before large generation or editorial work.
5. Final `continuity-check` across canon, character performance signatures, current story state, screenplay, visible-dialogue requirements, end-frame handoffs, shots, prompts, voices, music, and SFX before generation.
6. Verify the workflow preflight is still complete and use its durable selections for every generation task. Do not reopen workflow selection here or separately rebuild model stacks.
7. If the user requested actual media, run `comfyui-handoff` and the ComfyUI Generate playbook for each approved generation scope. Register every concrete output with `asset-approval`; use `media-qc` and `take-selection` for picture candidates.
8. When the requested endpoint is a complete finished film, run `film-finishing`.
9. When trailers are requested, run `trailer-campaign` after enough approved film media exists.
10. When a social launch campaign is requested, run `social-campaign`.
11. If the user requests deterministic FFmpeg/MLT/ImageMagick edits or editable Kdenlive/Shotcut projects, run `media-editing-and-project-export` at the appropriate postproduction boundary.
12. When the endpoint includes distribution-ready files, run `release-package`.
13. Run project, standalone, style, promotional, and release validators for the requested endpoint.

Done when the requested endpoint is genuinely complete. A generation-ready project is valid when rendering was not requested. A finished-film request requires the actual verified master. A release-campaign request additionally requires its requested trailer/social masters and release manifest.
