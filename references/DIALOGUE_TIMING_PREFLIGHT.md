# Dialogue Timing Preflight

Measure approved dialogue before expensive video generation.

For each planned clip, compare approved line start time plus measured duration with the clip duration. Classify each line or clip as:

- `fits`
- `needs-timing-rebalance`
- `impossible`

The preflight must not silently speed up, truncate, rewrite, reassign, or overlap dialogue to make a shot fit. A model/shot plan may declare a bounded rebalance window; otherwise an overflow is a blocker returned to shot design.
