# Edit Assist and Motion Graphics

Use when the user wants deterministic cleanup, captions, reframing, clipping, compression, lower thirds, title cards, watermarks, end cards, or transitions around an existing edit.

1. Read `edit-assist` and perform only approved non-destructive editorial assists.
2. Preserve a silence map or transcript when those operations drive cuts or captions.
3. Read `design-system` when a graphics package should match campaign identity.
4. Build `GFX-###` records through `motion-graphics`.
5. Use `programmatic-video` only when the requested animation exceeds ordinary FFmpeg/ImageMagick compositing.
6. Register outputs and run `media-qc` or `delivery-qc` as appropriate.
7. Reconcile affected editor projects and campaign deliverables through `project-impact`.

Done when the edited media is verified and all graphics remain reproducible from project state.
