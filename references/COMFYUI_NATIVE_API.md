# ComfyUI Native API

This reference describes the stable operating concepts Story-Film Skills uses against a running ComfyUI. Live server responses remain authoritative.

## Base URL

Default local URL:

```text
http://127.0.0.1:8188
```

The bundled client also accepts an explicit URL and environment configuration. Never hardcode a personal installation path.

ComfyUI currently exposes its main routes both without and with an `/api` prefix. The bundled client uses the traditional unprefixed routes for broad compatibility.

## Inspection

### `GET /system_stats`

Returns ComfyUI version, Python and PyTorch details, RAM, device names, VRAM totals, VRAM free values, and frontend/template package version information.

Use it to confirm that the server is ComfyUI and to assess resource state before heavy work.

### `GET /features`

Returns server feature flags. Treat fields as capability data, not a fixed schema to memorize forever.

### `GET /prompt`

Returns queue information such as `exec_info.queue_remaining`.

### `GET /object_info`

Returns the live node-class catalog. Current node definitions place input schemas under `input.required` and `input.optional`. Do not look for a top-level `inputs` object.

Each class may describe:

- required and optional inputs
- input ordering
- output types and output names
- display name
- description
- Python module
- category
- whether it is an output node
- API-node status
- experimental or deprecated status
- search aliases

This is the primary source for workflow class validation.

### `GET /object_info/{node_class}`

Returns information for one exact installed node class. Prefer this when validating a small known set.

### `GET /models`

Lists model folder categories known to the live server.

### `GET /models/{folder}`

Lists filenames visible in one model folder category. ComfyUI resolves its registered model roots before this call. This includes roots loaded from `extra_model_paths.yaml` and supported startup path configuration. Story-Film should use this server-visible list instead of scanning the filesystem or assuming model files live under the ComfyUI application directory.

## Workflow discovery

Story-Film's bundled controller uses the project's runnable workflow directory plus the user's saved ComfyUI workflows:

- `04_generation/comfyui/workflows/` - runnable project copies
- `GET /userdata?dir=workflows&recurse=true&full_info=true` - workflows saved by the ComfyUI user

`04_generation/comfyui/templates/` remains a project-owned staging/materialization area, not a discovery source. Story-Film does not query ComfyUI core/custom template catalogs for workflow selection. If the user wants a ComfyUI template, they save it into their workflow area first or export/register it as an external workflow.

Current ComfyUI deployments may expose user-data routes with or without the `/api` prefix. The bundled controller tries the compatible forms for user workflow discovery.

Use:

```text
python scripts/comfyui_control.py --project PROJECT workflow-catalog
python scripts/comfyui_control.py --project PROJECT workflow-catalog --query image
python scripts/comfyui_control.py --project PROJECT workflow-fetch --source user --name saved.json --out 04_generation/comfyui/templates/saved.json
```

Fetched sources are preserved copies. UI-format workflows must use a supported UI-to-run/conversion path such as current comfy-cli or an API export. API-format candidates are not runnable merely because their JSON shape looks correct: validate them against the live node schemas and choices first.

For a newly constructed API candidate, promote it to the runnable workflow directory only after live validation:

```text
python scripts/comfyui_control.py --project PROJECT workflow-promote \
  --candidate 04_generation/comfyui/candidate.json \
  --out 04_generation/comfyui/workflows/SHOT-001.json
```

Do not bypass this discovery/validation path with one-off `/userdata`, `/object_info`, or `/prompt` loops. Do not infer an executable node from a Story-Film prompt-adapter name.

## Inputs and outputs

### `POST /upload/image`

Multipart upload for workflow images. Typical fields are:

- `image`: file bytes
- `type`: usually `input`
- `subfolder`: optional relative subfolder
- `overwrite`: optional

The response provides the server-side name, subfolder, and type. Use those returned values in the workflow instead of guessing how the server renamed a collision.

### `POST /upload/mask`

Uploads masks using ComfyUI's mask semantics. Use only when the workflow requires a mask and the original reference is known.

### `GET /view`

Fetches generated or stored media by `filename`, `subfolder`, and `type`. History output records provide the values needed to build this request.

Do not construct arbitrary filesystem paths for `/view`.

## Queue and history

### `POST /prompt`

Submits an API-format workflow.

Minimum body:

```json
{
  "prompt": {
    "1": {
      "class_type": "SomeInstalledNode",
      "inputs": {}
    }
  }
}
```

Useful optional fields include `client_id`, a canonical UUID `prompt_id`, queue ordering fields, `partial_execution_targets`, and `extra_data`.

Successful submission returns a `prompt_id`, queue number, and `node_errors`.

Validation errors return HTTP 400 with `error` and `node_errors`. Preserve those details during troubleshooting.

### `GET /queue`

Returns `queue_running` and `queue_pending`.

### `POST /queue`

Can clear the pending queue or delete selected pending queue IDs. Treat queue clearing as destructive and require explicit user intent.

### `GET /history`

Returns recorded execution history.

### `GET /history/{prompt_id}`

Returns the authoritative history record for one prompt. Poll this for completion when live WebSocket progress is unnecessary.

### `POST /history`

Can clear history or delete selected history entries. This is destructive bookkeeping, not a generation requirement.

## Cancellation and memory

### `POST /api/jobs/{id}/cancel`

Modern ComfyUI exposes targeted atomic cancellation for a job ID. Prefer it when supported.

### `POST /interrupt`

Can interrupt the currently running prompt. Modern servers accept a `prompt_id` to target the running job. A global interrupt without an ID is broader and should not be the first choice.

### `POST /free`

Body fields:

```json
{
  "unload_models": true,
  "free_memory": false
}
```

This requests memory cleanup from the ComfyUI worker. It does not free memory owned by other processes.

## WebSocket

### `GET /ws?clientId=<id>`

Provides live status, execution, progress, preview, and related events. The server performs feature-flag negotiation and sends an initial status message.

Story-Film Skills uses polling for correctness in its dependency-free Python client. If comfy-cli, comfy-mcp, or another capable client is available, live WebSocket progress can be used as an enhancement.

## Output extraction

History output objects are node keyed. A file output can appear under keys such as images, video, videos, audio, files, 3d, or other node-defined names. Do not hardcode only `images`.

Treat any list item containing a `filename` record as a downloadable file output, except boolean or metadata-only fields. Keep the producing node ID with each output record.

Text-producing nodes may return a list under `text`; preserve these separately from file outputs.


## Mask uploads

`POST /upload/mask` is a specialized image upload used when a mask should replace the alpha channel of an existing ComfyUI image reference. It requires an `original_ref` naming the existing filename, subfolder, and type. Do not treat a mask as an arbitrary-file upload.

Bundled native command:

```text
python scripts/comfyui_control.py upload-mask MASK.png \
  --original-filename ORIGINAL.png \
  --original-type output
```

The original filename must be a plain filename. Use server-returned references rather than inventing a filesystem path.
