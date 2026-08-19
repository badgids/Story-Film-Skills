# Full Pipeline

1. Run all steps from `idea-to-story.md`.
2. Run `story-to-screenplay.md`, using the new story as source.
3. Run `screenplay-to-film-package.md`.
4. If the project format is `feature-film`, run `feature-scale-production` before large generation or editorial work.
5. Final `continuity-check` across canon, story, screenplay, shots, prompts, voices, music, and SFX before generation.
6. If the user requested actual media, run `comfyui-handoff` and the ComfyUI Generate playbook for each approved generation scope. Register every concrete output with `asset-approval`; use `media-qc` and `take-selection` for picture candidates.
7. When the requested endpoint is a complete finished film, run `film-finishing`.
8. When trailers are requested, run `trailer-campaign` after enough approved film media exists.
9. When a social launch campaign is requested, run `social-campaign`.
10. If the user requests deterministic FFmpeg/MLT/ImageMagick edits or editable Kdenlive/Shotcut projects, run `media-editing-and-project-export` at the appropriate postproduction boundary.
11. When the endpoint includes distribution-ready files, run `release-package`.
12. Run project, standalone, style, promotional, and release validators for the requested endpoint.

Done when the requested endpoint is genuinely complete. A generation-ready project is valid when rendering was not requested. A finished-film request requires the actual verified master. A release-campaign request additionally requires its requested trailer/social masters and release manifest.
