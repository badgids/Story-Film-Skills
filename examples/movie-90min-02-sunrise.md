# MOVIE-90M-002: After the Third Sunrise

**Production level:** 90+ minute movie  
**Target runtime:** at least 90 minutes, target about 105 minutes  
**Purpose:** Example and end-to-end test prompt for Story-Film Skills.

## Prompt

```text
Use Story-Film Skills to create a complete original feature film with a final runtime of at least 90 minutes. Target about 105 minutes.

Working title: After the Third Sunrise

Genre: Science-fiction survival thriller with a strong human core.

Premise: A small maintenance crew on a remote research settlement wakes after an automated emergency shutdown. The settlement's navigation system says three local sunrises passed while they were unconscious, but external instruments disagree about how much time has passed. Communications are damaged. A supply craft is approaching on an old trajectory that is now unsafe. The crew must repair enough of the settlement to warn the craft while discovering why the emergency system altered their records.

Use five to seven important speaking characters with different technical roles, fears, loyalties, and personal stakes. Keep the mystery solvable from information that appears on screen. Do not solve major problems with unexplained technology.

Create clear rules for the settlement, life support, communications, power, vehicles, tools, suits, and timekeeping. Track injuries, oxygen, power availability, equipment state, access permissions, character knowledge, physical geography, warnings, and every change to the central time discrepancy.

Use full feature-scale Story-Film production controls. Divide the film into `SEQ-###` units. Create bounded context shards. Maintain `CONT-###` anchors across distant sequences. Build generation resource profiles so high-VRAM video work does not fight the local LLM. Prepare deterministic offline ComfyUI batches before unloading the LLM. Preserve completed generation jobs after failures. Reconcile every selected shot into the final feature timeline.

Take the project from concept through feature screenplay, preproduction, image/audio/video generation, voices, sound design, original score direction, editorial, visual and audio finishing, captions, final master, delivery QC, completeness audit, trailer, campaign, and release package.

Testing goal: stress feature-scale continuity, complex resource scheduling, repeated environments, technical props, multiple voices, action geography, failure recovery, and long editorial timelines.
```

## Test notes

Use the prompt without changes for a full production test. For a faster planning test, use the test modes in [Examples and test prompts](README.md).
