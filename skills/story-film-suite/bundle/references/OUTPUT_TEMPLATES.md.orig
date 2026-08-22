# Output Templates

## Creative brief

```text
# Creative Brief
Title:
Format:
Target length:
Audience:
Premise:
Core dramatic question:
Genre:
Tone:
Point of view:
Must include:
Must avoid:
Production constraints:
Open decisions:
```

## Beat

```text
BEAT-##
Purpose:
Cause:
Action:
Turn:
Consequence:
```

## Scene outline entry

```text
SCN-### - short label
Location: LOC-###
Time:
Characters:
Goal:
Conflict:
Turn:
Outcome:
Next-scene cause:
```

## Narrative question

```json
{"question_id":"QST-001","text":"","introduced_in":"SCN-001","status":"open","resolved_in":null,"answer":null}
```

## Narrative promise

```json
{"promise_id":"PROM-001","text":"","setup_in":"SCN-001","status":"open","payoff_in":null,"payoff":null}
```

## Screenplay line manifest row

```json
{"line_id":"LINE-001","scene_id":"SCN-001","order":1,"kind":"dialogue","character_id":"CHAR-001","text":"Exact screenplay dialogue.","audible":true,"on_screen":true,"blocking_required":true}
```

## Production capability

```json
{"status":"conditional","conditions":["subject must already be moving"],"limits":{},"evidence":"tested workflow","notes":""}
```

## Performance blocking row

```json
{"line_id":"LINE-001","scene_id":"SCN-001","character_ids":["CHAR-001"],"initial_state":{"anchor":"door"},"moves":[],"actions":[],"end_state":{"anchor":"door"},"timing":{"source":"estimated","dialogue_duration_s":null,"action_window_s":null},"constraints":[]}
```

## Shooting-script unit

```json
{"line_id":"LINE-001","kind":"dialogue","speaker":"CHAR-001","text":"Exact screenplay dialogue.","current_positions":[],"moves":[],"actions":[],"shot_ids":["SHOT-001"],"timing":{"source":"estimated","speech_duration_s":null,"planned_duration_s":4.0},"constraints":[]}
```

## Media QC row

```json
{"take_id":"TAKE-001","shot_id":"SHOT-001","overall":"pass","checks":{"script_faithfulness":{"status":"pass","evidence":""},"character_identity":{"status":"pass","evidence":""},"motion_smoothness":{"status":"not-checked","evidence":""}},"metrics":[],"notes":""}
```

## Take

```json
{"take_id":"TAKE-001","shot_id":"SHOT-001","prompt_id":"","path":"","status":"candidate","assessment":{},"rejection_reason":""}
```

## Shot list columns

```text
shot_id,scene_id,line_ids,setup,framing,angle,movement,subject_action,dialogue_audio,duration_s,continuity,notes
```

## Music cue

```json
{"cue_id":"MUS-001","scene_id":"SCN-001","start":"","end":"","duration_seconds":30,"dramatic_job":"","energy_curve":"","instrumentation":"","tempo":"","key":"","hit_points":[],"avoid":[]}
```

## SFX cue

```json
{"cue_id":"SFX-001","shot_id":"SHOT-001","source":"","action":"","duration_seconds":1.2,"perspective":"","room":"","processing":"","avoid":[]}
```

## Media registry row

```json
{"schema_version":1,"media_id":"MEDIA-001","kind":"video","group_id":"SHOT-001","source_ids":["TAKE-001"],"path":"04_generation/outputs/shot-001.mp4","status":"candidate","qc_status":"not-checked","created_by":"","metadata":{}}
```

## Audio mix event

```json
{"event_id":"AUD-001","kind":"dialogue","source_id":"VOICE-001","media_id":"MEDIA-101","path":"04_generation/audio/line-001.wav","start":3.25,"source_in":0.0,"duration":2.1,"gain_db":0.0,"pan":0.0,"fade_in":0.01,"fade_out":0.03}
```

## Executable timeline event

```json
{"event_id":"EVT-001","kind":"video","source_id":"TAKE-001","media_id":"MEDIA-001","path":"04_generation/comfyui/outputs/shot-001.mp4","source_in":0.0,"duration":4.5,"shot_id":"SHOT-001"}
```

## Trailer plan entry

```json
{"trailer_id":"TRL-001","type":"official","target_duration":90.0,"duration_tolerance":3.0,"aspect_ratio":"16:9","spoiler_policy":"Do not reveal the final resolution","timeline_path":"06_release/trailers/TRL-001/timeline.json","audio_mix_path":"06_release/trailers/TRL-001/audio_mix.json","output_path":"06_release/trailers/TRL-001/master.mp4","structure":[]}
```

## Social deliverable

```json
{"schema_version":1,"social_id":"SOC-001","platform":"instagram","placement":"reel","media_type":"video","aspect_ratio":"9:16","width":1080,"height":1920,"target_duration":15.0,"duration_tolerance":1.0,"source_ids":["TRL-002"],"timeline_path":"06_release/social/SOC-001/timeline.json","output_path":"06_release/social/masters/SOC-001.mp4","copy_id":"COPY-001","status":"planned"}
```

## Release deliverable

```json
{"delivery_id":"DELIV-001","kind":"film-master","path":"05_post/masters/film_master.mp4","required":true,"qc_status":"pass","source_ids":["MASTER-001"]}
```

## Deterministic tool operation manifest

```json
{
  "schema_version": 1,
  "steps": [
    {
      "step_id": "TOOL-001",
      "tool": "ffmpeg",
      "args": ["-i", "04_generation/input.mp4", "-vf", "scale=1920:1080", "05_post/finished/output.mp4"],
      "inputs": ["04_generation/input.mp4"],
      "outputs": ["05_post/finished/output.mp4"],
      "allow_overwrite": false
    }
  ]
}
```

## Editor project manifest

```json
{
  "schema_version": 1,
  "project_title": "Example",
  "profile": {"width":1920,"height":1080,"fps":24,"progressive":true,"colorspace":709,"audio_channels":2,"audio_sample_rate":48000},
  "bin": [
    {"clip_id":"CLIP-001","kind":"video","path":"04_generation/video/shot-001.mp4","name":"SHOT-001"}
  ],
  "tracks": [
    {
      "track_id":"V1",
      "name":"V1",
      "type":"video",
      "clips":[
        {"edit_id":"EDIT-001","clip_id":"CLIP-001","timeline_start":0.0,"duration":4.5,"source_in":0.0,"filters":[]}
      ]
    }
  ],
  "transitions": [],
  "global_filters": [],
  "markers": [],
  "subtitle_file": "05_post/subtitles.srt",
  "notes": []
}
```

## Editor clip filter

```json
{"service":"volume","properties":{"level":"-6dB"}}
```

## Editor transition

```json
{"service":"composite","a_track":"V1","b_track":"V2","timeline_start":2.0,"duration":1.0,"properties":{}}
```

## Evidence claim

```json
{"claim_id":"CLAIM-001","statement":"","status":"verified","confidence":"high","sources":[{"source_id":"SRC-001","citation":"","url":"","notes":""}],"adopted":false,"adoption_note":"","used_by":[]}
```

## Motion graphic

```json
{"gfx_id":"GFX-001","type":"lower-third","start":2.0,"duration":4.0,"text":"Name","secondary_text":"Role","position":"bottom-left","style":{"safe_margin":0.06},"source_ids":["SHOT-001"]}
```

## Programmatic composition

```json
{"composition_id":"COMP-001","width":1920,"height":1080,"fps":24,"duration_frames":120,"background":"#000000","layers":[{"type":"text","text":"Title","start_frame":0,"duration_frames":120,"x":0,"y":0}]}
```

## Campaign content lineage

```json
{"content_id":"CONTENT-001","destination":"instagram/reel","source_ids":["SOC-001","SHOT-004"],"transformation":"15-second character hook cutdown","copy_id":"COPY-001","claim_ids":["CLAIM-001"]}
```

## Production document manifest entry

```json
{"doc_id":"DOC-001","format":"xlsx","title":"Shot Tracker","source":"03_preproduction/documents/shot_tracker.json","output":"03_preproduction/documents/shot_tracker.xlsx","required":true}
```

## Visual design system

```json
{"schema_version":1,"visual_concept":"","source_refs":["REF-001"],"palette_roles":{},"typography":{},"safe_zones":{},"motifs":[],"motion_behavior":{},"accessibility":[],"exact_text":[],"forbidden_shortcuts":[],"asset_paths":[]}
```


## Creative decision

```json
{"decision_id":"DEC-001","question":"What must the audience understand before the reveal?","answer":"The fence appears protective before it appears restrictive.","status":"decided","depends_on":[],"evidence":[],"affects":["SCN-004","SCN-005"]}
```

## Production work unit

```json
{"unit_id":"UNIT-001","title":"Lock the opening sequence","status":"ready","blocked_by":[],"source_ids":["SCN-001","SCN-002"],"delivers":"Approved opening sequence through picture and sound briefs","acceptance":["continuity passes","generation briefs are executable"]}
```

## Offline ComfyUI batch

```json
{"schema_version":1,"batch_id":"BATCH-001","status":"prepared","sequential":true,"uploads":[{"upload_id":"UP-001","path":"03_preproduction/references/character/pippa.png","type":"input"}],"jobs":[{"job_id":"JOB-001","source_ids":["SHOT-001"],"workflow":"04_generation/comfyui/workflows/SHOT-001.json","patches":[{"node":"12","input":"image","upload_id":"UP-001"}],"blocked_by":[],"output_dir":"04_generation/comfyui/outputs/SHOT-001","timeout_s":1800,"max_transient_retries":1}]}
```

## Resource policy

```json
{"schema_version":1,"local_llm":{"adapter":"command","unload_command":["llm-control","unload"],"reload_command":["llm-control","load"],"health_command":["llm-control","health"]},"comfyui":{"url":"http://127.0.0.1:8188"},"exclusive_generation":{"release_timeout_s":900}}
```

## Rich-document companion pair

```text
03_preproduction/documents/call_sheet.pdf
03_preproduction/documents/call_sheet.md
```
