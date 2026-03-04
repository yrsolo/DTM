# CAM-ENTRYPOINT-REFORM-V1 Evidence

## Trust Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `index.py`, `main.py`, `src/entrypoints/http/*`, `src/entrypoints/jobs/*` | 2026-03-04 | TeamLead agent | direct code scan + compile smoke | high | extraction done without behavior-targeting rewrites |
| `tests/services/test_pipeline_runtime.py` | 2026-03-04 | TeamLead agent | local unittest run passed | high | guard-path smoke coverage for extracted pipeline helper |
| `docs/system/entrypoints_index_main.md` | 2026-03-04 | TeamLead agent | doc updated with extraction progress section | high | runtime behavior notes aligned with code split |

## Execution Log
- P01 completed:
  - HTTP payload/path/method/query parsing extracted to `src/entrypoints/http/event_parser.py`
  - dispatch chain extracted to `src/entrypoints/http/router.py`
- P02 completed:
  - `TimerJob` shell integrated in `main.py`
  - `db_migrate` branch extracted to `src/entrypoints/jobs/db_migrate_job.py`
- P03 completed:
  - YDB sync + readmodel orchestration extracted to `src/services/pipeline_runtime.py`
  - smoke test added: `tests/services/test_pipeline_runtime.py`
- P04 completed:
  - system docs updated with explicit extraction progress

## Closeout Threshold
Campaign is considered complete for V1 when:
1. parsing/routing scaffolds are extracted and used by `index.py`,
2. major runtime branches (`timer shell`, `db_migrate`, `ydb sync/readmodel orchestration`) are no longer inline in `main.py`,
3. at least one smoke test protects extracted helper behavior,
4. docs reflect the split and known remaining hotspots.

## Remaining Hotspots (handoff candidates)
- endpoint business handlers still live in `index.py` (next split candidates: v1/v2 API handlers, group-query handler)
- additional `main.py` branches can still be extracted into dedicated jobs/use-cases

