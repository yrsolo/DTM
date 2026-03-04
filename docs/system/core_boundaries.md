# Core Boundaries (Current)

This document tracks what is domain-pure vs infrastructure-coupled inside `core/`.

## Rule
`core/` should contain:
- domain models/contracts,
- pure business rules and normalization,
- query/projection logic without IO.

`core/` should not contain:
- SDK clients (Google/YDB/Telegram/OpenAI),
- network calls,
- env/config wiring.

## Inventory snapshot (2026-03-04)

### Domain-lean modules (good candidates to keep in core)
- `core/contracts.py`
- `core/models/task.py`
- `core/errors.py`
- `core/task_repository_contract.py`
- `core/task_query_contract.py`
- `core/task_query_adapter.py`
- `core/api_payload_v2.py`
- `core/read_model.py`
- `core/group_query.py`
- `core/timing_parser.py`

### Infra-coupled modules (migration candidates out of core)
- `core/bootstrap.py` (config/env + adapter composition + external clients)
- `core/repository.py` (compatibility shim; should eventually stop re-exporting infra adapters)
- `core/people.py` (compatibility shim; should eventually stop re-exporting infra adapters)
- `core/reminder.py` (reminder orchestration + delivery policy wiring; transports moved to adapters)
- `core/planner.py` (runtime orchestration + dependency access)
- `core/manager.py` (partially extracted; write-path manager still coupled to renderer/service)

### Transitional / mixed
- `core/sheet_renderer.py` (adapter protocol boundary; keep or move depends on final module map)
- `core/use_cases.py` (application orchestration, candidate for `src/services/usecases/`)

## First extraction targets (low-risk)
1. Move composition/bootstrap concerns from `core/bootstrap.py` to `src/app/bootstrap.py`.
2. Move runtime orchestration from `core/use_cases.py` towards `src/services/usecases/`.
3. Keep domain-only contracts in `core/*` with zero SDK imports.

## Atomic move map (P01-T002)
| From | To | Method | Runtime risk |
|---|---|---|---|
| `core/bootstrap.py` | `src/app/planner_bootstrap.py` | move implementation, keep compatibility shim in `core/bootstrap.py` | low |
| `core/use_cases.py` | `src/services/usecases/planner_runtime.py` | move implementation, keep compatibility shim in `core/use_cases.py` | low |
| `main.py` imports from `core/*` | `main.py` imports from `src/app` and `src/services/usecases` | direct import swap after shim is in place | low |
| `index.py` imports from `core/bootstrap.py` | `index.py` imports from `src/app/planner_bootstrap.py` | direct import swap after shim is in place | low |

## Completed in CAM-CORE-CLEANUP-V1 (current wave)
- `core/bootstrap.py` converted to compatibility shim; implementation moved to `src/app/planner_bootstrap.py`.
- `core/use_cases.py` converted to compatibility shim; implementation moved to `src/services/usecases/planner_runtime.py`.
- `TimingParser` extracted to `core/timing_parser.py` and de-duplicated from `core/repository.py`.
- `GoogleSheetsTaskRepository` moved to `src/adapters/google_sheets/task_repository.py`; `core/repository.py` keeps compatibility re-export.
- `Task` model moved to `core/models/task.py`; non-legacy imports switched to direct module paths.
- `TaskRepository` contract moved to `core/task_repository_contract.py`; adapter no longer depends on `core.repository` contract shim.
- `Person/Designer` moved to `core/models/people.py`; `PeopleManager` moved to `src/adapters/google_sheets/people_manager.py`; `core/people.py` keeps compatibility re-export.
- `core/planner.py` no longer imports `utils.service.GoogleSheetInfo`; internal `_SheetInfoView` used for read-only sheet metadata.
- LLM and Telegram transport classes moved from `core/reminder.py` to `src/adapters/llm_*.py` and `src/adapters/telegram.py`.
- Reminder error-classification policies moved to `core/reminder_policy.py`; `core/reminder.py` now has no direct SDK imports.
- `CalendarManager` and `TaskCalendarManager` moved to `src/services/calendar_runtime.py`; `core/manager.py` keeps compatibility re-export.
- Legacy frontend v1 payload serializer `core/api_payload.py` removed from active tree; HTTP runtime uses `core/api_payload_v2.py`.

## Next extraction candidates (ordered)
1. `core/manager.py`: move remaining `TaskManager` write-path to `src/services/render/*` and keep core as thin shim.
2. `core/planner.py`: move remaining runtime orchestration into `src/services/*` and keep core as thin compatibility shim.
3. `core/repository.py` and `core/people.py`: remove final compatibility re-exports after consumer migration is complete.

## Legacy policy (owner decision, 2026-03-04)
- `old/*` and notebooks are kept untouched.
- Compatibility shims in `core/*` are preserved for legacy-only imports.
- Active contour (`src/*`, `main.py`, `index.py`, `tests/*`, `agent/*`) must continue using direct non-shim imports.
