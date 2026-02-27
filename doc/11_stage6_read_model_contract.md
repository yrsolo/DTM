# Stage 6 Read-Model JSON Contract (v1 draft)

## Purpose
Define a canonical JSON read-model for downstream UI/API consumers without changing current production runtime behavior.

## Scope
- Producer in Stage 6: runtime artifact builder (`core/read_model.py`).
- Consumers: web UI, API adapters, review tooling.
- Source systems in current state: planner outputs, quality report summary/counters, alert evaluation artifacts.

## Contract Metadata
- `schema_version` (string, required): semantic version for contract compatibility.
- `generated_at_utc` (string, required): ISO-8601 UTC timestamp.
- `source` (object, required):
  - `mode` (string): runtime mode (`sync-only`, `timer`, `test`, `reminders-only`, ...).
  - `dry_run` (boolean): run safety mode marker.
  - `build_id` (string|null): optional run identifier.

## Top-Level Shape
```json
{
  "schema_version": "1.0.0",
  "generated_at_utc": "2026-02-27T12:00:00Z",
  "source": {
    "mode": "sync-only",
    "dry_run": true,
    "build_id": null
  },
  "board": {
    "timeline": [],
    "by_designer": []
  },
  "task_details": [],
  "alerts": [],
  "quality_summary": {}
}
```

## Entities

### `board.timeline[]`
Row-level timeline projection for date/stage-oriented views.
- `task_id` (string, required)
- `task_name` (string, required)
- `designer` (string|null)
- `brand` (string|null)
- `stage` (string|null)
- `start_date` (string|null, `YYYY-MM-DD`)
- `due_date` (string|null, `YYYY-MM-DD`)
- `status` (string|null)

### `board.by_designer[]`
Designer-centric projection for board/grouped views.
- `designer` (string, required)
- `tasks` (array, required):
  - `task_id` (string, required)
  - `task_name` (string, required)
  - `status` (string|null)
  - `due_date` (string|null, `YYYY-MM-DD`)
  - `priority` (string|null)

### `task_details[]`
Detailed task projection for drill-down panels.
- `task_id` (string, required)
- `task_name` (string, required)
- `brand` (string|null)
- `designer` (string|null)
- `status` (string|null)
- `stage` (string|null)
- `timing_raw` (string|null)
- `timing_issue` (string|null)
- `links` (object|null)

### `alerts[]`
Normalized operational alerts for UI badges and incident screens.
- `level` (string, required): `OK|INFO_ONLY|WARN|CRITICAL|UNKNOWN`
- `code` (string, required): stable alert code.
- `message` (string, required)
- `source_file` (string|null)
- `metrics` (object|null)

### `quality_summary`
Runtime quality and delivery counters consumed by dashboards.
- `task_row_issue_count` (integer)
- `people_row_issue_count` (integer)
- `timing_parse_error_count` (integer)
- `reminder_sent_count` (integer)
- `reminder_send_error_count` (integer)
- `reminder_send_retry_attempt_count` (integer)
- `reminder_send_retry_exhausted_count` (integer)
- `reminder_send_error_transient_count` (integer)
- `reminder_send_error_permanent_count` (integer)
- `reminder_send_error_unknown_count` (integer)
- `reminder_delivery_attemptable_count` (integer|null)
- `reminder_delivery_attempted_count` (integer|null)
- `reminder_delivery_rate` (number|null)
- `reminder_failure_rate` (number|null)

## Mapping Notes (Current Runtime -> Read-Model)
- `quality_summary` maps from `GoogleSheetPlanner.build_quality_report()['summary']`.
- `alerts[]` maps from alert evaluator outputs (`alert_evaluation.json` / evaluator CLI output).
- `board.*` and `task_details[]` are currently emitted as empty arrays and will be filled from planner manager projections in the next Stage 6 slices.
- Current implementation entrypoint: `core.read_model.build_read_model(quality_report, alert_evaluation, build_id=None)`.

## Versioning Policy
- Backward-compatible field additions: bump minor (`1.0.0` -> `1.1.0`).
- Breaking shape/type changes: bump major (`1.x` -> `2.0.0`).
- Patch version only for typo/description updates with no JSON shape changes.

## Validation Rules
- Unknown fields are allowed for forward compatibility.
- Required fields must always be present, even when value is `null`.
- Date strings must be normalized to `YYYY-MM-DD` where applicable.

## Smoke Coverage
- Deterministic builder contract smoke: `agent/read_model_builder_smoke.py`.
- Local launcher publication smoke: `agent/read_model_publication_smoke.py`.
- Local launcher artifact option: `local_run.py --read-model-file <path> [--read-model-build-id <id>]`.
