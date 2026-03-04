# CAM-CONFIG-REFORM-V0 Evidence

## Trust Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `docs/system/config.md`, `docs/system/architecture.md`, `work/roadmap/campaigns/priorities.md` | 2026-03-03 | TeamLead agent | direct read of current docs + priority queue | high | campaign priority and target contour confirmed |
| `config/constants.py`, `index.py`, `main.py`, `src/adapters/ydb/client.py` | 2026-03-03 | TeamLead agent | code scan (`rg`) for env/constants coupling and runtime entrypoints | high | current state has strong env/constants coupling; refactor needed |
| `src/services/planner_runtime.py`, `core/planner.py`, `main.py` | 2026-03-04 | TeamLead agent | direct code scan + compile/test smoke | high | confirms planner runtime no longer needs direct `config.SOURCE_SHEET_INFO` import when dependencies already provide source sheet context |
| `index.py`, `main.py`, `src/app/planner_bootstrap.py`, `src/services/calendar_runtime.py`, adapters` | 2026-03-04 | TeamLead agent | code scan (`rg`) for remaining direct config imports in active contour | high | migration checklist built with ordered safe path for cfg-driven wiring |
| `src/app/planner_bootstrap.py`, `main.py`, `index.py` | 2026-03-04 | TeamLead agent | direct code scan + compile/test smoke | high | first cfg-driven wiring slice applied for planner bootstrap and main runtime source policy inputs |
| `index.py`, `main.py` | 2026-03-04 | TeamLead agent | direct code scan + compile/test smoke | high | non-secret runtime toggles in entrypoints now sourced from `APP_CONTEXT.cfg` instead of direct config globals |
| `src/app/planner_bootstrap.py`, `src/services/planner_runtime.py`, `main.py`, `index.py` | 2026-03-04 | TeamLead agent | `py_compile` + targeted unit smoke after cfg wiring cleanup | high | planner bootstrap non-secret defaults now sourced from cfg object; runtime path remains green |
| `src/services/calendar_runtime.py`, `src/app/planner_bootstrap.py`, `core/timing_parser.py`, `core/task_timing_processor.py`, `src/adapters/google_sheets/task_repository.py`, `core/reminder.py` | 2026-03-04 | TeamLead agent | direct code edits + compile/test smoke + import scan | high | removed active non-secret config reads from services/core timing path; core reminder stale config import dropped |
| `src/adapters/telegram.py`, `index.py`, `src/adapters/google_sheets/task_repository.py`, `src/adapters/google_sheets/people_manager.py`, `src/app/planner_bootstrap.py` | 2026-03-04 | TeamLead agent | direct code edits + compile/test smoke + import scan | high | adapter config imports reduced to entrypoint/bootstrap boundary; legacy bootstrap shim compatibility preserved |
| `work/roadmap/campaigns/priorities.md`, `docs/system/entrypoints_index_main.md`, `docs/system/module_map.md`, `docs/system/config.md` | 2026-03-04 | TeamLead agent | owner instruction in chat + docs update pass | high | API v1 support discontinued; active documentation switched to API v2-only maintenance policy |
| `src/adapters/ydb/client.py`, `src/adapters/store_ydb.py`, `tests/services/test_ydb_backoff.py`, `tests/adapters/test_json_store_adapter.py` | 2026-03-04 | TeamLead agent | adapter refactor + compile + targeted unit tests + import scan | high | YDB adapters no longer import `config.constants`; credentials/backoff are explicit parameters at adapter boundary |
| `index.py`, `tests/api/test_frontend_api_routing.py` | 2026-03-04 | TeamLead agent | runtime routing change + unit smoke | high | API v1 routes now explicitly return `410 api_v1_discontinued`; API v2 remains active and tested |
| `config/constants.py`, `src/config/loader.py`, `docs/system/config.md` | 2026-03-04 | TeamLead agent | config contour cleanup + compile/test smoke | high | legacy API default-version knob removed from active config contour for v2-only runtime policy |
| `index.py`, `tests/api/test_frontend_api_routing.py`, `tests.services/*`, `tests.adapters/*` | 2026-03-04 | TeamLead agent | dead-code cleanup + extended smoke pack | high | removed unused API v1 doc builders from runtime entrypoint; verified no regressions in API/core/services/adapters smoke contour |
| `docs/system/entrypoints_index_main.md` | 2026-03-04 | TeamLead agent | documentation sync pass | high | entrypoint behavior doc now explicitly states runtime `410 api_v1_discontinued` response for API v1 paths |
| `src/entrypoints/http/frontend_v2_docs.py`, `index.py`, `tests/api/test_frontend_api_routing.py` | 2026-03-04 | TeamLead agent | extraction refactor + compile + routing smoke | high | API v2 doc builders moved out of index entrypoint into dedicated HTTP module without behavior change |
| `src/entrypoints/http/frontend_v2_handler.py`, `index.py`, `tests/api/test_frontend_api_routing.py`, `tests.services/*`, `tests.adapters/*` | 2026-03-04 | TeamLead agent | handler extraction refactor + full smoke pack | high | API v2 handler moved out of index into dedicated HTTP module; index now delegates with explicit boundary wiring |
| `src/entrypoints/http/frontend_compat_handlers.py`, `index.py`, `tests/api/test_frontend_api_routing.py`, `tests.services/*`, `tests.adapters/*` | 2026-03-04 | TeamLead agent | compatibility handler extraction + full smoke pack | high | API root/v1-discontinued HTTP handlers moved out of index into dedicated module; index delegation contour reduced further |
| `main.py`, `index.py`, `src/services/pipeline_runtime.py`, `src/entrypoints/jobs/db_migrate_job.py`, `src/adapters/ydb/{operational_repo,readmodel_repo,task_repository}.py`, `src/entrypoints/http/frontend_v2_handler.py` | 2026-03-04 | TeamLead agent | boundary credential propagation refactor + full smoke pack | high | explicit YDB SA credential wiring restored from entrypoints/services into adapters after removing adapter-level config constants imports |
| `src/entrypoints/http/group_query_handler.py`, `index.py`, `tests/api/test_frontend_api_routing.py`, `tests.services/*`, `tests.adapters/*` | 2026-03-04 | TeamLead agent | group-query handler extraction + full smoke pack | high | group-query branch moved out of index entrypoint into dedicated HTTP module; index delegates with injected boundaries |
| `src/entrypoints/http/frontend_query_params.py`, `index.py`, `tests/api/test_frontend_api_routing.py`, `tests.services/*`, `tests.adapters/*` | 2026-03-04 | TeamLead agent | query parser extraction + full smoke pack | high | frontend API query parsing helpers moved out of index entrypoint into dedicated HTTP module; behavior retained |
| `src/entrypoints/http/runtime_mode.py`, `index.py`, `tests/api/test_frontend_api_routing.py`, `tests.services/*`, `tests.adapters/*` | 2026-03-04 | TeamLead agent | runtime mode helper extraction + full smoke pack | high | trigger/mode/force-refresh extraction moved out of index into dedicated HTTP module; behavior retained |
| `src/entrypoints/http/response_utils.py`, `index.py`, `tests/api/test_frontend_api_routing.py`, `tests.services/*`, `tests.adapters/*` | 2026-03-04 | TeamLead agent | response/path helper extraction + full smoke pack | high | JSON/HTML/error/path helpers moved out of index into dedicated HTTP module; behavior retained |
| `src/entrypoints/http/frontend_tasks_loader.py`, `index.py`, `tests/api/test_frontend_api_routing.py`, `tests.services/*`, `tests.adapters/*` | 2026-03-04 | TeamLead agent | frontend task loader extraction + full smoke pack | high | frontend API task source selection/loading moved out of index into dedicated HTTP module; behavior retained |
| `src/entrypoints/http/debug_utils.py`, `index.py`, `tests/api/test_frontend_api_routing.py`, `tests.services/*`, `tests.adapters/*` | 2026-03-04 | TeamLead agent | debug helper extraction + full smoke pack | high | HTTP debug event-shape logger moved out of index into dedicated module; behavior retained |
| `src/entrypoints/http/frontend_v2_handler.py`, `tests/api/test_frontend_api_routing.py`, `docs/system/{entrypoints_index_main,module_map}.md` | 2026-03-04 | TeamLead agent | compatibility rollback fix + smoke/docs sync | high | API v1 compatibility restored by mapping supported v1 routes to v2 handlers; docs/tests aligned with alias policy |
| `src/entrypoints/http/frontend_v2_handler.py`, `tests/api/test_frontend_api_routing.py` | 2026-03-04 | TeamLead agent | v2 availability hotfix + regression smoke | high | API v2 no longer hard-fails when YDB readmodel path is unavailable; runtime falls back to legacy data source and returns payload |
| `src/entrypoints/http/group_query_tasks_loader.py`, `index.py`, `tests/api/test_frontend_api_routing.py`, `tests.services/*`, `tests.adapters/*` | 2026-03-04 | TeamLead agent | group-query task loader extraction + full smoke pack | high | group-query task loading moved out of index into dedicated HTTP helper module; behavior retained |
| `index.py`, `src/entrypoints/http/group_query_handler.py`, `src/entrypoints/http/group_query_tasks_loader.py`, `tests/api/test_frontend_api_routing.py`, `tests.services/*`, `tests.adapters/*` | 2026-03-04 | TeamLead agent | group-query wrapper removal + full smoke pack | high | index group-query wrapper removed; handler now delegates directly with injected boundaries in-place; behavior retained |
| `index.py`, `src/entrypoints/http/router.py`, `src/entrypoints/http/frontend_v2_handler.py`, `tests/api/test_frontend_api_routing.py`, `tests.services/*`, `tests.adapters/*` | 2026-03-04 | TeamLead agent | HTTP dispatch chain simplification + full smoke pack | high | removed redundant legacy `v1_discontinued` handler from HTTP dispatch chain; v1 compatibility remains via v2 alias routes |
| `src/entrypoints/http/http_dispatch_chain.py`, `index.py`, `tests/api/test_frontend_api_routing.py`, `tests.services/*`, `tests.adapters/*` | 2026-03-04 | TeamLead agent | dispatch-chain wiring extraction + full smoke pack | high | root/v2 HTTP handler wiring moved out of index into dedicated dispatch-chain builder; behavior retained |
| `src/entrypoints/http/runtime_execution.py`, `index.py`, `tests/api/test_frontend_api_routing.py`, `tests.services/*`, `tests.adapters/*` | 2026-03-04 | TeamLead agent | runtime execution extraction + full smoke pack | high | runtime main invocation and error handling moved out of index into dedicated helper; behavior retained |
| `docs/system/entrypoints_index_main.md`, `docs/system/module_map.md`, `index.py`, `src/entrypoints/http/*` | 2026-03-04 | TeamLead agent | docs sync pass against current code contour | high | system docs now reflect thinned index orchestration role and extracted HTTP module boundaries |
| `src/entrypoints/http/frontend_compat_handlers.py`, `index.py`, `tests/api/test_frontend_api_routing.py`, `tests.services/*`, `tests.adapters/*` | 2026-03-04 | TeamLead agent | dead compatibility code cleanup + full smoke pack | high | removed unused `v1_discontinued` compatibility handler code after switching to v1->v2 alias policy |
| `src/entrypoints/jobs/source_snapshot_reader.py`, `main.py`, `index.py`, `tests/api/test_frontend_api_routing.py`, `tests.services/*`, `tests.adapters/*` | 2026-03-04 | TeamLead agent | main snapshot helper extraction + full smoke pack | high | source snapshot (values/colors/range) IO helpers moved out of main entrypoint into dedicated jobs module; behavior retained |
| `index.py`, `src/entrypoints/http/frontend_v2_handler.py`, `tests/api/test_frontend_api_routing.py`, `tests.services/*`, `tests.adapters/*` | 2026-03-04 | TeamLead agent | HTTP error-boundary hardening + full smoke pack | high | unhandled HTTP runtime exceptions now produce structured API `503` responses (`http_dispatch_failed` / `frontend_source_unavailable`) instead of gateway-level `502` |

## Execution Log
- CAM-CONFIG-REFORM-V0 activated in `work/now/campaign.md`.
- P01 task list initialized in `work/now/tasks.md`.
- Owner rule acknowledged: no commits before YAML transfer scope review.
- CFG-P02-T001 completed: removed direct `config.SOURCE_SHEET_INFO` dependency from `src/services/planner_runtime.py`; source sheet info now derived from injected dependencies (with safe fallback).
- CFG-P02-T002 completed: created config import migration checklist (`docs/system/modules/config_import_migration_checklist.md`) with active contour inventory and ordered implementation steps.
- CFG-P02-T003 completed: `build_planner_dependencies(..., cfg=...)` added; `main.py` now reads non-secret runtime toggles (triggers/source modes/runtime env/store mode) from `APP_CONTEXT.cfg` instead of direct config globals.
- CFG-P02-T004 completed: `index.py` moved non-secret runtime toggles (`debug_http_event`, `triggers`, `frontend_api_default_version`) to `APP_CFG`.
- CFG-P02-T005 completed: `src/app/planner_bootstrap.py` now resolves non-secret LLM/runtime defaults from `cfg` (with `load_config()` fallback), keeping only secret/deployment constants in direct config imports.
- CFG-P02-T006 completed: `src/services/calendar_runtime.py` no longer imports `config.COLORS`; palette is now injectable and wired from `cfg.mapping.palette` in planner bootstrap.
- CFG-P02-T007 completed: `core/timing_parser.py` no longer reads `TIMING_YEAR_MODE` from config; mode now defaults locally and is injected from cfg via planner bootstrap into repository/timing processor.
- CFG-P02-T008 completed: removed stale `from config import DEFAULT_CHAT_ID, TG` import from `core/reminder.py` (unused after adapter/token injection path).
- CFG-P02-T009 completed: `src/adapters/telegram.py` no longer imports config defaults; token/chat id are passed explicitly from entrypoint wiring (`index.py`) and bootstrap flows.
- CFG-P02-T010 completed: Google Sheets adapters (`task_repository`, `people_manager`) moved off direct `config` imports; mappings/status aliases now come from cfg-backed constructor inputs (with loader fallback).
- CFG-P02-T011 completed: restored backward compatibility for legacy shim path by reintroducing planner bootstrap mutable knobs consumed by `core/bootstrap.py`.
- CFG-P02-T012 completed: owner decision recorded in active docs - API v1 support discontinued; v2-only maintenance policy documented across system and campaign docs.
- CFG-P02-T013 completed: removed direct `config.constants` imports from `src/adapters/ydb/client.py` and `src/adapters/store_ydb.py`; switched to explicit constructor parameters for credentials/backoff policy.
- CFG-P02-T014 completed: updated adapter tests for explicit credential injection path and validated YDB backoff/store factory behaviors.
- CFG-P02-T015 completed: `index.py` runtime routing switched to v2-only policy; all API v1 routes return `410` with `api_v1_discontinued`.
- CFG-P02-T016 completed: `tests/api/test_frontend_api_routing.py` aligned with v2-only policy and current mutable runtime knobs (`APP_READMODEL_SOURCE`).
- CFG-P02-T017 completed: removed legacy `FRONTEND_API_DEFAULT_VERSION` from active runtime config contour (`config/constants.py`, `src/config/loader.py` allowlist, docs note).
- CFG-P02-T018 completed: executed extended smoke pack across API/core/services/adapters after v2-only/config cleanup.
- CFG-P02-T019 completed: removed dead API v1 documentation builders (`_frontend_api_doc`, `_frontend_api_doc_html`) from `index.py`.
- CFG-P02-T020 completed: reran extended smoke pack after dead-code removal (api/core/services/adapters) with green result.
- CFG-P02-T021 completed: updated entrypoint system doc with explicit runtime behavior for API v1 paths (`410 api_v1_discontinued`).
- CFG-P02-T022 completed: extracted API v2 documentation builders from `index.py` to `src/entrypoints/http/frontend_v2_docs.py`.
- CFG-P02-T023 completed: validated no behavior regressions with API routing/unit smoke and runtime smoke packs.
- CFG-P02-T024 completed: extracted API v2 request handler from `index.py` into `src/entrypoints/http/frontend_v2_handler.py`; kept index as thin delegator for this path.
- CFG-P02-T025 completed: executed full smoke contour after handler extraction (API routing + core/services/adapters unit smoke).
- CFG-P02-T026 completed: extracted API root and API v1-discontinued compatibility handlers from `index.py` into `src/entrypoints/http/frontend_compat_handlers.py`.
- CFG-P02-T027 completed: executed full smoke contour after compatibility handler extraction (API routing + core/services/adapters unit smoke).
- CFG-P02-T028 completed: restored explicit boundary propagation for YDB SA credentials (`YC_SA_JSON_CREDENTIALS` / `YC_SA_KEY_FILE`) through main/index/services into YDB repos and migrate job.
- CFG-P02-T029 completed: executed full smoke contour after credential wiring updates (API routing + core/services/adapters unit smoke).
- CFG-P02-T030 completed: extracted group-query request handling from `index.py` to `src/entrypoints/http/group_query_handler.py` with dependency injection boundary.
- CFG-P02-T031 completed: executed full smoke contour after group-query extraction (API routing + core/services/adapters unit smoke).
- CFG-P02-T032 completed: extracted frontend API query parameter parsers from `index.py` into `src/entrypoints/http/frontend_query_params.py`.
- CFG-P02-T033 completed: executed full smoke contour after parser extraction (API routing + core/services/adapters unit smoke).
- CFG-P02-T034 completed: extracted runtime mode helpers (`trigger/mode/force_refresh`) from `index.py` into `src/entrypoints/http/runtime_mode.py`.
- CFG-P02-T035 completed: executed full smoke contour after runtime mode helper extraction (API routing + core/services/adapters unit smoke).
- CFG-P02-T036 completed: extracted HTTP response/path helper functions (`json/html/error/path_matches`) from `index.py` into `src/entrypoints/http/response_utils.py`.
- CFG-P02-T037 completed: executed full smoke contour after response/path helper extraction (API routing + core/services/adapters unit smoke).
- CFG-P02-T038 completed: extracted frontend task loading helper from `index.py` into `src/entrypoints/http/frontend_tasks_loader.py`.
- CFG-P02-T039 completed: executed full smoke contour after frontend task loader extraction (API routing + core/services/adapters unit smoke).
- CFG-P02-T040 completed: extracted HTTP debug event-shape logger from `index.py` into `src/entrypoints/http/debug_utils.py`.
- CFG-P02-T041 completed: executed full smoke contour after HTTP debug helper extraction (API routing + core/services/adapters unit smoke).
- CFG-P02-T042 completed: restored API v1 runtime compatibility (supported `/api/v1*` frontend/read-model routes mapped to v2 handler paths instead of `410`).
- CFG-P02-T043 completed: aligned API routing tests and system docs with v1 compatibility-alias policy and validated full smoke contour.
- CFG-P02-T044 completed: added API v2 runtime fallback when YDB readmodel access fails under `READMODEL_SOURCE=ydb`; fallback serves payload from legacy source path instead of crashing the request.
- CFG-P02-T045 completed: added regression test for `READMODEL_SOURCE=ydb` + YDB failure path and validated full smoke contour.
- CFG-P02-T046 completed: extracted group-query task loading helper from `index.py` into `src/entrypoints/http/group_query_tasks_loader.py`.
- CFG-P02-T047 completed: executed full smoke contour after group-query task loader extraction (API routing + core/services/adapters unit smoke).
- CFG-P02-T048 completed: removed intermediate group-query wrapper function from `index.py`; switched handler flow to direct delegation call using extracted HTTP modules.
- CFG-P02-T049 completed: executed full smoke contour after group-query wrapper removal (API routing + core/services/adapters unit smoke).
- CFG-P02-T050 completed: removed redundant `v1_discontinued` handler from dispatch chain since supported API v1 paths are already handled as v2 aliases.
- CFG-P02-T051 completed: executed full smoke contour after HTTP dispatch chain simplification (API routing + core/services/adapters unit smoke).
- CFG-P02-T052 completed: extracted root/v2 HTTP dispatch wiring from `index.py` into `src/entrypoints/http/http_dispatch_chain.py`.
- CFG-P02-T053 completed: executed full smoke contour after dispatch-chain wiring extraction (API routing + core/services/adapters unit smoke).
- CFG-P02-T054 completed: extracted runtime execution/error-handling block from `index.py` into `src/entrypoints/http/runtime_execution.py`.
- CFG-P02-T055 completed: executed full smoke contour after runtime execution extraction (API routing + core/services/adapters unit smoke).
- CFG-P02-T056 completed: synchronized system docs to reflect current thinned `index.py` role and extracted HTTP modules (`event_parser`, dispatch chain, runtime execution helpers).
- CFG-P02-T057 completed: removed dead `v1_discontinued` compatibility handler code from `src/entrypoints/http/frontend_compat_handlers.py`.
- CFG-P02-T058 completed: executed full smoke contour after dead compatibility code removal (API routing + core/services/adapters unit smoke).
- CFG-P02-T059 completed: extracted source snapshot reader helpers from `main.py` into `src/entrypoints/jobs/source_snapshot_reader.py`.
- CFG-P02-T060 completed: executed full smoke contour after snapshot-reader extraction from `main.py` (API routing + core/services/adapters unit smoke).
- CFG-P02-T061 completed: added HTTP dispatch error boundary in `index.py` so handler exceptions return structured API errors instead of bubbling to gateway `502`.
- CFG-P02-T062 completed: added structured `503 frontend_source_unavailable` response in `frontend_v2_handler` when legacy source path fails at runtime.
- CFG-P02-T063 completed: added regression test for legacy source failure path and validated full smoke contour.
- P01 scaffold implemented (uncommitted):
  - YAML config files added: `config/runtime.yaml`, `config/tables.yaml`, `config/db.yaml`, `config/llm.yaml`, `config/mapping.yaml`
  - typed schema scaffold: `src/config/schema.py`
  - loader scaffold + env allowlist: `src/config/loader.py`
  - bootstrap scaffold: `src/app/bootstrap.py`
  - docs update: `docs/system/config.md`
  - dependency note: `PyYAML` added to `requirements.txt`
  - constants dedup: `config/constants.py` now sources sheet names/field maps/color maps/hidden stages and runtime defaults from YAML loader (`load_config()`), without hardcoded duplicates.
  - constants transfer: `HELPER_CHARACTER` moved to `config/llm.yaml` (`assistant.helper_character`), `TRIGGERS` moved to `config/runtime.yaml` (`triggers`).
  - env cleanup: removed YAML-covered defaults from `.env`, `.env.example`, `.env.dev.example`, `.env.prod.example` (runtime/sheet/source/pipeline/source-select keys).
  - added deploy defaults map: `config/deploy.yaml` (folder/function/runtime/timeout/entrypoint/service-account id).
  - moved web defaults to `config/runtime.yaml` and object storage defaults to `config/db.yaml`.
  - updated workflows to consume YAML defaults instead of repo vars/secrets for non-sensitive deploy settings:
    - `.github/workflows/deploy_yc_function_main.yml`
    - `.github/workflows/release_yc_function_prod.yml`
  - `.env` cleaned to secrets/override-only keys; non-secret constants removed.
  - `.env.example` rewritten to minimal secret/override template; `.env.dev.example` and `.env.prod.example` reduced to optional override stubs.
- Local smoke check:
  - `.venv\\Scripts\\python.exe -c "from src.config.loader import load_config; cfg=load_config(); print('ok', bool(cfg.tables.sheet_names), bool(cfg.mapping.project_aliases), cfg.db.tables.get('tasks'))"`
  - result: `ok True True dtm_tasks`
  - `.venv\\Scripts\\python.exe -c "from src.config.loader import load_config; cfg=load_config(); import config.constants as c; print('cfg', bool(cfg.tables.sheet_names), bool(cfg.mapping.project_aliases)); print('const', len(c.SHEET_NAMES), len(c.TASK_FIELD_MAP), len(c.PEOPLE_FIELD_MAP), len(c.REPLACE_NAMES), len(c.COLOR_STATUS), len(c.NO_VISIBLE_STAGES))"`
  - result: `cfg True True` and `const 7 11 8 26 5 6`
  - `python -m py_compile src/services/planner_runtime.py core/planner.py main.py`
  - `python -m unittest tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty -v`
  - `rg -n "from config import|from config\\.constants import|import config\\.constants" src core main.py index.py agent tests`
  - `python -m py_compile src/app/planner_bootstrap.py src/services/planner_runtime.py main.py index.py`
  - `python -m unittest tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty -v`
  - `python -m py_compile index.py main.py src/app/planner_bootstrap.py src/services/planner_runtime.py`
  - `python -m unittest tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty -v`
  - `python -m py_compile src/app/planner_bootstrap.py main.py index.py src/services/planner_runtime.py`
  - `python -m unittest tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty -v`
  - `python -m py_compile src/services/calendar_runtime.py src/app/planner_bootstrap.py src/services/planner_runtime.py main.py index.py`
  - `python -m py_compile core/timing_parser.py core/task_timing_processor.py src/adapters/google_sheets/task_repository.py src/app/planner_bootstrap.py src/services/calendar_runtime.py main.py index.py`
  - `python -m py_compile core/reminder.py core/timing_parser.py core/task_timing_processor.py src/services/calendar_runtime.py src/app/planner_bootstrap.py src/adapters/google_sheets/task_repository.py main.py index.py`
  - `python -m unittest tests.core.test_timing_year_modes tests.services.test_pipeline_runtime tests.core.test_manager_calendar_empty -v`
  - `python -m py_compile src/adapters/telegram.py index.py main.py src/app/planner_bootstrap.py src/services/calendar_runtime.py core/timing_parser.py core/task_timing_processor.py src/adapters/google_sheets/task_repository.py src/adapters/google_sheets/people_manager.py`
  - `python -m unittest tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty -v`
  - `python -m unittest tests.api.test_frontend_api_routing -v` (known pre-existing drift: expects `index.build_operational_store` symbol not present in current branch contour)
  - `python -m py_compile src/adapters/ydb/client.py src/adapters/store_ydb.py tests/adapters/test_json_store_adapter.py`
  - `python -m unittest tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `rg -n "from config import|from config\\.constants import|import config\\.constants" src core main.py index.py`
  - `python -m py_compile index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing -v`
  - `python -m unittest tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile config/constants.py src/config/loader.py index.py main.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `rg -n "^def _frontend_api_doc\\(|^def _frontend_api_doc_html\\(" index.py`
  - `python -m py_compile index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile src/entrypoints/http/http_dispatch_chain.py index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile src/entrypoints/http/runtime_execution.py index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile src/entrypoints/http/frontend_compat_handlers.py index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile src/entrypoints/jobs/source_snapshot_reader.py main.py index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile src/entrypoints/http/frontend_v2_handler.py index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing -v`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile src/entrypoints/http/frontend_v2_docs.py index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing -v`
  - `python -m unittest tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile src/entrypoints/http/frontend_v2_handler.py src/entrypoints/http/frontend_v2_docs.py index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile src/entrypoints/http/frontend_compat_handlers.py src/entrypoints/http/frontend_v2_handler.py src/entrypoints/http/frontend_v2_docs.py index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile main.py index.py src/services/pipeline_runtime.py src/entrypoints/jobs/db_migrate_job.py src/adapters/ydb/readmodel_repo.py src/adapters/ydb/operational_repo.py src/adapters/ydb/task_repository.py src/entrypoints/http/frontend_v2_handler.py tests/services/test_pipeline_runtime.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile src/entrypoints/http/group_query_handler.py index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile src/entrypoints/http/frontend_query_params.py index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile src/entrypoints/http/runtime_mode.py index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile src/entrypoints/http/response_utils.py index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile src/entrypoints/http/frontend_tasks_loader.py index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile src/entrypoints/http/debug_utils.py index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile src/entrypoints/http/frontend_v2_handler.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing -v`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile src/entrypoints/http/group_query_tasks_loader.py index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile index.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
  - `python -m py_compile src/entrypoints/http/frontend_v2_handler.py tests/api/test_frontend_api_routing.py`
  - `python -m unittest tests.api.test_frontend_api_routing -v`
  - `python -m unittest tests.api.test_frontend_api_routing tests.services.test_pipeline_runtime tests.core.test_timing_year_modes tests.core.test_manager_calendar_empty tests.services.test_ydb_backoff tests.adapters.test_json_store_adapter -v`
