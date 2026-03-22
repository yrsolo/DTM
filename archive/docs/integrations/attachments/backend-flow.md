# File Attachments (Current)

This document describes the active task-attachment contour.

## Purpose

Task attachments are stored as binary objects in Object Storage, while canonical attachment metadata is stored in the snapshot extra-store and exposed through snapshot-backed read paths.

## Current flow

The canonical upload flow is:

1. Request an upload contract from the attachment admin HTTP path.
2. Upload the binary directly to Object Storage using the returned presigned URL.
3. Finalize the uploaded object; backend verifies object existence, size, and mime.
4. Finalize enqueues metadata attachment through the command queue.
5. Worker writes canonical attachment metadata into the extra snapshot, rebuilds the primary task-list read-model, and best-effort invalidates exact default frontend response cache entries.

## HTTP/admin intake

Upload-contract request:
- `POST /ops/admin/task-attachments/request-upload`
- `POST /test/ops/admin/task-attachments/request-upload`

Legacy ingress alias still accepted:
- `POST /admin/attachments/request-upload`

Required request body:
- `task_id`
- `filename`
- `mime`
- `size`
- `uploaded_by`

Response artifact:
- `attachment_upload_request`

Returned fields:
- `task_id`
- `attachment_id`
- `key`
- `filename`
- `mime`
- `size`
- `kind`
- `expiresIn`
- `method`
- `uploadUrl`
- `headers`
- `diagnostics`

`diagnostics` is additive debug metadata for browser upload troubleshooting:
- `uploadContractVersion`
- `signedMethod`
- `signedContentType`
- `requiredHeaders`
- `uploadUrlScheme`
- `uploadUrlHost`
- `uploadUrlPath`
- `expiresAtUtc`
- `browserMayRequirePreflight`
- `notes`

The handler validates:
- task exists in the current prep snapshot
- mime type is supported
- filename is normalized into a safe storage key

Current supported upload mime types:
- `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (`.docx`)
- `application/msword` (`.doc`)
- `application/pdf` (`.pdf`)
- `image/jpeg` (`.jpg`, `.jpeg`)
- `image/png` (`.png`)
- `image/webp` (`.webp`)

Current direct-upload contract details:
- backend signs exact `PUT`
- backend signs exact `Content-Type`
- browser caller must use the returned `uploadUrl` as-is
- browser `PUT` may require successful `OPTIONS`/CORS handling on the storage ingress before the actual upload

`request-upload` error responses are JSON and now include structured `error.details` for frontend diagnostics:
- `artifact=attachment_upload_request_error`
- `step=request-upload`
- `reason=<machine-readable reason>`
- input echoes such as `task_id`, `filename`, `mime`, `size`
- `uploaded_by_present`
- `field` for missing required input when applicable

Finalize request:
- `POST /ops/admin/task-attachments/finalize`
- `POST /test/ops/admin/task-attachments/finalize`

Required request body:
- `task_id`
- `attachment_id`
- `uploaded_by`

Behavior:
- verifies uploaded object with `head_object`
- enforces size/mime consistency
- records `uploaded_unverified`
- enqueues `attach_task_file`

Delete request:
- `POST /ops/admin/task-attachments/delete`
- `POST /test/ops/admin/task-attachments/delete`

Required request body:
- `task_id`
- `attachment_id`
- `deleted_by`

Metadata attach enqueue:
- `POST /admin/commands/attach-task-file`

Required request body:
- `task_id`
- `key`
- `filename`
- `mime`
- `size`
- `uploaded_by`

Optional request body:
- `attachment_id`
- `preview`

This legacy enqueue endpoint only enqueues command `attach_task_file`; canonical callers should use `finalize`.

Hidden cleanup enqueue:
- `POST /admin/commands/cleanup-task-attachments`

Request body:
- `ttl_seconds` (optional, default `86400`)

Behavior:
- enqueues `cleanup_task_attachments`
- scans bulk attachment metadata for stale `pending_upload`, `uploaded_unverified`, and `deleted` records
- best-effort deletes the underlying storage object when `storage_key` is present
- removes stale metadata and rebuilds prep once if anything changed

## Storage contract

Object Storage key scheme:
- `attachments/{env}/{task_id}/{attachment_id}-{filename}`

Derived preview key scheme (legacy `.doc` only):
- `attachments/{env}/{task_id}/{attachment_id}/preview.pdf`

Binary payloads:
- are uploaded directly to Object Storage
- are never placed into queue payloads
- are never embedded into snapshots

Attachment metadata is persisted in the extra snapshot under:
- `snapshots/{env}/extra/default.json`

Canonical metadata model includes:
- `attachment_id`
- `task_id`
- `filename_original`
- `filename_display`
- `mime_type`
- `kind`
- `size_bytes`
- `status`
- `storage_bucket` (internal only)
- `storage_key` (internal only)
- `storage_etag`
- `storage_version`
- `uploaded_by_user_id`
- `uploaded_at`
- `verified_at`
- `deleted_at`
- `deleted_by_user_id`
- `error_code`
- `error_message`
- `snapshot_visible`
- `preview_capabilities`
- `preview_state` (`none | pending | ready | failed`)
- `derived_preview_ref` (preview object key when ready)
- future enrichment fields reserved for later waves

## Worker/job behavior

Command type:
- `attach_task_file`
- `delete_task_attachment`
- `cleanup_task_attachments`
- `generate_attachment_preview` (legacy `.doc` PDF preview)

Runtime path:
- `AdminTaskAttachmentsHandler` serves canonical request-upload/finalize/delete routes
- `Worker` dispatches command to `AttachTaskFileJob`
- `Worker` dispatches delete mutations to `DeleteTaskAttachmentJob`
- `AttachTaskFileJob` calls `SnapshotEngine.attach_file_metadata(...)`
- `SnapshotEngine` updates bulk extra snapshot and rebuilds prep from current raw snapshot

Worker responsibilities:
1. validate required metadata
2. verify object before attach publication
3. append/replace attachment metadata in task extra record
4. persist bulk extra snapshot
5. rebuild and write prep snapshot
6. best-effort invalidate exact default frontend response cache entries after successful attach/delete mutation
7. revoke readability and remove metadata during delete
8. remove stale non-ready/deleted metadata during cleanup with one bulk prep rebuild
9. for legacy `.doc`, enqueue `generate_attachment_preview` after successful attach

Legacy `.doc` preview job:
- converts `.doc` to PDF via external converter (source_url -> target_url)
- writes preview object to derived preview key
- updates `preview_state` and `derived_preview_ref`
- does not affect original `.doc` download path

## Read path behavior

Frontend API v2 exposes attachment metadata through:
- `tasks[].attachments`

Exposed fields:
- `id`
- `name`
- `mime`
- `kind`
- `sizeBytes`
- `status`
- `uploadedAt`
- `capabilities`
- `meta.preview` when present
- `links.view`
- `links.download`

Read routes:
- `GET /ops/api/task-attachments/{attachment_id}/view`
- `GET /ops/api/task-attachments/{attachment_id}/download`
- same routes under `/test`

Legacy `.doc` split semantics:
- `download` always returns the original `.doc` object
- `view` returns the derived PDF preview only
- if preview is still generating: `409` with `attachment_preview_pending`
- if preview failed/unavailable: `503` with `attachment_preview_unavailable`

Security and visibility rules:
- only `ready` + `snapshot_visible` attachments are published into task payloads
- masked contour hides attachments entirely
- read access requires trusted ingress + authenticated + `full` + `approved`
- storage keys are intentionally not exposed through the frontend payload
- successful attach/delete mutation also clears exact default frontend response cache variants (`api|bff` x `masked|full`) so the next default frontend hit is rebuilt from the fresh primary task-list payload

## Lifecycle and cleanup policy

Active lifecycle states:
- `pending_upload`
- `uploaded_unverified`
- `ready`
- `delete_pending`
- `deleted`
- `failed`

Publication rules:
- only `ready` + `snapshot_visible=true` attachments are published into task payloads
- masked contour hides attachments entirely
- `deleted`, `pending_upload`, `uploaded_unverified`, and `failed` attachments are never frontend-visible

Cleanup v1 policy:
- stale `pending_upload` older than 24h -> orphan candidate
- stale `uploaded_unverified` older than 24h -> orphan candidate
- stale `deleted` older than 24h -> final cleanup candidate
- `ready` records are never touched by cleanup
- `delete_pending` younger than TTL is never touched by cleanup
- transient storage-delete failure keeps metadata and records a warning

Reference timestamps:
- `pending_upload` -> `uploaded_at_utc`
- `uploaded_unverified` -> `verified_at_utc`, fallback `uploaded_at_utc`
- `deleted` -> `deleted_at_utc`

Cleanup carrier:
- no separate attachment table/store in v1
- stale cleanup scans the existing bulk extra snapshot only

## `/info` attachment harness

Backend-owned operator harness is exposed through:
- `/ops/info`
- `/test/ops/info`

Detail payload now includes additive block:
- `attachmentsHarness`

Current fields:
- `enabled`
- `probeTaskId`
- `probeTaskExpectedStatus`
- `probeTaskAvailable`
- `probeTaskStatus`
- `probeAttachmentsTotal`
- `probeAttachments`
- `allowedMimeTypes`
- `browserRoutes`
- `backendRoutes`
- `authFacadeRequired`
- `notes`

Purpose:
- verify the full attachment contour from an operator-controlled page
- use one reserved real probe task instead of arbitrary task input
- surface step-by-step diagnostics for upload/finalize/job/read/delete operations
- provide backend-owned manual proof that the current `test` contour works independently of the product frontend UI

Reserved probe task contract:
- task id comes from runtime config:
  - `runtime.api.attachment_harness_probe_task_id`
- expected source status comes from:
  - `runtime.api.attachment_harness_probe_task_status`
- current default values:
  - `attachment_harness_probe_task_id = "1111111111"`
  - `attachment_harness_probe_task_status = "test"`

Important:
- the probe task must exist in the real source data and current prep snapshot
- backend does not add synthetic-task bypass for harness use
- harness publication check is backend-owned:
  - `/info` detail payload reports `probeAttachments` for the reserved task
- this avoids depending on normal frontend query defaults, which do not have to include the `test` status

Harness flow in `/info`:
1. request upload contract through browser-safe auth facade route
2. upload binary directly to Object Storage using returned `uploadUrl`
3. finalize through auth facade
4. poll queued job until terminal state
5. reload `/info` detail payload and inspect `probeAttachments`
6. test `view` / `download`
7. delete attachment and verify disappearance again

Current operator affordances in `/info`:
- step-by-step harness log
- current probe-task attachment cards
- direct `Open file`
- direct `Download file`
- direct `Delete file`
- explicit after-attach vs after-delete visibility checks

Current `/info` harness uses browser-facing auth facade routes only for:
- `/ops/auth/attachments/request-upload`
- `/ops/auth/attachments/finalize`
- `/ops/auth/attachments/delete`
- `/ops/auth/attachments/jobs/{job_id}`
- `/ops/auth/attachments/{attachment_id}/view`
- `/ops/auth/attachments/{attachment_id}/download`

Same namespace is expected under `/test/ops/auth/attachments/*` for the `test` contour.

Operational rule:
- if `/test/ops/info` succeeds for the same environment and auth facade, backend attachment runtime should be considered verified
- subsequent failures in product UI are then most likely in frontend/auth integration, not in the core attachment pipeline itself

Direct binary upload remains outside auth facade:
- browser uses returned Object Storage `uploadUrl` directly
- auth facade must not proxy the binary upload stream

## Operator smoke runbook

Minimal manual smoke on `test`:
1. `POST /test/ops/admin/task-attachments/request-upload`
2. direct `PUT` to returned `uploadUrl`
3. `POST /test/ops/admin/task-attachments/finalize`
4. wait for worker and confirm attachment appears in trusted `GET /test/ops/api/v2/frontend`
5. confirm masked `GET /test/ops/api/v2/frontend` hides attachments
6. `GET /test/ops/api/task-attachments/{attachment_id}/view` -> expect `302`
7. `GET /test/ops/api/task-attachments/{attachment_id}/download` -> expect `302`
8. `POST /test/ops/admin/task-attachments/delete`
9. wait for worker and confirm attachment no longer appears in trusted frontend payload

Expected statuses:
- `request-upload` -> `200`
- direct Object Storage `PUT` -> `200`
- `finalize` -> `202`
- `delete` -> `202`
- `view` / `download` for trusted full approved access -> `302`

Contour note:
- `test` live smoke is verified against deployed runtime
- `prod` smoke requires running the manual release workflow first because push to `main` does not deploy the function by itself

## Current boundaries

Active code pointers:
- `src/entrypoints/http/admin_task_attachments_handler.py`
- `src/contexts/access_api/internal/task_attachment_read_api.py`
- `src/contexts/attachments/public.py`
- `src/contexts/attachments/internal/job_runners.py`
- `src/contexts/attachments/internal/preview_job.py`
- `src/contexts/attachments/contracts/*`
- `src/contexts/snapshot/internal/attachment_mutations.py`
- `src/contexts/snapshot/internal/engine/query_engine.py`

Tests:
- `tests/entrypoints/http/test_command_queue_foundation.py`
- `tests/contexts/access_api/test_task_attachment_read_api.py`
- `tests/contexts/attachments/test_attach_task_file_job.py`
- `tests/contexts/attachments/test_delete_task_attachment_job.py`
- `tests/contexts/snapshot/test_engine_attach_metadata.py`
- `tests/contexts/snapshot/test_query_engine.py`

## Guardrails

- no binary payload in queue messages
- no direct prep mutation without extra-store update
- no attachment metadata write through retired database migration paths
- no read access for non-ready, deleted, or masked attachments
