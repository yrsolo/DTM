# File Attachments (Current)

This document describes the active task-attachment contour.

## Purpose

Task attachments are stored as binary objects in Object Storage, while attachment metadata is stored in the snapshot extra-store and exposed through snapshot-backed read paths.

## Current flow

The active upload flow is two-step:

1. Request an upload contract from the admin HTTP path.
2. Upload the binary directly to Object Storage using the returned presigned URL.
3. Enqueue metadata attachment through the command queue.
4. Worker writes attachment metadata into the extra snapshot and rebuilds prep.

## HTTP/admin intake

Upload-contract request:
- `POST /admin/attachments/request-upload`

Required request body:
- `task_id`
- `filename`
- `mime`
- `size`

Response artifact:
- `attachment_upload_request`

Returned fields:
- `task_id`
- `attachment_id`
- `key`
- `filename`
- `mime`
- `size`
- `expiresIn`
- `method`
- `uploadUrl`
- `headers`

The handler validates that the task exists in the current prep snapshot before issuing a presigned upload URL.

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

This endpoint only enqueues command `attach_task_file`; it does not mutate snapshot state inline.

## Storage contract

Object Storage key scheme:
- `attachments/{env}/{task_id}/{attachment_id}-{filename}`

Binary payloads:
- are uploaded directly to Object Storage
- are never placed into queue payloads
- are never embedded into snapshots

Attachment metadata is persisted in the extra snapshot under:
- `snapshots/{env}/extra/default.json`

## Worker/job behavior

Command type:
- `attach_task_file`

Runtime path:
- `AdminQueueHandler` requests upload contract or enqueues attach command
- `Worker` dispatches command to `AttachTaskFileJob`
- `AttachTaskFileJob` calls `SnapshotEngine.attach_file_metadata(...)`
- `SnapshotEngine` updates bulk extra snapshot and rebuilds prep from current raw snapshot

Worker responsibilities:
1. validate required metadata
2. validate referenced task exists in current raw snapshot
3. append/replace attachment metadata in task extra record
4. persist bulk extra snapshot
5. rebuild and write prep snapshot

## Read path behavior

Frontend API v2 exposes attachment metadata through:
- `tasks[].attachments`

Exposed fields:
- `id`
- `filename`
- `mime`
- `size`
- `uploadedAt`
- `uploadedBy`
- `preview`

Storage keys are intentionally not exposed through the public frontend payload.

## Current boundaries

Active code pointers:
- `src/entrypoints/http/admin_queue_handler.py`
- `src/jobs/attach_task_file_job.py`
- `src/snapshot_engine/engine.py`
- `src/snapshot_engine/frontend_v2_payload_builder.py`

Tests:
- `tests/api/test_command_queue_foundation.py`
- `tests/jobs/test_attach_task_file_job.py`
- `tests/snapshot_engine/test_engine_attach_metadata.py`
- `tests/snapshot_engine/test_query_engine.py`

## Guardrails

- no binary payload in queue messages
- no direct prep mutation without extra-store update
- no attachment metadata write through legacy YDB path
