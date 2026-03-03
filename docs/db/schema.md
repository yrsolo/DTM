# DTM YDB Schema (Operational + Readmodel)

## Purpose
- Keep normalized operational data in relational tables.
- Keep API v2 response as a single readmodel snapshot row.
- Minimize runtime queries and avoid N+1 patterns.

## Tables

### `dtm_tasks`
- Primary key: `task_id` (`Utf8`).
- Columns:
  - `task_id` `Utf8`
  - `title` `Utf8`
  - `brand` `Utf8`
  - `format_` `Utf8`
  - `customer` `Utf8`
  - `raw_timing` `Utf8`
  - `owner_id` `Utf8`
  - `group_id` `Utf8`
  - `status` `Utf8`
  - `start_date` `Date?`
  - `end_date` `Date?`
  - `next_due_date` `Date?`
  - `tags_json` `Utf8`
  - `links_json` `Utf8`
  - `task_hash` `Utf8?`
  - `task_revision` `Uint64`
  - `raw_payload` `Utf8`
  - `updated_at_utc` `Timestamp`

### `dtm_task_milestones`
- Primary key: `(task_id, idx)`.
- Columns:
  - `task_id` `Utf8`
  - `idx` `Uint32`
  - `type` `Utf8`
  - `planned_date` `Date?`
  - `actual_date` `Date?`
  - `status` `Utf8`
  - `raw_text` `Utf8?`
  - `confidence` `Double`
  - `inference_rule` `Utf8?`

Compatibility role:
- Legacy/current snapshot table kept for compatibility during migration.
- Must not be used as source of truth for version-bound readmodel once `dtm_task_milestones_v` path is enabled.
- Sync safety rule: bulk updates must delete only affected `task_id` scopes; full-table delete is forbidden.

### `dtm_task_milestones_v`
- Primary key: `(task_id, version, idx)`.
- Columns:
  - `task_id` `Utf8`
  - `version` `Uint64`
  - `idx` `Uint32`
  - `type` `Utf8`
  - `planned_date` `Date?`
  - `actual_date` `Date?`
  - `status` `Utf8`
  - `raw_text` `Utf8?`
  - `confidence` `Double`
  - `inference_rule` `Utf8?`

### `dtm_sync_state`
- Primary key: `source_id` (`Utf8`).
- Columns:
  - `source_id` `Utf8`
  - `preflight_hash_50` `Utf8`
  - `source_hash_full` `Utf8`
  - `synced_at_utc` `Timestamp`
  - `last_full_sync_at` `Timestamp?`
  - `last_success_at_utc` `Timestamp`
  - `last_error` `Utf8?`
  - `last_error_code` `Utf8?`
  - `last_error_at_utc` `Timestamp?`

### `dtm_task_versions`
- Primary key: `(task_id, version)`.
- Columns:
  - `task_id` `Utf8`
  - `version` `Uint64`
  - `status` `Utf8` (`active|archive`)
  - `content_hash` `Utf8`
  - `payload_json` `Utf8`
  - `created_at_utc` `Timestamp`

## Version Truth Rule
- Active version of a task is `dtm_tasks.task_revision` (exposed by adapter as both `task_revision` and `current_version`).
- Readmodel milestone join contract (target state): load milestones by `(task_id, current_version)` from `dtm_task_milestones_v`.

### `dtm_readmodel_frontend_v2`
- Primary key: `readmodel_id` (`Utf8`).
- Default row id: `frontend_v2:default`.
- Columns:
  - `readmodel_id` `Utf8`
  - `contract_version` `Utf8`
  - `payload_json` `Utf8`
  - `payload_hash` `Utf8`
  - `built_from_source_hash` `Utf8`
  - `generated_at_utc` `Timestamp`

## Query Policy
- Sync gate uses two hashes:
  - `preflight_hash_50` for top-50 source rows (values+colors),
  - `source_hash_full` for full source-range (values+colors).
- Full sync is required daily (24h) even when preflight is unchanged.
- Readmodel build loads operational data in batched reads (tasks + milestones).
- API v2 in YDB mode reads readmodel snapshot row (`dtm_readmodel_frontend_v2`) and returns payload.
- Versioning rule:
  - content changes create new version rows in `dtm_task_versions`,
  - color/status-only changes do not increment version.
