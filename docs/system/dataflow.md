# Dataflow, Hashing, Versioning (Current)

Canonical path: Sheets -> normalize -> Raw snapshot (S3) -> Prep snapshot (S3) -> API v2/query consumers.

## 1) Snapshot inputs
Source snapshot is read from Sheets range `A1:Z2000` and includes:
- `values`
- `colors`

Hash basis is stable JSON over `{values, colors}`.

## 2) Canonical timer runtime
Runtime object:
- `src/services/timer_pipeline.py` -> `TimerPipeline(AppContext)`
- `TimerPipeline.run(RunRequest(...))` invokes `SnapshotEngine.update(...)`

Execution order:
1. fetch sheet snapshot
2. compute source hash
3. compare with previous raw snapshot hash
4. on change (or force): write Raw -> build Prep -> write Prep
5. on no-change: skip writes

No YDB operational/readmodel writes are part of the canonical API v2 runtime path.

People routing snapshot:
- timer update also refreshes people snapshot from sheet `Люди` into S3.
- notify uses people snapshot as canonical source for `chat_id` and `vacation`.

## Render v2 safety and target policy
- `render_v2` reads only snapshot prep data.
- `render_v2` target worksheet is `task_calendar` (human name: `Задачи`).
- `render_v2` must never write to `tasks` (`ТАБЛИЧКА`) source sheet.
- Unsafe target is blocked at runtime with `error.code=render_target_unsafe`.

## 3) Query runtime
- API handler: `src/entrypoints/http/frontend_v2_handler.py`
- Query engine: `src/snapshot_engine/query_engine.py`
- Source: `PrepSnapshot` from S3

Payload contract remains API v2 compatible (including `history`, `brand`, `format_`, `customer`).

## 4) Status semantics
- `status`: normalized color-derived status (`work|pre_done|wait|done|unknown`)
- `history`: raw textual status from source sheet

## 5) Group query runtime
`src/entrypoints/http/group_query_handler.py` reads active tasks from snapshot-backed API payload and builds Telegram replies from that data.

## 6) Reminder parity runtime
- reminder modes (`reminder_v2`, `reminders-only`, `morning`, `test`) use `src/notify/*` parity contour.
- candidate designers are selected only from tasks with milestones on:
  - today,
  - next workday (weekend-aware).
- message flow:
  1) draft by formatter
  2) optional LLM enhancement
  3) fallback to draft on empty/error
  4) Telegram delivery with retries/backoff/classified counters
- in `env=test` all reminder sends are forced to test chat routing.
