# DTM-29 - Stage 3 close-out: TaskManager renderer adapter unification

## Context
- `DTM-25..DTM-28` moved calendar/task-calendar rendering behind `SheetRenderAdapter` and shared `RenderCell` helpers.
- `TaskManager.task_to_table` still writes directly through `repository.service` (`clear_cells`, `update_cell`, `execute_updates`).
- Jira issue: `DTM-29` (status: `V rabote`).

## Goal
- Unify remaining TaskManager write-path behind `SheetRenderAdapter`.
- Keep output parity for sheet `designers` while reducing direct service coupling.

## Non-goals
- No visual redesign for `designers` sheet.
- No changes to reminder pipeline.
- No deep `GoogleSheetsService` refactor.

## Plan
1. Add renderer injection/default adapter for TaskManager.
2. Replace direct write calls with adapter API (`begin`, `clear_cells`, `update_cell`, `execute_updates`).
3. Normalize TaskManager payload creation via `RenderCell` helper methods.
4. Run smoke checks and sync Jira/sprint/docs lifecycle.

## Checklist (DoD)
- [x] TaskManager does not call direct write methods on `repository.service`.
- [x] Adapter boundary and shared render contract used for designers sheet payloads.
- [x] Smoke checks pass (`py_compile`, `local_run.py --mode sync-only --dry-run`, adapter smoke script).
- [x] Jira/sprint/docs synchronized.

## Work log
- 2026-02-27: Task created in Jira (`DTM-29`) and moved to `V rabote`.
- 2026-02-27: `TaskManager` migrated to `SheetRenderAdapter` boundary with `RenderCell` helper builders and timestamp write through adapter.
- 2026-02-27: Bootstrap DI updated with dedicated `designers_renderer` and TaskManager renderer injection.
- 2026-02-27: Smoke passed: `python -m py_compile core/manager.py core/bootstrap.py core/sheet_renderer.py core/adapters.py core/render_contracts.py`, `python agent/render_adapter_smoke.py`, `.venv\\Scripts\\python.exe local_run.py --mode sync-only --dry-run`.

## Links
- `core/manager.py`
- `core/bootstrap.py`
- `core/sheet_renderer.py`
- `agile/sprint_current.md`
