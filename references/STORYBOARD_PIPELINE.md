# Progressive Storyboard Pipeline

A storyboard is an approval system for visual decisions, not a prompt dump.

Use progressive disclosure. Lock broad decisions before expanding them into more expensive detail.

## Stage 1: Narrative anchors

Select only the moments that must be visually understood for the sequence to work. An anchor can establish geography, introduce a visual fact, mark a power shift, reveal information, define a transition, or carry a payoff.

Write `03_preproduction/storyboards/anchors.jsonl`.

Each record includes:

- anchor ID
- scene ID
- dramatic purpose
- audience question before the anchor
- state change after the anchor
- required characters, props, and location
- continuity facts that must be visible
- status: `draft`, `approved`, `rejected`, or `superseded`

Do not force a fixed number of anchors. A quiet scene may need two. A complicated sequence may need more.

## Stage 2: Visual anchor board

Turn approved narrative anchors into still frames that establish the visual baseline for identity, staging, light, geography, and composition.

Write `03_preproduction/storyboards/beat_board.jsonl`.

The name `beat_board` describes function, not a required grid size. Each frame points back to an anchor and forward to any shot it informs.

Before prompt adaptation, lock the shared visual layer:

- approved character and prop references
- location/geography reference
- palette or color behavior
- source-light logic
- lens/optical character
- camera movement language if movement is already decided
- aspect ratio and delivery constraints

Do not paste a generic style suffix into every prompt. Each model adapter receives the same locked intent and translates it appropriately.

## Stage 3: Sequence boards

Expand only anchors whose blocking, action, eyelines, axis, motion, or cut point cannot be inferred from one still.

Write one file per expanded scope under `03_preproduction/storyboards/sequence_boards/`.

Use the minimum frames needed to show:

- start state
- decisive intermediate action or gaze change
- end state or cut point

Check:

- 180-degree axis and intentional crossings
- eyeline match
- screen direction
- match on action
- prop handoff and occupancy
- entering and exiting frame direction
- physical plausibility

## Stage 4: Motion handoff

Motion is derived from approved sequence state, not invented as a new scene.

Write `03_preproduction/storyboards/motion_handoff.jsonl` or feed the approved state directly into shot briefs.

Each motion record states:

- source storyboard/shot IDs
- initial pose and framing
- subject action over time
- camera action over time
- interaction constraints
- end pose/framing
- sound or dialogue timing when relevant
- what must remain visually unchanged

Video-model adapters then translate this intent into model-specific syntax.

## Review gates

At each stage, use a simple verdict:

- `PASS`: stage communicates the intended decision and can advance
- `REVISE`: concrete fix is required before advancing
- `ESCALATE`: contradictory direction or a taste decision needs the user

Use `crew-review` for high-stakes or repeatedly failing stages. After 3 failed correction rounds on one scope, escalate instead of endlessly regenerating.

## Generated candidates are not approvals

A rendered panel or clip is a take. It becomes production state only after selection. Preserve rejected takes when they are useful evidence, but never let the newest render silently replace the approved one.
