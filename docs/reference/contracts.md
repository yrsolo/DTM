# Contracts (Current)

This document defines the current runtime contracts that shape the live snapshot-first contour.
It intentionally excludes legacy database/storage schemas and historical migration contracts.

## 1) Normalized task contract

Minimum canonical task fields observed in the active runtime:
- `task_id`
- `title`
- `brand`
- `format_`
- `customer`
- `owner_id`
- `group_id`
- `raw_timing`
- `status`
- `history`
- `min_date`
- `max_date`
- `milestones`

Notes:
- `status` is the normalized workflow status derived from sheet color/text mapping.
- `history` is the raw human-facing source status/history text preserved for runtime consumers.
- task identity is snapshot-centric and stable across the active runtime contour.

## 2) Milestone contract

Milestone fields used by the active runtime:
- `idx`
- `type`
- `planned`
- `actual`
- `status`
- `raw_text`

Invariant:
- `milestones` must never be empty for a runtime task view.

## 3) Snapshot contracts

### Raw snapshot
Represents normalized sheet source state before extra metadata merge.

### Prep snapshot
Represents the canonical read-side snapshot used by:
- frontend/API reads,
- render jobs,
- reminder flows,
- group-query selection,
- attachment metadata exposure.

### Extra snapshot
Represents bulk metadata that augments raw/prep snapshots:
- attachment metadata,
- orphan flags and other auxiliary task metadata.

Attachment metadata fields:
- `attachment_id`
- `task_id`
- `filename_original`
- `filename_display`
- `mime_type`
- `kind`
- `size_bytes`
- `status`
- `storage_bucket` (internal only)
- `storage_key` (internal only; not exposed by frontend API)
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
- future enrichment fields are reserved but may be null in v1

## 4) Frontend API v2 contract

Canonical response shape remains:
- `meta`
- `filters`
- `summary`
- `entities`
- `tasks`

Current behavioral guarantees:
- filtering stays query-driven over prep snapshot,
- masking changes sensitive values but preserves payload shape,
- `milestones` remain full for selected tasks,
- ids, dates, statuses, and summary/meta structure remain stable across full/masked modes.

Attachment publication guarantees:
- `tasks[].attachments` contains only `ready` + visible attachments
- frontend DTO never exposes storage internals
- masked mode returns empty attachments arrays
- browser content access goes through trusted read routes, not direct storage keys

## 5) Hashing and freshness contracts

### Stable source hash
- built from stable JSON over sheet values/colors
- used to decide whether snapshot rebuild is necessary

### Content-level task hashing
- must include milestone timing fields
- must not let cosmetic-only markers redefine task identity

## 6) Runtime mode contract view

See `docs/reference/runtime-modes.md` for current supported modes and transport mapping.

## Archive pointer

Legacy YDB/readmodel table contracts are not part of the current runtime story.
If historical schema detail is needed, use:
- `archive/docs/system_legacy/ydb_schema.md`

