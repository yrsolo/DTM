# CAM-CORE-CLEANUP-V1 Evidence

## Trust Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `core/*`, `main.py`, `index.py` | 2026-03-04 | TeamLead agent | direct code scan (`rg`, file reads) | high | boundaries and import hotspots verified against runtime entrypoints |
| `docs/system/core_boundaries.md` | 2026-03-04 | TeamLead agent | updated with atomic move map | high | used as source for P01-T002 decomposition |
| `core/repository.py`, `src/adapters/google_sheets/task_repository.py`, `src/app/planner_bootstrap.py` | 2026-03-04 | TeamLead agent | direct code scan + compile/test smoke | high | extraction step P03-T001 validated with compatibility shim and bootstrap import switch |
| `core/repository.py`, `core/api_payload.py`, `core/group_query.py`, `src/adapters/google_sheets/task_repository.py` | 2026-03-04 | TeamLead agent | direct code scan (`rg`, file reads) | high | confirms current `Task` import graph before P03-T002 extraction |
| `core/people.py`, `core/models/people.py`, `src/adapters/google_sheets/people_manager.py`, `src/app/planner_bootstrap.py` | 2026-03-04 | TeamLead agent | direct code scan + compile/import smoke | high | verifies people manager extraction and compatibility shim behavior |
| `core/planner.py` | 2026-03-04 | TeamLead agent | direct code scan + compile smoke | high | confirms removal of `utils.service.GoogleSheetInfo` dependency with local sheet-info view |
| `core/reminder.py`, `core/reminder_policy.py`, `src/adapters/llm_openai.py`, `src/adapters/llm_google.py`, `src/adapters/llm_yandex.py`, `src/adapters/telegram.py` | 2026-03-04 | TeamLead agent | direct code scan + compile smoke + targeted runtime smoke | high | reminder transport and error-policy extraction validated without behavior changes in covered smoke paths |
| `core/manager.py`, `src/app/planner_bootstrap.py`, `tests/core/test_manager_calendar_empty.py` | 2026-03-04 | TeamLead agent | direct code scan (`rg`, file reads) | high | import graph and calendar manager usage verified before P06-T002 extraction |
| `core/manager.py`, `src/services/calendar_runtime.py`, `src/app/planner_bootstrap.py` | 2026-03-04 | TeamLead agent | direct code scan + compile/test smoke | high | confirms calendar runtime extraction with core shim compatibility and bootstrap import switch |
| `core/manager.py`, `src/services/render/task_table_runtime.py`, `src/app/planner_bootstrap.py` | 2026-03-04 | TeamLead agent | direct code scan + compile/test smoke | high | confirms TaskManager extraction with core shim compatibility and bootstrap import switch |
| `core/planner.py`, `src/services/planner_runtime.py`, `main.py` | 2026-03-04 | TeamLead agent | direct code scan + compile/test smoke | high | confirms planner orchestration extraction with core compatibility shim and main import switch |
| `core/task_timing_processor.py`, `core/manager.py`, `src/app/planner_bootstrap.py`, `docs/system/modules/core_shim_deprecation_checklist.md` | 2026-03-04 | TeamLead agent | direct code scan + compile/test smoke + full import audit | high | confirms removal of non-legacy shim imports and documents remaining legacy-only shim usage |

## Execution Log
- P01-T001 completed: core inventory and domain/infra split documented.
- P01-T002 completed: first atomic move map documented with concrete source/destination pairs.
- P02-T001 started: implementation moved out of `core/bootstrap.py` and `core/use_cases.py` into `src/app/planner_bootstrap.py` and `src/services/usecases/planner_runtime.py`, with compatibility shims preserved.
- P02-T002 completed: `TimingParser` extracted into `core/timing_parser.py`; `core/manager.py` now imports parser directly from this domain module instead of `core/repository.py`.
- P02-T003 completed: `core/repository.py` switched to `from core.timing_parser import TimingParser`; duplicate parser implementation removed.
- P02-T004 completed: repository IO extraction steps documented in `docs/system/modules/repository_extraction_plan.md`.
- P03-T001 completed: `GoogleSheetsTaskRepository` moved to `src/adapters/google_sheets/task_repository.py`; `core/repository.py` now re-exports adapter implementation as compatibility shim; `src/app/planner_bootstrap.py` switched to adapter import.
- P03-T002 completed: `Task` model moved to `core/models/task.py`; `core/repository.py` now hosts `TaskRepository` contract + compatibility re-exports; core consumers switched to direct `core.models.task` imports.
- P03-T003 completed: non-legacy imports switched off `core.repository` shims (`tests/core/test_timing_year_modes.py`, `src/adapters/google_sheets/task_repository.py`); explicit `core.task_repository_contract` introduced to avoid adapter->shim dependency.
- P04-T001 completed: infra import audit refreshed and recorded in `docs/system/core_boundaries.md`, with ordered extraction candidates.
- P04-T002 completed: sheet-loading `PeopleManager` moved to `src/adapters/google_sheets/people_manager.py`; `core/people.py` converted to compatibility shim; payload/bootstrap imports switched to direct modules.
- P04-T003 completed: `core/planner.py` no longer imports `utils.service.GoogleSheetInfo`; local `_SheetInfoView` preserves required read-only behavior for planner attributes.
- P05-T001 completed: reminder transport extraction plan documented in `docs/system/modules/reminder_transport_extraction_plan.md`.
- P05-T002 completed: pure reminder policy helpers extracted into `core/reminder_policy.py`; `core/reminder.py` wired to new policy module.
- P05-T003 completed: transport classes moved out of `core/reminder.py` into `src/adapters/llm_openai.py`, `src/adapters/llm_google.py`, `src/adapters/llm_yandex.py`, `src/adapters/telegram.py`; core keeps compatibility imports.
- P05-T004 completed: adapter SDK imports switched to lazy import pattern to avoid import-time failures in flows that do not use optional providers.
- P06-T001 completed: manager extraction plan documented in `docs/system/modules/manager_extraction_plan.md`.
- P06-T002 completed: `CalendarManager` and `TaskCalendarManager` moved to `src/services/calendar_runtime.py`; `core/manager.py` now re-exports them as compatibility shim; `src/app/planner_bootstrap.py` switched to direct service imports.
- P06-T003 completed: `TaskManager` moved to `src/services/render/task_table_runtime.py`; `core/manager.py` reduced to `TaskTimingProcessor` + compatibility re-exports.
- P07-T001 completed: planner extraction plan documented in `docs/system/modules/planner_extraction_plan.md`.
- P07-T002 completed: `GoogleSheetPlanner` implementation moved to `src/services/planner_runtime.py`; `core/planner.py` converted to compatibility shim; `main.py` switched to direct service import.
- P07-T003 completed: shim usage audit documented in `docs/system/modules/core_shim_deprecation_checklist.md`; active runtime/test/agent imports migrated to `src/services/*`.
- P07-T004 completed: `TaskTimingProcessor` moved to `core/task_timing_processor.py`; `src/app/planner_bootstrap.py` switched to direct import.
- P07-T005 completed: owner decision received — keep `old/*` and notebooks untouched; keep compatibility re-exports for legacy-only imports.
- P08-T001 completed: active-path import audit confirms zero `core.repository/core.people/core.planner/core.manager` imports outside legacy contour.

## Validation
- `python -m py_compile src/app/planner_bootstrap.py src/services/usecases/planner_runtime.py core/bootstrap.py core/use_cases.py main.py index.py`
- `python -m unittest tests.services.test_pipeline_runtime -v`
- `python -m py_compile core/timing_parser.py core/manager.py`
- `python -m py_compile core/timing_parser.py core/repository.py core/manager.py main.py index.py`
- `python -m py_compile core/repository.py src/adapters/google_sheets/task_repository.py src/app/planner_bootstrap.py`
- `python -m unittest tests.core.test_timing_year_modes -v`
- `python -m unittest tests.services.test_pipeline_runtime -v`
- `python -m py_compile core/models/task.py core/models/__init__.py core/repository.py src/adapters/google_sheets/task_repository.py core/api_payload.py core/group_query.py`
- `python -m unittest tests.core.test_timing_year_modes -v`
- `python -m unittest tests.services.test_pipeline_runtime -v`
- `python -m py_compile core/task_repository_contract.py core/repository.py core/models/task.py src/adapters/google_sheets/task_repository.py tests/core/test_timing_year_modes.py core/api_payload.py core/group_query.py`
- `python -m unittest tests.core.test_timing_year_modes -v`
- `python -m unittest tests.services.test_pipeline_runtime -v`
- `python -m py_compile core/models/people.py src/adapters/google_sheets/people_manager.py core/people.py src/app/planner_bootstrap.py core/api_payload.py core/api_payload_v2.py src/adapters/google_sheets/__init__.py`
- `python -m py_compile core/planner.py core/people.py core/models/people.py src/adapters/google_sheets/people_manager.py`
- `python -m unittest tests.core.test_timing_year_modes tests.services.test_pipeline_runtime -v`
- `python -m unittest tests.api.test_frontend_api_routing tests.api.test_frontend_api_v2_payload -v` (partial signal: environment missing `httpx`; v2 snapshot mismatch observed on milestone type labels and `nextDue`, pre-existing scope not modified in this wave)
- `python -m py_compile core/reminder.py core/reminder_policy.py src/adapters/telegram.py`
- `python -m py_compile core/reminder.py core/reminder_policy.py src/adapters/telegram.py src/adapters/llm_openai.py src/adapters/llm_google.py src/adapters/llm_yandex.py`
- `python -m py_compile src/adapters/llm_openai.py src/adapters/llm_google.py src/adapters/llm_yandex.py src/adapters/telegram.py core/reminder.py`
- `python -m unittest tests.services.test_pipeline_runtime tests.core.test_timing_year_modes -v`
- `python -m unittest tests.api.test_frontend_api_routing -v` (imports now pass optional LLM/TG deps gate; failures indicate missing `index.build_operational_store` test expectation mismatch, outside current core-cleanup scope)
- `rg -n "\bfrom (openai|telegram|google|ydb)|\bimport (openai|telegram|google|ydb|httpx|aiohttp)|from utils\.service" core` (only optional imports remain in `core/reminder_policy.py`)
- `python -m py_compile core/manager.py src/services/calendar_runtime.py src/app/planner_bootstrap.py`
- `python -m unittest tests.core.test_manager_calendar_empty tests.services.test_pipeline_runtime tests.core.test_timing_year_modes -v`
- `python -m py_compile core/manager.py src/services/calendar_runtime.py src/services/render/task_table_runtime.py src/app/planner_bootstrap.py`
- `python -m unittest tests.core.test_manager_calendar_empty tests.services.test_pipeline_runtime tests.core.test_timing_year_modes -v`
- `python -m py_compile core/planner.py src/services/planner_runtime.py main.py index.py`
- `python -m unittest tests.services.test_pipeline_runtime tests.core.test_manager_calendar_empty tests.core.test_timing_year_modes -v`
- `python -m py_compile agent/render_adapter_smoke.py agent/reminder_enhancer_counters_smoke.py agent/reminder_sli_summary_smoke.py tests/core/test_manager_calendar_empty.py core/manager.py src/services/planner_runtime.py src/services/render/task_table_runtime.py src/services/calendar_runtime.py`
- `python -m py_compile core/task_timing_processor.py core/manager.py src/app/planner_bootstrap.py src/services/planner_runtime.py`
- `python -m unittest tests.core.test_manager_calendar_empty tests.services.test_pipeline_runtime tests.core.test_timing_year_modes -v`
- `rg -n "from core\\.(repository|people|planner|manager) import|import core\\.(repository|people|planner|manager)" .` (remaining usages only in old contour + notebook)
- `rg -n "from core\\.(repository|people|planner|manager) import|import core\\.(repository|people|planner|manager)" src core tests main.py index.py agent` (no matches)

## Notes
- Local environment in this shell misses some optional runtime deps (`httpx`), so full import smoke of legacy bootstrap path was not executed.
- Compatibility shims are intentionally preserved to keep old imports stable while migration continues.
- During extraction, adapter runtime import was adjusted to avoid hard dependency on Google SDK during unit-test imports (`TYPE_CHECKING` guarded type imports from `utils.service`).
- API v2 snapshot tests currently show milestone label/hash diffs not introduced by this extraction wave; treated as separate verification stream.
- Blocked-state escalation executed: `agent/notify_owner.py --mode blocked ...` sent successfully in Russian with decision options.
- Owner decision applied: legacy contour remains supported through shim re-exports; active contour remains direct-import only.
