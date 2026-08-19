#!/usr/bin/env python3
# Copyright 2026 Alan Guice (Badgids)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import uuid
import xml.etree.ElementTree as ET
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from media_runtime import MediaRuntimeError, project_path, project_root, read_json
from render_timeline import validate_timeline

NS = uuid.UUID('1f85eb97-bdd5-4de6-b8ef-c03d3a09d5bc')


def prop(parent: ET.Element, name: str, value: Any) -> ET.Element:
    node = ET.SubElement(parent, 'property', {'name': str(name)})
    node.text = '' if value is None else str(value)
    return node


def fps_fraction(fps: float) -> tuple[int, int]:
    frac = Fraction(str(fps)).limit_denominator(1001)
    return frac.numerator, frac.denominator


def clock(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds - hours * 3600 - minutes * 60
    return f'{hours:02d}:{minutes:02d}:{secs:06.3f}'


def end_time(start: float, duration: float, fps: float) -> float:
    # MLT out points are inclusive. Move one frame back from the mathematical end.
    return max(start, start + duration - (1.0 / fps))


def is_portable_path(value: str) -> bool:
    if not value:
        return False
    if value.startswith('/') or re.match(r'^[A-Za-z]:[\\/]', value):
        return False
    return '..' not in Path(value).parts


def derive_editor_project(timeline: dict[str, Any]) -> dict[str, Any]:
    video = timeline['video']
    t = 0.0
    bin_items: list[dict[str, Any]] = []
    clips: list[dict[str, Any]] = []
    for i, rec in enumerate(timeline['events'], 1):
        clip_id = f'CLIP-{i:03d}'
        if rec['kind'] == 'color':
            item = {'clip_id': clip_id, 'kind': 'color', 'color': rec.get('color', 'black'), 'name': rec['event_id']}
        else:
            item = {'clip_id': clip_id, 'kind': rec['kind'], 'path': rec['path'], 'name': rec['event_id']}
        bin_items.append(item)
        clips.append({
            'edit_id': f'EDIT-{i:03d}', 'clip_id': clip_id, 'timeline_start': round(t, 6),
            'duration': float(rec['duration']), 'source_in': float(rec.get('source_in', 0.0)),
            'filters': rec.get('filters', []), 'source_ids': [rec['event_id']],
        })
        t += float(rec['duration'])
    tracks = [{'track_id': 'V1', 'name': 'V1', 'type': 'video', 'clips': clips}]
    if timeline.get('audio_master_path'):
        aid = f'CLIP-{len(bin_items)+1:03d}'
        bin_items.append({'clip_id': aid, 'kind': 'audio', 'path': timeline['audio_master_path'], 'name': 'Film Audio Master'})
        tracks.append({
            'track_id': 'A1', 'name': 'A1 Master', 'type': 'audio', 'clips': [{
                'edit_id': f'EDIT-{len(clips)+1:03d}', 'clip_id': aid, 'timeline_start': 0.0,
                'duration': round(t, 6), 'source_in': 0.0, 'filters': [], 'source_ids': ['MASTER-AUDIO']
            }]
        })
    return {
        'schema_version': 1,
        'project_title': timeline.get('title', 'Badgids Story Film Project'),
        'profile': {
            'width': int(video['width']), 'height': int(video['height']), 'fps': float(video['fps']),
            'progressive': True, 'sample_aspect_num': 1, 'sample_aspect_den': 1,
            'colorspace': 709, 'audio_channels': 2, 'audio_sample_rate': 48000,
        },
        'bin': bin_items,
        'tracks': tracks,
        'transitions': timeline.get('transitions', []),
        'global_filters': timeline.get('global_filters', []),
        'markers': timeline.get('markers', []),
        'subtitle_file': timeline.get('subtitle_path', '') if timeline.get('subtitle_policy') != 'none' else '',
        'notes': ['Derived from executable timeline.'],
    }


def validate_editor_project(root: Path, project: dict[str, Any], require_sources: bool = False) -> list[str]:
    errors: list[str] = []
    if project.get('schema_version') != 1:
        errors.append('schema_version must be 1')
    profile = project.get('profile')
    if not isinstance(profile, dict):
        errors.append('profile must be an object')
        return errors
    for k in ('width', 'height', 'fps'):
        try:
            if float(profile.get(k, 0)) <= 0:
                errors.append(f'profile.{k} must be positive')
        except Exception:
            errors.append(f'profile.{k} must be numeric')
    bin_items = project.get('bin')
    if not isinstance(bin_items, list):
        errors.append('bin must be an array')
        return errors
    by_id: dict[str, dict[str, Any]] = {}
    for i, item in enumerate(bin_items, 1):
        cid = item.get('clip_id', '')
        if not re.fullmatch(r'CLIP-\d{3,}', cid):
            errors.append(f'bin item {i}: clip_id must be CLIP-###')
        elif cid in by_id:
            errors.append(f'bin item {i}: duplicate clip_id {cid}')
        by_id[cid] = item
        kind = item.get('kind')
        if kind not in {'video', 'audio', 'image', 'color'}:
            errors.append(f'{cid or i}: unsupported bin kind {kind!r}')
        if kind == 'color':
            if not item.get('color'):
                errors.append(f'{cid}: color clip requires color')
        else:
            path = item.get('path', '')
            if not is_portable_path(path):
                errors.append(f'{cid}: path must be project-relative and portable')
            elif require_sources and not project_path(root, path).exists():
                errors.append(f'{cid}: missing source {path}')
    tracks = project.get('tracks')
    if not isinstance(tracks, list) or not tracks:
        errors.append('tracks must be a nonempty array')
        return errors
    track_ids: set[str] = set()
    edit_ids: set[str] = set()
    for ti, track in enumerate(tracks, 1):
        tid = track.get('track_id', '')
        if not re.fullmatch(r'[VA]\d+', tid):
            errors.append(f'track {ti}: track_id must look like V1 or A1')
        if tid in track_ids:
            errors.append(f'track {ti}: duplicate track_id {tid}')
        track_ids.add(tid)
        if track.get('type') not in {'video', 'audio'}:
            errors.append(f'{tid}: type must be video or audio')
        clips = track.get('clips', [])
        if not isinstance(clips, list):
            errors.append(f'{tid}: clips must be an array')
            continue
        ordered = sorted(clips, key=lambda x: float(x.get('timeline_start', 0)))
        for ci, edit in enumerate(ordered, 1):
            eid = edit.get('edit_id', '')
            if not re.fullmatch(r'EDIT-\d{3,}', eid):
                errors.append(f'{tid} clip {ci}: edit_id must be EDIT-###')
            if eid in edit_ids:
                errors.append(f'{tid} clip {ci}: duplicate edit_id {eid}')
            edit_ids.add(eid)
            if edit.get('clip_id') not in by_id:
                errors.append(f'{eid}: unknown clip_id {edit.get("clip_id")!r}')
            for k in ('timeline_start', 'duration', 'source_in'):
                try:
                    value = float(edit.get(k, 0.0))
                    if k == 'duration' and value <= 0:
                        errors.append(f'{eid}: duration must be positive')
                    if k != 'duration' and value < 0:
                        errors.append(f'{eid}: {k} cannot be negative')
                except Exception:
                    errors.append(f'{eid}: {k} must be numeric')
            filters = edit.get('filters', [])
            if not isinstance(filters, list):
                errors.append(f'{eid}: filters must be an array')
            else:
                for f in filters:
                    if not isinstance(f, dict) or not f.get('service'):
                        errors.append(f'{eid}: each filter requires a service')
        # More than two overlapping clips on one Kdenlive track cannot fit its two internal playlists.
        points: list[tuple[float, int]] = []
        for edit in ordered:
            s = float(edit.get('timeline_start', 0.0)); e = s + float(edit.get('duration', 0.0))
            points += [(s, 1), (e, -1)]
        active = 0
        for _, delta in sorted(points, key=lambda x: (x[0], x[1])):
            active += delta
            if active > 2:
                errors.append(f'{tid}: more than two overlapping clips require separate editor tracks')
                break
    for tr in project.get('transitions', []):
        if not isinstance(tr, dict) or not tr.get('service'):
            errors.append('each transition requires a service')
            continue
        if tr.get('a_track') not in track_ids or tr.get('b_track') not in track_ids:
            errors.append(f'transition references unknown tracks: {tr.get("a_track")} -> {tr.get("b_track")}')
    subtitle = project.get('subtitle_file', '')
    if subtitle:
        if not is_portable_path(subtitle):
            errors.append('subtitle_file must be project-relative and portable')
        elif require_sources and not project_path(root, subtitle).exists():
            errors.append(f'missing subtitle_file {subtitle}')
    return errors


def add_profile(mlt: ET.Element, profile: dict[str, Any]) -> None:
    num, den = fps_fraction(float(profile['fps']))
    width = int(profile['width']); height = int(profile['height'])
    common = math.gcd(width, height)
    ET.SubElement(mlt, 'profile', {
        'description': f'Badgids {width}x{height} {float(profile["fps"]):g} fps',
        'width': str(width), 'height': str(height),
        'progressive': '1' if profile.get('progressive', True) else '0',
        'sample_aspect_num': str(int(profile.get('sample_aspect_num', 1))),
        'sample_aspect_den': str(int(profile.get('sample_aspect_den', 1))),
        'display_aspect_num': str(width // common), 'display_aspect_den': str(height // common),
        'frame_rate_num': str(num), 'frame_rate_den': str(den),
        'colorspace': str(profile.get('colorspace', 709)),
    })


def producer_for_item(mlt: ET.Element, item: dict[str, Any], producer_id: str, fps: float) -> ET.Element:
    producer = ET.SubElement(mlt, 'producer', {'id': producer_id})
    kind = item['kind']
    if kind == 'color':
        prop(producer, 'resource', item.get('color', 'black'))
        prop(producer, 'mlt_service', 'color')
        prop(producer, 'set.test_audio', '0')
    else:
        prop(producer, 'resource', item['path'])
        prop(producer, 'mlt_service', 'avformat-novalidate')
        if kind == 'audio':
            prop(producer, 'set.test_image', '0')
        if kind == 'image':
            prop(producer, 'ttl', '1')
            prop(producer, 'eof', 'pause')
    prop(producer, 'kdenlive:clipname', item.get('name', item['clip_id']))
    prop(producer, 'shotcut:caption', item.get('name', item['clip_id']))
    return producer


def append_filter(parent: ET.Element, rec: dict[str, Any], filter_id: str, start: float, duration: float, fps: float,
                  editor: str) -> None:
    attrs = {'id': filter_id, 'in': clock(start), 'out': clock(end_time(start, duration, fps))}
    node = ET.SubElement(parent, 'filter', attrs)
    prop(node, 'mlt_service', rec['service'])
    if editor == 'shotcut' and rec.get('shotcut_filter'):
        prop(node, 'shotcut:filter', rec['shotcut_filter'])
    if editor == 'kdenlive' and rec.get('kdenlive_id'):
        prop(node, 'kdenlive_id', rec['kdenlive_id'])
    for k, v in rec.get('properties', {}).items():
        prop(node, k, v)


def lane_assign(clips: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    lanes: list[list[dict[str, Any]]] = [[], []]
    ends = [0.0, 0.0]
    for edit in sorted(clips, key=lambda x: float(x.get('timeline_start', 0.0))):
        start = float(edit.get('timeline_start', 0.0))
        duration = float(edit.get('duration', 0.0))
        target = None
        for li in range(2):
            if start >= ends[li] - 1e-9:
                target = li
                break
        if target is None:
            raise MediaRuntimeError('more than two overlapping clips on one track; split them into separate tracks')
        lanes[target].append(edit)
        ends[target] = start + duration
    return lanes


def fill_playlist(playlist: ET.Element, clips: list[dict[str, Any]], producer_ids: dict[str, str], fps: float,
                  editor: str, filter_counter: list[int]) -> None:
    cursor = 0.0
    for edit in sorted(clips, key=lambda x: float(x.get('timeline_start', 0.0))):
        start = float(edit['timeline_start']); duration = float(edit['duration']); source_in = float(edit.get('source_in', 0.0))
        if start > cursor + 1e-6:
            ET.SubElement(playlist, 'blank', {'length': clock(start - cursor)})
        entry = ET.SubElement(playlist, 'entry', {
            'producer': producer_ids[edit['clip_id']],
            'in': clock(source_in), 'out': clock(end_time(source_in, duration, fps)),
        })
        if editor == 'kdenlive':
            prop(entry, 'kdenlive:id', edit['edit_id'])
        for f in edit.get('filters', []):
            filter_counter[0] += 1
            append_filter(entry, f, f'filter{filter_counter[0]}', source_in, duration, fps, editor)
        cursor = max(cursor, start + duration)


def export_kdenlive(project: dict[str, Any], output: Path) -> dict[str, Any]:
    profile = project['profile']; fps = float(profile['fps'])
    mlt = ET.Element('mlt', {'LC_NUMERIC': 'C', 'version': '7.0.0', 'root': '.', 'producer': 'main_bin'})
    add_profile(mlt, profile)
    producer_ids: dict[str, str] = {}
    for i, item in enumerate(project['bin']):
        pid = f'producer{i}'
        producer_ids[item['clip_id']] = pid
        producer_for_item(mlt, item, pid, fps)

    track_tractor_ids: dict[str, str] = {}
    filter_counter = [0]
    total_end = 0.0
    for ti, track in enumerate(project['tracks']):
        tractor_id = f'track_tractor_{ti}'
        track_tractor_ids[track['track_id']] = tractor_id
        lanes = lane_assign(track.get('clips', []))
        playlist_ids = []
        for li, lane in enumerate(lanes):
            plid = f'track_{ti}_playlist_{li}'
            playlist_ids.append(plid)
            pl = ET.SubElement(mlt, 'playlist', {'id': plid})
            fill_playlist(pl, lane, producer_ids, fps, 'kdenlive', filter_counter)
        tr = ET.SubElement(mlt, 'tractor', {'id': tractor_id})
        prop(tr, 'kdenlive:track_name', track.get('name', track['track_id']))
        prop(tr, 'kdenlive:trackheight', track.get('height', 67))
        prop(tr, 'kdenlive:audio_track', 1 if track['type'] == 'audio' else 0)
        prop(tr, 'kdenlive:locked_track', 1 if track.get('locked') else 0)
        for plid in playlist_ids:
            attrs = {'producer': plid}
            if track['type'] == 'video': attrs['hide'] = 'audio'
            else: attrs['hide'] = 'video'
            ET.SubElement(tr, 'track', attrs)
        for edit in track.get('clips', []):
            total_end = max(total_end, float(edit['timeline_start']) + float(edit['duration']))

    sequence_id = 'sequence_tractor'
    sequence_uuid = str(uuid.uuid5(NS, project.get('project_title', '') + '|sequence'))
    seq = ET.SubElement(mlt, 'tractor', {'id': sequence_id, 'in': clock(0), 'out': clock(end_time(0, total_end or 1/fps, fps))})
    prop(seq, 'kdenlive:uuid', sequence_uuid)
    prop(seq, 'kdenlive:sequenceproperty.activeTrack', 0)
    for track in project['tracks']:
        attrs = {'producer': track_tractor_ids[track['track_id']]}
        if track['type'] == 'video': attrs['hide'] = 'audio'
        else: attrs['hide'] = 'video'
        ET.SubElement(seq, 'track', attrs)

    track_index = {t['track_id']: i for i, t in enumerate(project['tracks'])}
    for i, transition in enumerate(project.get('transitions', []), 1):
        start = float(transition.get('timeline_start', 0.0)); duration = float(transition.get('duration', 0.0))
        node = ET.SubElement(seq, 'transition', {'id': f'transition{i}', 'in': clock(start), 'out': clock(end_time(start, duration, fps))})
        prop(node, 'a_track', track_index[transition['a_track']])
        prop(node, 'b_track', track_index[transition['b_track']])
        prop(node, 'mlt_service', transition['service'])
        for k, v in transition.get('properties', {}).items(): prop(node, k, v)
    for gf in project.get('global_filters', []):
        filter_counter[0] += 1
        append_filter(seq, gf, f'filter{filter_counter[0]}', 0.0, total_end or 1/fps, fps, 'kdenlive')
    if project.get('subtitle_file'):
        filter_counter[0] += 1
        sf = {'service': 'avfilter.subtitles', 'properties': {'av.filename': project['subtitle_file'], 'internal_added': 237, 'kdenlive:locked': 1}}
        append_filter(seq, sf, f'filter{filter_counter[0]}', 0.0, total_end or 1/fps, fps, 'kdenlive')

    main_bin = ET.SubElement(mlt, 'playlist', {'id': 'main_bin'})
    prop(main_bin, 'kdenlive:docproperties.version', '1.1')
    prop(main_bin, 'kdenlive:docproperties.decimalPoint', '.')
    prop(main_bin, 'kdenlive:docproperties.documentid', str(uuid.uuid5(NS, project.get('project_title', '') + '|document')))
    prop(main_bin, 'kdenlive:documentnotes', '\n'.join(project.get('notes', [])))
    for item in project['bin']:
        entry = ET.SubElement(main_bin, 'entry', {'producer': producer_ids[item['clip_id']]})
        prop(entry, 'kdenlive:id', item['clip_id'])
    entry = ET.SubElement(main_bin, 'entry', {'producer': sequence_id})
    prop(entry, 'kdenlive:id', 'SEQUENCE-001')

    wrapper = ET.SubElement(mlt, 'tractor', {'id': 'project_tractor', 'in': clock(0), 'out': clock(end_time(0, total_end or 1/fps, fps))})
    prop(wrapper, 'kdenlive:projectTractor', 1)
    ET.SubElement(wrapper, 'track', {'producer': sequence_id, 'in': clock(0), 'out': clock(end_time(0, total_end or 1/fps, fps))})

    output.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(mlt); ET.indent(tree, space='  '); tree.write(output, encoding='utf-8', xml_declaration=True)
    return {'target': 'kdenlive', 'path': str(output), 'sequence_uuid': sequence_uuid, 'tracks': len(project['tracks']), 'bin_items': len(project['bin'])}


def export_shotcut(project: dict[str, Any], output: Path) -> dict[str, Any]:
    profile = project['profile']; fps = float(profile['fps'])
    mlt = ET.Element('mlt', {
        'LC_NUMERIC': 'C', 'version': '7.0.0', 'root': '.', 'producer': 'tractor0',
        'title': 'Shotcut project generated by Story-Film Skills'
    })
    add_profile(mlt, profile)
    producer_ids: dict[str, str] = {}
    for i, item in enumerate(project['bin']):
        pid = f'producer{i}'
        producer_ids[item['clip_id']] = pid
        p = producer_for_item(mlt, item, pid, fps)
        prop(p, 'shotcut:detail', item.get('path', item.get('color', '')))
        prop(p, 'shotcut:skipConvert', 1)

    main_bin = ET.SubElement(mlt, 'playlist', {'id': 'main_bin', 'autoclose': '1'})
    prop(main_bin, 'shotcut:projectAudioChannels', int(profile.get('audio_channels', 2)))
    prop(main_bin, 'shotcut:projectFolder', 1)
    prop(main_bin, 'shotcut:projectNote', '\n'.join(project.get('notes', [])))
    prop(main_bin, 'xml_retain', 1)
    for item in project['bin']:
        ET.SubElement(main_bin, 'entry', {'producer': producer_ids[item['clip_id']]})

    background_prod = ET.SubElement(mlt, 'producer', {'id': 'black'})
    prop(background_prod, 'resource', 'black'); prop(background_prod, 'mlt_service', 'color'); prop(background_prod, 'set.test_audio', 0)
    background = ET.SubElement(mlt, 'playlist', {'id': 'background', 'autoclose': '1'})

    filter_counter = [0]
    track_playlist_ids: dict[str, str] = {}
    total_end = 0.0
    for ti, track in enumerate(project['tracks']):
        plid = f'playlist{ti}'
        track_playlist_ids[track['track_id']] = plid
        pl = ET.SubElement(mlt, 'playlist', {'id': plid, 'autoclose': '1'})
        prop(pl, 'shotcut:video' if track['type'] == 'video' else 'shotcut:audio', 1)
        prop(pl, 'shotcut:name', track.get('name', track['track_id']))
        prop(pl, 'shotcut:locked', 1 if track.get('locked') else 0)
        fill_playlist(pl, track.get('clips', []), producer_ids, fps, 'shotcut', filter_counter)
        for edit in track.get('clips', []):
            total_end = max(total_end, float(edit['timeline_start']) + float(edit['duration']))
    ET.SubElement(background, 'entry', {'producer': 'black', 'in': clock(0), 'out': clock(end_time(0, total_end or 1/fps, fps))})

    tractor = ET.SubElement(mlt, 'tractor', {'id': 'tractor0', 'in': clock(0), 'out': clock(end_time(0, total_end or 1/fps, fps)), 'global_feed': '1'})
    prop(tractor, 'shotcut', 1)
    prop(tractor, 'shotcut:projectAudioChannels', int(profile.get('audio_channels', 2)))
    prop(tractor, 'shotcut:projectFolder', 1)
    ET.SubElement(tractor, 'track', {'producer': 'background'})
    track_index = {}
    for i, track in enumerate(project['tracks'], 1):
        track_index[track['track_id']] = i
        attrs = {'producer': track_playlist_ids[track['track_id']]}
        if track.get('muted') and track['type'] == 'audio': attrs['hide'] = 'audio'
        if track.get('hidden') and track['type'] == 'video': attrs['hide'] = 'video'
        ET.SubElement(tractor, 'track', attrs)
        # Standard automatic audio summing from background to each timeline track.
        mix = ET.SubElement(tractor, 'transition', {'id': f'auto_mix_{i}'})
        prop(mix, 'a_track', 0); prop(mix, 'b_track', i); prop(mix, 'mlt_service', 'mix'); prop(mix, 'always_active', 1); prop(mix, 'sum', 1)

    for i, transition in enumerate(project.get('transitions', []), 1):
        start = float(transition.get('timeline_start', 0.0)); duration = float(transition.get('duration', 0.0))
        node = ET.SubElement(tractor, 'transition', {'id': f'user_transition_{i}', 'in': clock(start), 'out': clock(end_time(start, duration, fps))})
        prop(node, 'a_track', track_index[transition['a_track']]); prop(node, 'b_track', track_index[transition['b_track']])
        prop(node, 'mlt_service', transition['service'])
        prop(node, 'shotcut:transition', 1)
        for k, v in transition.get('properties', {}).items(): prop(node, k, v)
    for gf in project.get('global_filters', []):
        filter_counter[0] += 1
        append_filter(tractor, gf, f'filter{filter_counter[0]}', 0.0, total_end or 1/fps, fps, 'shotcut')
    if project.get('subtitle_file'):
        filter_counter[0] += 1
        sf = {'service': 'avfilter.subtitles', 'properties': {'av.filename': project['subtitle_file']}}
        append_filter(tractor, sf, f'filter{filter_counter[0]}', 0.0, total_end or 1/fps, fps, 'shotcut')

    output.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(mlt); ET.indent(tree, space='  '); tree.write(output, encoding='utf-8', xml_declaration=True)
    return {'target': 'shotcut', 'path': str(output), 'tracks': len(project['tracks']), 'bin_items': len(project['bin'])}


def validate_export(path: Path, target: str) -> list[str]:
    errors: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except Exception as exc:
        return [f'XML parse failed: {exc}']
    if root.tag != 'mlt': errors.append('root element must be mlt')
    if root.find('profile') is None: errors.append('missing profile')
    if target == 'kdenlive':
        main = root.find("playlist[@id='main_bin']")
        if main is None: errors.append('Kdenlive project missing main_bin')
        else:
            props = {x.get('name'): (x.text or '') for x in main.findall('property')}
            if props.get('kdenlive:docproperties.version') != '1.1': errors.append('Kdenlive project missing document version 1.1')
        seqs = [t for t in root.findall('tractor') if any(p.get('name') == 'kdenlive:uuid' for p in t.findall('property'))]
        if not seqs: errors.append('Kdenlive project missing sequence tractor with kdenlive:uuid')
        wrappers = [t for t in root.findall('tractor') if any(p.get('name') == 'kdenlive:projectTractor' and (p.text or '') == '1' for p in t.findall('property'))]
        if not wrappers: errors.append('Kdenlive project missing project tractor wrapper')
    elif target == 'shotcut':
        main = root.find("playlist[@id='main_bin']")
        if main is None: errors.append('Shotcut project missing main_bin')
        tractors = root.findall('tractor')
        tagged = [t for t in tractors if any(p.get('name') == 'shotcut' and (p.text or '') == '1' for p in t.findall('property'))]
        if not tagged: errors.append('Shotcut project missing shotcut=1 tractor')
        playlists = root.findall('playlist')
        if not any(any(p.get('name') == 'shotcut:name' for p in pl.findall('property')) for pl in playlists):
            errors.append('Shotcut project missing named timeline playlists')
    else:
        errors.append(f'unknown target {target}')
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description='Export canonical Badgids editorial state as Kdenlive or Shotcut project files.')
    ap.add_argument('project_dir')
    src = ap.add_mutually_exclusive_group(required=False)
    src.add_argument('--editor-project', default=None, help='Advanced editor_project.json path.')
    src.add_argument('--timeline', default=None, help='Executable timeline path to compile into an editor project.')
    ap.add_argument('--target', choices=['kdenlive', 'shotcut', 'both'], default='both')
    ap.add_argument('--output')
    ap.add_argument('--require-sources', action='store_true')
    ap.add_argument('--validate-only', action='store_true')
    ap.add_argument('--write-derived-manifest', action='store_true')
    args = ap.parse_args()
    root = project_root(args.project_dir)

    if args.editor_project:
        source = project_path(root, args.editor_project, must_exist=True)
        project = read_json(source)
    else:
        timeline_rel = args.timeline or '05_post/timeline.json'
        source = project_path(root, timeline_rel, must_exist=True)
        timeline = read_json(source)
        terr = validate_timeline(root, timeline, require_sources=args.require_sources)
        if terr:
            raise MediaRuntimeError('; '.join(terr))
        project = derive_editor_project(timeline)
        if args.write_derived_manifest:
            mp = project_path(root, '05_post/editorial/editor_project.json')
            mp.parent.mkdir(parents=True, exist_ok=True)
            mp.write_text(json.dumps(project, indent=2) + '\n', encoding='utf-8')

    errors = validate_editor_project(root, project, require_sources=args.require_sources)
    if errors:
        for e in errors: print('ERROR', e)
        return 2
    if args.validate_only:
        print('OK editor project manifest')
        return 0

    targets = ['kdenlive', 'shotcut'] if args.target == 'both' else [args.target]
    reports = []
    for target in targets:
        if args.output and len(targets) == 1:
            rel = args.output
        elif target == 'kdenlive':
            rel = '05_post/editorial/kdenlive/film_project.kdenlive'
        else:
            rel = '05_post/editorial/shotcut/film_project.mlt'
        output = project_path(root, rel)
        report = export_kdenlive(project, output) if target == 'kdenlive' else export_shotcut(project, output)
        xerr = validate_export(output, target)
        if xerr:
            raise MediaRuntimeError('; '.join(xerr))
        report['relative_path'] = rel
        reports.append(report)
    print(json.dumps({'schema_version': 1, 'exports': reports}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except MediaRuntimeError as exc:
        print(f'ERROR {exc}')
        raise SystemExit(2)
