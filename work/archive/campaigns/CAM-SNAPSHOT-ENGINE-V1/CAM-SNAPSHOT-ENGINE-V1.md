# CAM-SNAPSHOT-ENGINE-V1 — Hard Cutover with S3 Snapshot Engine

## Goal
Replace YDB readmodel runtime path with JSON snapshots in Object Storage:
Sheets -> Normalize -> Raw(S3) -> Merge Extra(S3) -> Prep(S3) -> QueryEngine -> API/Notify.

## Scope
- Introduce `src/snapshot_engine/*` canonical runtime module.
- Add S3-backed stores for Raw/Prep/Extra.
- Switch timer pipeline update path to SnapshotEngine update job.
- Switch API v2/group-query runtime reads to SnapshotEngine prep snapshot.

## Non-goals
- Legacy/planner tree deletion.
- API v2 contract changes.
- Color parsing cleanup campaign.

## DoD
- Runtime read path for API v2 and group query does not depend on YDB readmodel.
- Timer pipeline writes S3 snapshots via UpdateJob.
- `status` and `history` semantics are preserved.
- Target tests/smokes are green.
