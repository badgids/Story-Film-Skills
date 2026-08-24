#!/usr/bin/env python3
from __future__ import annotations
import argparse, re
from pathlib import Path

BASE_FIELDS=("integrated_multimodal_description:","overall_soundscape:","non_diegetic_music:")
REF_FIELDS=("subject_definitions:","summary:","retention_analysis:","detailed_description:","overall_soundscape:","non_diegetic_music:")
REF_LABEL_RX=re.compile(r"<(?:Subject|Picture|Video|Audio) \d+>")
SHOT_RX=re.compile(r"\[Shot (\d+)\](?: At (\d{2}):(\d{2}\.\d{3}),)?")
DIALOGUE_RX=re.compile(r"<d>\[[^\]\r\n]+\][\s\S]*?</d>")

def _positions(text, fields):
    pos=[]
    for f in fields:
        c=text.count(f)
        if c != 1:
            raise ValueError(f"expected exactly one {f!r}, found {c}")
        pos.append(text.index(f))
    if pos != sorted(pos):
        raise ValueError("required H3 fields/sections are out of order")
    return pos

def _validate_shots(text,duration):
    ms=list(SHOT_RX.finditer(text))
    if not ms: raise ValueError("missing [Shot 1]")
    ids=[int(m.group(1)) for m in ms]
    if ids != list(range(1,len(ids)+1)):
        raise ValueError(f"shot numbers must be sequential starting at 1, found {ids}")
    if ms[0].group(2) is not None:
        raise ValueError("[Shot 1] must not have a cut timestamp")
    last=0.0
    for m in ms[1:]:
        if m.group(2) is None:
            raise ValueError(f"[Shot {m.group(1)}] is missing At MM:SS.mmm cut time")
        value=int(m.group(2))*60.0+float(m.group(3))
        if value <= last: raise ValueError("shot cut times must be strictly increasing")
        if value >= duration: raise ValueError(f"shot cut time {value:.3f}s must be before duration {duration:.3f}s")
        last=value

def _validate_dialogue(text):
    if text.count("<d>") != text.count("</d>"):
        raise ValueError("unbalanced <d> dialogue tags")
    if text.count("<d>") != len(DIALOGUE_RX.findall(text)):
        raise ValueError("every <d> block must use <d>[Language] exact content</d> format")

def validate(text,mode,duration):
    errors=[]
    try:
        if duration <= 0: raise ValueError("duration must be positive")
        if mode=="Ref2VA":
            p=_positions(text,REF_FIELDS)
            defs=text[p[0]+len(REF_FIELDS[0]):p[1]]
            missing=sorted(set(REF_LABEL_RX.findall(text[p[1]:]))-set(REF_LABEL_RX.findall(defs)))
            if missing: raise ValueError("Ref2VA labels used later but not defined: "+", ".join(missing))
            desc=text[p[3]+len(REF_FIELDS[3]):p[4]]
        else:
            p=_positions(text,BASE_FIELDS)
            first=text.lstrip().splitlines()[0] if text.strip() else ""
            token=f"{duration:.2f}-second mark"
            if mode=="T2VA":
                if first.startswith("For the target video,") or first.startswith("How the reference pictures align"):
                    raise ValueError("T2VA must not start with a keyframe alignment instruction")
            elif mode=="I2VA":
                required="For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced."
                if first != required: raise ValueError("I2VA first-frame alignment is malformed")
            elif mode=="FL2VA":
                if not first.startswith("How the reference pictures align with the target video") or "0.00-second mark" not in first or token not in first:
                    raise ValueError("FL2VA first/last-frame alignment is malformed")
            elif mode=="L2VA":
                if not first.startswith("How the reference pictures align with the target video") or token not in first:
                    raise ValueError("L2VA last-frame alignment is malformed")
            else:
                raise ValueError(f"unsupported H3 mode {mode!r}")
            desc=text[p[0]+len(BASE_FIELDS[0]):p[1]]
        _validate_shots(desc,duration)
        _validate_dialogue(text)
    except ValueError as exc:
        errors.append(str(exc))
    return errors

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",required=True,choices=("T2VA","I2VA","FL2VA","L2VA","Ref2VA"))
    ap.add_argument("--duration",required=True,type=float)
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--prompt-file")
    g.add_argument("--text")
    a=ap.parse_args()
    text=Path(a.prompt_file).read_text(encoding="utf-8") if a.prompt_file else a.text
    errors=validate(text,a.mode,a.duration)
    if errors:
        for e in errors: print("ERROR",e)
        return 1
    print(f"PASS: MiniMax H3 {a.mode} prompt format validated")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
