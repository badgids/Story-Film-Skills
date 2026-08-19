# Film Finishing

Use after picture, dialogue, music, and sound candidates exist and the requested endpoint is an actual finished film.

1. Run `asset-approval` across selected picture, dialogue, voiceover, score, ambience, Foley, and SFX groups. Do not use newest-file selection.
2. Run `production-coverage` for the full film. Resolve blockers before postproduction.
3. Run `media-qc` on selected picture candidates that have not been inspected and resolve hard failures.
4. Run `video-finishing` only for selected picture that needs normalization, aspect correction, or approved upscale processing.
5. Run `edit-plan` and `editorial-package` to reconcile picture order, exact dialogue placement, audio cues, subtitles, and pickups.
6. Run `audio-master`: create `05_post/audio_mix.json` and render `05_post/masters/film_audio_master.wav` when actual output is requested.
7. Run `timeline-assembly`: create and validate `05_post/timeline.json` from approved picture and post decisions.
8. Run `film-master` to render the actual movie and run delivery QC.
9. Run `editor-project-export` when the user requests an editable Kdenlive or Shotcut project. Use `mlt-export` only when generic MLT interchange is sufficient.
10. Register and preserve the verified film master through `asset-approval`.

Done only when an actual requested master exists and passes its blocking delivery checks. A timeline manifest without a rendered master is not a finished-film endpoint.

11. Before final master assembly, use `edit-assist` for requested speech-aware cleanup/captions/reframes and `motion-graphics` for approved titles, lower thirds, watermarks, mattes, or transitions. Keep all such derivatives traceable to their source media.
12. Use `programmatic-video` only for elements that benefit from code-driven composition; render them to approved media before final timeline/master unless the target editor explicitly carries the composition as an external source.

