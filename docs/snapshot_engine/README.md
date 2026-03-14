# Snapshot Engine

Snapshot Engine is the canonical read-side runtime contour.

Current data path:
1. fetch Sheets snapshot (`values + colors`)
2. normalize into `RawSnapshot`
3. merge extra metadata into `PrepSnapshot`
4. write raw/prep/extra objects to Object Storage
5. serve query/render/notify flows from prep snapshot

Key invariants:
- `status` is normalized from source color/text rules
- `history` preserves source human-facing status/history text
- `task_id` stays the canonical runtime identifier

Current environment isolation:
- `snapshots/test/...`
- `snapshots/prod/...`

Current doc set:
- `docs/snapshot_engine/architecture.md`
- `docs/snapshot_engine/api_v2_parity.md`

Historical cutover/migration material is archive-only and not part of the current runtime story.
