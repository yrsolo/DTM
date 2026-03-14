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
5. Worker writes canonical attachment metadata into the extra snapshot and rebuilds prep.

## HTTP/admin intake

Upload-contract request:
- `POST /ops/admin/task-attachments/request-upload`
- `POST /test/ops/admin/task-attachments/request-upload`

Transitional wrapper still accepted:
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

The handler validates:
- task exists in the current prep snapshot
- mime type is supported
- filename is normalized into a safe storage key

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

This compatibility endpoint only enqueues command `attach_task_file`; canonical callers should use `finalize`.

## Storage contract

Object Storage key scheme:
- `attachments/{env}/{task_id}/{attachment_id}-{filename}`

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
- future enrichment fields reserved for later waves

## Worker/job behavior

Command type:
- `attach_task_file`
- `delete_task_attachment`

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
6. revoke readability and remove metadata during delete

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

Security and visibility rules:
- only `ready` + `snapshot_visible` attachments are published into task payloads
- masked contour hides attachments entirely
- read access requires trusted ingress + authenticated + `full` + `approved`
- storage keys are intentionally not exposed through the frontend payload

## Current boundaries

Active code pointers:
- `src/entrypoints/http/admin_task_attachments_handler.py`
- `src/entrypoints/http/task_attachment_read_handler.py`
- `src/jobs/attach_task_file_job.py`
- `src/jobs/delete_task_attachment_job.py`
- `src/services/attachments/*`
- `src/snapshot_engine/engine.py`
- `src/snapshot_engine/frontend_v2_payload_builder.py`

Tests:
- `tests/api/test_command_queue_foundation.py`
- `tests/api/test_task_attachment_read_handler.py`
- `tests/jobs/test_attach_task_file_job.py`
- `tests/jobs/test_delete_task_attachment_job.py`
- `tests/snapshot_engine/test_engine_attach_metadata.py`
- `tests/snapshot_engine/test_query_engine.py`

## Guardrails

- no binary payload in queue messages
- no direct prep mutation without extra-store update
- no attachment metadata write through legacy YDB path
- no read access for non-ready, deleted, or masked attachments
