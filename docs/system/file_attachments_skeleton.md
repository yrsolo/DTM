# File Attachments Skeleton

## Purpose

Source of truth for future task attachment support without implementing runtime code yet.

## Goal

Attach files to tasks through Object Storage and expose attachment metadata through snapshot-backed read paths.

## Non-goals

- No binary payloads in queue messages
- No OCR or LLM processing
- No immediate orphan cleanup implementation

## Target Data Model

`TaskExtra.attachments[]`

Required fields:
- `id`
- `key`
- `filename`
- `mime`
- `size`
- `uploaded_at`
- `uploaded_by`

Optional fields:
- `preview`

## Upload Flow Options

Supported future options:
1. request upload URL, then complete attach command
2. accept already-uploaded object key from trusted frontend/admin path

Preferred rollout:
- presigned upload or short-lived object upload contract
- metadata write through queued command

## Object Storage Key Scheme

Recommended prefix:
- `attachments/{env}/{task_id}/{attachment_id}-{filename}`

Do not expose raw internal storage keys in public API unless explicitly needed.

## Attach Command Contract

Future command type:
- `attach_task_file`

Worker responsibilities:
1. validate `task_id`
2. validate object key/metadata
3. update `TaskExtra.attachments`
4. trigger prep rebuild or partial refresh

## Read Path Policy

Attachment metadata may later be exposed in API payload where needed.

Binary content delivery should remain storage-backed, not embedded in snapshot payloads.

## Cleanup Placeholder

Orphan cleanup is a later CAM.

Initial policy:
- no immediate delete on detach
- prefer mark-and-sweep later

## Current Touchpoints

- [src/snapshot_engine/model.py](n:/PROJECTS/python/SCRIPT/DTM/src/snapshot_engine/model.py)
- [src/snapshot_engine/prep_builder.py](n:/PROJECTS/python/SCRIPT/DTM/src/snapshot_engine/prep_builder.py)
- [src/snapshot_engine/stores/s3_store.py](n:/PROJECTS/python/SCRIPT/DTM/src/snapshot_engine/stores/s3_store.py)

## Forbidden Shortcuts

- No file binary in queue payload
- No attachment metadata in YDB side path
- No direct mutation of prep snapshot without going through extra-store update flow
