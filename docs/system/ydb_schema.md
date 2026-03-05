# YDB schema (Current)

Source of truth: `src/adapters/ydb/schema.py` (DDL) and repos in `src/adapters/ydb/*`.

Default table names:
- `dtm_tasks`
- `dtm_task_milestones` (legacy/current milestones table; may be disabled by `WRITE_LEGACY_MILESTONES=0`)
- `dtm_task_milestones_v` (versioned milestones; canonical for readmodel)
- `dtm_task_versions`
- `dtm_sync_state`
- `dtm_readmodel_frontend_v2`

## dtm_tasks
Primary key: `(task_id)`

Columns:
- task_id Utf8
- title Utf8
- brand Utf8
- format_ Utf8
- customer Utf8
- raw_timing Utf8
- owner_id Utf8
- group_id Utf8
- status Utf8
- start_date Date
- end_date Date
- next_due_date Date
- tags_json Utf8
- links_json Utf8
- task_hash Utf8
- task_revision Uint64
- history Utf8
- raw_payload Utf8
- updated_at_utc Timestamp

Meaning: head row (latest canonical state + current revision).
`history` is the raw textual status trail from source column `Статус` and is the canonical source for API `tasks[].history`.

## dtm_task_versions
Primary key: `(task_id, version)`

Columns:
- task_id Utf8
- version Uint64
- status Utf8   (active/archive marker; secondary to dtm_tasks.task_revision)
- content_hash Utf8
- payload_json Utf8
- created_at_utc Timestamp

Meaning: immutable version records (history).

## dtm_task_milestones_v
Primary key: `(task_id, version, idx)`

Columns:
- task_id Utf8
- version Uint64
- idx Uint32
- type Utf8
- planned_date Date
- actual_date Date
- status Utf8
- raw_text Utf8
- confidence Double
- inference_rule Utf8

Meaning: milestones for a specific task revision.

## dtm_task_milestones (legacy/current)
Primary key: `(task_id, idx)`

Same column set as milestones_v but without `version`.

Meaning: optional compat/current table. Should not be used for readmodel when milestones_v is available.

## dtm_sync_state
Primary key: `(source_id)`

Columns:
- source_id Utf8
- preflight_hash_50 Utf8
- source_hash_full Utf8
- synced_at_utc Timestamp
- last_full_sync_at Timestamp
- last_success_at_utc Timestamp
- last_error Utf8
- last_error_code Utf8
- last_error_at_utc Timestamp

Meaning: hash gate cursor and operational telemetry.

## dtm_readmodel_frontend_v2
Primary key: `(readmodel_id)`

Columns:
- readmodel_id Utf8
- contract_version Utf8
- payload_json Utf8
- payload_hash Utf8
- built_from_source_hash Utf8
- generated_at_utc Timestamp

Meaning: single-row snapshot for API v2/consumers.
