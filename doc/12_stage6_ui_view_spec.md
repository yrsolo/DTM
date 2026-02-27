# Stage 6 UI View-Spec Baseline (Read-Model Driven)

## Purpose
Define a baseline UI specification over Stage 6 read-model payload to align frontend scope before implementation.

## Inputs
- Read-model contract: `doc/11_stage6_read_model_contract.md`.
- Target architecture direction: `doc/04_target_architecture.md`.

## Main Views

### 1) Board Timeline View
Goal: show date/stage progression of tasks across designers and brands.
- Data source: `board.timeline[]`.
- Required fields:
  - `task_id`, `task_name`, `designer`, `brand`, `stage`, `start_date`, `due_date`, `status`.
- Interactions:
  - sort by `due_date`,
  - quick filter by `designer` and `brand`,
  - status color markers (`status` -> UI color mapping).

### 2) Designer Board View
Goal: grouped view by designer for daily/weekly planning.
- Data source: `board.by_designer[]`.
- Required fields:
  - `designer`,
  - `tasks[].task_id`, `tasks[].task_name`, `tasks[].status`, `tasks[].due_date`, `tasks[].priority`.
- Interactions:
  - collapse/expand per designer,
  - overdue highlighting based on `due_date`,
  - status chips from `status`.

### 3) Task Detail Panel
Goal: drill-down context for selected task.
- Data source: `task_details[]`.
- Required fields:
  - `task_id`, `task_name`, `brand`, `designer`, `status`, `stage`, `timing_raw`, `timing_issue`, `links`.
- Interactions:
  - open from Timeline/Designer views,
  - display timing parsing diagnostics when `timing_issue != null`.

### 4) Alerts & Quality Sidebar
Goal: operational context near planning views.
- Data source:
  - `alerts[]` (`level`, `code`, `message`, `source_file`, `metrics`),
  - `quality_summary` (row issues, timing errors, reminder delivery counters/rates).
- Interactions:
  - severity filtering (`OK|INFO_ONLY|WARN|CRITICAL|UNKNOWN`),
  - clickable source link when `source_file` is present.

## Global Filters
- `designer` (single/multi select),
- `brand` (single/multi select),
- `status` (multi select),
- `date_range` (from/to over `start_date` / `due_date`).

Filter contract:
- Filters are client-side over read-model payload in Stage 6 baseline.
- Server/API filtering can be added later without breaking UI semantics.

## History Baseline
Stage 6 baseline history is lightweight:
- Source: `source.generated_at_utc`, `source.build_id`, plus alerts/quality snapshots from artifact file history.
- UI requirement:
  - show latest snapshot metadata,
  - provide list of available artifact files (if present in local storage).

## Non-Functional Notes
- UI must tolerate empty arrays for `board.timeline`, `board.by_designer`, and `task_details` (current Stage 6 partial builder state).
- Missing optional fields must not crash rendering.
- Schema compatibility guard is expected via `validate_read_model_contract`.

## Out of Scope (Stage 6)
- Live API/WebSocket transport.
- Inline editing/workflow mutations.
- Full audit log with per-field diffs.
