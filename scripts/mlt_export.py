#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import math
import xml.etree.ElementTree as ET
from pathlib import Path

from media_runtime import MediaRuntimeError, project_path, project_root, read_json
from render_timeline import validate_timeline


def frames(seconds: float, fps: float) -> int:
    return max(1, int(round(float(seconds) * fps)))


def prop(parent, name, value):
    node = ET.SubElement(parent, 'property', {'name': name})
    node.text = str(value)
    return node


def export_mlt(root: Path, timeline: dict, output: Path) -> None:
    errors = validate_timeline(root, timeline, require_sources=False)
    if errors:
        raise MediaRuntimeError('; '.join(errors))
    video = timeline['video']
    fps = float(video['fps'])
    fps_num = int(round(fps * 1000))
    fps_den = 1000
    total_frames = sum(frames(rec['duration'], fps) for rec in timeline['events'])
    mlt = ET.Element('mlt', {
        'LC_NUMERIC': 'C',
        'version': '7.0.0',
        'root': '.',
        'producer': 'main_bin',
    })
    ET.SubElement(mlt, 'profile', {
        'description': 'Badgids Story Film Timeline',
        'width': str(int(video['width'])),
        'height': str(int(video['height'])),
        'progressive': '1',
        'sample_aspect_num': '1',
        'sample_aspect_den': '1',
        'display_aspect_num': str(int(video['width'])),
        'display_aspect_den': str(int(video['height'])),
        'frame_rate_num': str(fps_num),
        'frame_rate_den': str(fps_den),
        'colorspace': '709',
    })

    playlist = ET.SubElement(mlt, 'playlist', {'id': 'playlist0'})
    prop(playlist, 'kdenlive:track_name', 'V1')
    for idx, rec in enumerate(timeline['events'], 1):
        pid = f'producer{idx}'
        count = frames(rec['duration'], fps)
        kind = rec['kind']
        source_in = frames(rec.get('source_in', 0.0), fps) if kind == 'video' and rec.get('source_in', 0.0) else 0
        producer = ET.SubElement(mlt, 'producer', {
            'id': pid, 'in': str(source_in), 'out': str(source_in + count - 1)
        })
        if kind in {'video', 'image'}:
            prop(producer, 'resource', rec['path'])
            prop(producer, 'mlt_service', 'avformat-novalidate')
            prop(producer, 'kdenlive:clipname', rec.get('event_id', pid))
            if kind == 'image':
                prop(producer, 'ttl', '1')
        else:
            prop(producer, 'resource', rec.get('color', 'black'))
            prop(producer, 'mlt_service', 'color')
        ET.SubElement(playlist, 'entry', {'producer': pid, 'in': str(source_in), 'out': str(source_in + count - 1)})

    audio_playlist_id = None
    if timeline.get('audio_master_path'):
        audio_playlist_id = 'playlist_audio'
        apid = 'producer_audio'
        producer = ET.SubElement(mlt, 'producer', {'id': apid, 'in': '0', 'out': str(max(0, total_frames - 1))})
        prop(producer, 'resource', timeline['audio_master_path'])
        prop(producer, 'mlt_service', 'avformat-novalidate')
        prop(producer, 'set.test_audio', '0')
        audio_playlist = ET.SubElement(mlt, 'playlist', {'id': audio_playlist_id})
        prop(audio_playlist, 'kdenlive:track_name', 'A1 Master')
        ET.SubElement(audio_playlist, 'entry', {'producer': apid, 'in': '0', 'out': str(max(0, total_frames - 1))})

    tractor = ET.SubElement(mlt, 'tractor', {'id': 'tractor0', 'in': '0', 'out': str(max(0, total_frames - 1))})
    multitrack = ET.SubElement(tractor, 'multitrack')
    ET.SubElement(multitrack, 'track', {'producer': 'playlist0'})
    if audio_playlist_id:
        ET.SubElement(multitrack, 'track', {'producer': audio_playlist_id, 'hide': 'video'})

    output.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(mlt)
    ET.indent(tree, space='  ')
    tree.write(output, encoding='utf-8', xml_declaration=True)


def main() -> int:
    ap = argparse.ArgumentParser(description='Export an executable timeline as portable MLT XML.')
    ap.add_argument('project_dir')
    ap.add_argument('--timeline', default='05_post/timeline.json')
    ap.add_argument('--output', default='05_post/editorial/film_timeline.mlt')
    args = ap.parse_args()
    root = project_root(args.project_dir)
    timeline_path = project_path(root, args.timeline, must_exist=True)
    output = project_path(root, args.output)
    timeline = read_json(timeline_path)
    export_mlt(root, timeline, output)
    ET.parse(output)
    print(args.output)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except MediaRuntimeError as exc:
        print(f'ERROR {exc}')
        raise SystemExit(2)
