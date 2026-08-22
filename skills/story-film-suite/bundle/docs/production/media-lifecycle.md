# Media Lifecycle

[Documentation home](../README.md) | [Up: Production](../README.md#3-feature-film-production)

## Table of contents

- [Rejected media](#rejected-media)
- [Approved-output repair](#approved-output-repair)
- [Related pages](#related-pages)

## Rejected media

Rejection and physical deletion are separate. `scripts/media_lifecycle.py delete` deletes only the exact registered rejected, superseded, or retired media path after safety checks and appends a cleanup ledger entry. It never performs directory sweeps.

## Approved-output repair

`repair-copy MEDIA-### --dest PATH` can restore a missing disposable runtime copy only from the registered approved primary media. Repair means copying verified existing media, not regenerating an approved shot. The repair is recorded in the cleanup ledger with a SHA-256 digest.

## Related pages

- [Reference authority](reference-authority.md)
- [Temporal continuity](temporal-continuity.md)
