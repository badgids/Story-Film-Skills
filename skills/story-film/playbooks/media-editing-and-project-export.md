# Media Editing and Project Export

Use when the user requests deterministic video/audio/image manipulation, editorial interchange, or a Kdenlive/Shotcut project.

1. Read `media-toolkit` and discover only the runtime capabilities needed for the task.
2. Route moving-image, audio, subtitle, container, metadata, stream, filter-graph, capture, or QC work to `ffmpeg`.
3. Route service-graph, multitrack MLT, serialization, or MLT rendering work to `mlt`.
4. Route still-image, image-sequence, poster, title-card, mask, montage, transform, color, or comparison work to `imagemagick`.
5. Use existing specialized helpers such as `audio-master`, `video-finishing`, `timeline-assembly`, `delivery-qc`, or `social-reframe` when they already encode the requested operation and its validation.
6. For reproducible custom operations, save a `TOOL-###` manifest and execute it through `scripts/media_toolkit.py manifest`.
7. If the user requests Kdenlive or Shotcut, reconcile the final editorial intent into `05_post/editorial/editor_project.json` or derive it from the executable timeline.
8. Run `editor-project-export`, then `kdenlive-export`, `shotcut-export`, or both.
9. Parse and target-validate the exported XML. If the target GUI editor is actually installed and target certification was requested, perform an editor import/open integration check.
10. Run appropriate media or delivery QC on any newly rendered production asset and update project dependency state when an approved source changed.

Done when the requested deterministic media edits and editable editor projects actually exist and their applicable validation gates pass.

11. Use `edit-assist` for silence maps, non-destructive jump-cut proposals, captions, transcript-driven clips, subject-aware reframing, and delivery compression when these operations are requested.
12. Use `motion-graphics` for reusable intros, outros, lower thirds, watermarks, title cards, mattes, fades, and transitions rather than burying packaging decisions inside opaque filter strings.
13. Use `programmatic-video` when the requested visual is better expressed as a deterministic code-driven composition. Keep the portable `COMP-###` manifest authoritative; use the Remotion adapter only when appropriate and license-compatible.

