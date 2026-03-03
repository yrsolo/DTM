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

### `dtm_sync_state`
- Primary key: `source_id` (`Utf8`).
- Columns:
  - `source_id` `Utf8`
  - `source_hash` `Utf8`
  - `synced_at_utc` `Timestamp`
  - `last_success_at_utc` `Timestamp`
  - `last_error` `Utf8?`

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
- Sync hash gate uses source-range values hash (`source_hash` in `dtm_sync_state`).
- Readmodel build loads operational data in batched reads (tasks + milestones).
- API v2 in YDB mode reads readmodel snapshot row (`dtm_readmodel_frontend_v2`) and returns payload.
