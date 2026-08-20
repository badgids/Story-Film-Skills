# Comfy API v2 and comfy-api-proxy

`comfy-api-proxy` exposes the official Comfy API v2 contract in front of a self-hosted ComfyUI. Story-Film installs the proxy into its separate managed official control environment and can start/stop it on loopback through the Pi-native `story_comfy` tool when v2 semantics are needed.

A normal local ComfyUI operation does not require the proxy to be running. Automatic proxy startup does not enable model-directory placement and does not install models or custom nodes.

## Why v2 matters

The v2 contract provides a uniform external-application model across supported surfaces:

- durable jobs
- poll-first status
- explicit cancellation
- UUID assets
- content-addressed deduplication
- resumable retrieval through job and asset IDs
- API-format workflow submission

The current self-hosted proxy defaults to ComfyUI at `127.0.0.1:8188` and serves the v2 API separately, commonly on `127.0.0.1:8189`.

## Jobs

### `POST /api/v2/jobs`

Submits an API-format workflow under `workflow`. UI-format JSON is rejected.

Optional `extra_data` can carry the Comfy partner-node API key. Do not persist or print it.

Use an idempotency key when a caller may retry an ambiguous submission. Do not reuse one key for a different intended job.

### `GET /api/v2/jobs/{id}`

This is the polling source of truth for state, progress, and outputs.

### `POST /api/v2/jobs/{id}/cancel`

Cancels the selected job.

### Events

SSE events are a live enhancement. Polling remains authoritative and works without a persistent event stream.

## Assets

### `POST /api/v2/assets`

Multipart asset upload includes:

- file bytes
- content type
- file path
- optional expected blake3 hash
- optional tags

The server computes the trusted hash. A client-provided hash is only a verification value.

### `GET /api/v2/assets/{id}`

Returns asset metadata.

### `GET /api/v2/assets/{id}/content`

Returns or redirects to asset bytes and supports range requests on compatible surfaces.

## Model-file safety in the self-hosted proxy

Direct placement into ComfyUI model directories is available only when the proxy is co-located with ComfyUI and configured with its base directory. The proxy deliberately constrains this path.

Story-Film Skills follows the same safety intent:

- do not place arbitrary executable content in model folders
- do not use model upload as a path to `custom_nodes` or config files
- prevent traversal outside the intended model root
- avoid silent overwrite
- prefer safetensors for direct model placement

## Network safety

The proxy defaults to loopback. Exposing it beyond loopback should use authentication and explicit CORS/origin configuration. Never widen a local generation control service to a network interface merely because an agent could not connect through the default address.

## Choosing native API versus v2

Use native ComfyUI API when operating one known ComfyUI directly and the job does not need v2 asset semantics.

Use v2 when:

- the user selected comfy-api-proxy or Comfy Cloud
- the application is intentionally written against the v2 contract
- durable asset IDs or uniform cloud/local integration are useful

Do not run a proxy just to submit one ordinary local API workflow.
