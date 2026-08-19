# MLT Toolkit Contract

MLT is the timeline and service-graph framework used for editable multimedia compositions and as the common interchange foundation for Kdenlive and Shotcut projects.

## Runtime truth

MLT installations differ by version and compiled modules. Do not assume a producer, consumer, filter, transition, link, profile, or preset exists.

Discover the local runtime when `melt` is installed:

```bash
python scripts/media_toolkit.py discover --project PROJECT --deep
python scripts/media_toolkit.py query melt --category producers
python scripts/media_toolkit.py query melt --category consumers
python scripts/media_toolkit.py query melt --category filters
python scripts/media_toolkit.py query melt --category transitions
python scripts/media_toolkit.py query melt --category links
python scripts/media_toolkit.py query melt --category profiles
```

For a specific service, use MLT's query mechanism through the bridge:

```bash
python scripts/media_toolkit.py query melt --name SERVICE_NAME
```

## MLT model

Treat an MLT composition as an explicit service graph:

1. producers and chains create media frames;
2. playlists arrange producer cuts and blanks;
3. multitracks or tractors combine tracks;
4. filters modify services;
5. transitions combine tracks over time;
6. links implement time-affecting processing where available;
7. consumers render, display, serialize, stream, or otherwise consume the result.

MLT XML is the portable serialization form. The current MLT DTD permits `profile`, `producer`, `playlist`, `tractor`, `multitrack`, `consumer`, and `chain` at the document level, with filters, transitions, properties, entries, blanks, tracks, and links attached in their defined locations.

## Operations the skill may perform

When the installed runtime supports them, use MLT for:

- multitrack timeline composition
- trim and playlist editing
- blank/gap placement
- filters and keyframed properties
- transitions and compositions
- audio and video track visibility
- nested MLT XML compositions
- profile selection and frame-rate handling
- preview and playback through consumers
- headless rendering
- XML serialization and deserialization
- project graph inspection
- producer, filter, transition, link, profile, preset, and consumer discovery
- MLT-compatible project interchange

Do not hardcode a service name for a runtime that has not been queried when the service is optional or version-dependent.

## MLT XML rules

For hand-authored or generated XML:

- keep resources project-relative when the project should be portable;
- define unique media producers once where practical;
- keep source in/out on playlist entries rather than unnecessarily restricting master producers;
- place tracks in explicit playlists/tractors;
- preserve declared filter and transition service names and properties without inventing undocumented parameters;
- represent timeline gaps with `<blank>` rather than fake black media unless a true black background is intended;
- keep frame rate and aspect data in the `<profile>`;
- parse generated XML before reporting success;
- when `melt` is installed, optionally load or render the XML for a stronger integration check.

## Raw operation

For an MLT operation not covered by a higher-level exporter:

```bash
python scripts/media_toolkit.py run melt -- INPUT.mlt -consumer avformat:OUTPUT.mp4
```

The bridge does not use a shell.

## Relationship to editor projects

Generic MLT XML is not automatically a complete editor-native project.

- Kdenlive adds `kdenlive:` project metadata and a Generation 5 sequence/bin structure.
- Shotcut adds `shotcut:` project properties to the MLT service graph.

Use `editor-project-export` when the user asks for an editable Kdenlive or Shotcut project. Use `mlt-export` only when generic MLT interchange is sufficient.
