# CAM-FILE-ATTACHMENTS-V1

## Goal

Add task attachments through Object Storage and snapshot-backed metadata without introducing binary payloads into queue messages.

## Scope

- attachment metadata model in task extras
- object storage key policy
- attach command contract
- prep refresh strategy
- API exposure policy for metadata

## Non-goals

- no OCR or LLM processing
- no immediate orphan cleanup engine
- no binary-in-queue payloads

## Implementation Skeleton Reference

- Primary implementation skeleton: `docs/system/file_attachments_skeleton.md`
- Current trust level: medium
- Current touchpoints:
  - `src/snapshot_engine/model.py`
  - `src/snapshot_engine/prep_builder.py`
  - `src/snapshot_engine/stores/s3_store.py`
- Depends on: `CAM-QUEUE-FOUNDATION-ON-CF-V1`
- Forbidden shortcuts:
  - no binary file blobs in queue messages
  - no direct prep mutation bypassing extra-store flow

## Phases

1. metadata schema
2. upload contract
3. attach command flow
4. prep refresh integration
5. metadata read exposure

## DoD

- attachment metadata is modeled and persisted cleanly
- queue command updates metadata without moving binary through runtime
- snapshot-backed read path can expose metadata where needed
