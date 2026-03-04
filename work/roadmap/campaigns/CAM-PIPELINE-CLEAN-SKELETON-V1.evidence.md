# CAM-PIPELINE-CLEAN-SKELETON-V1 Evidence

## Trust Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `main.py`, `src/services/pipeline_runtime.py`, `docs/system/architecture.md` | 2026-03-04 | TeamLead agent | direct code/doc scan + helper usage grep | high | confirms `main.py` still hosts operational helper blocks suitable for behavior-preserving extraction |

## Execution Log
- `PIPE-P01-T001` completed: inventory and extraction order documented in campaign plan.
- `PIPE-P01-T002` completed: readmodel freshness helper extracted to `src/entrypoints/jobs/readmodel_freshness.py`; `main.py` switched to imports.
- `PIPE-P02-T001` completed: source hash-gate branch extracted to `src/entrypoints/jobs/hash_gate_job.py`; `main.py` delegates decision.
- `PIPE-P02-T002` completed: legacy store-write branch extracted to `src/entrypoints/jobs/legacy_store_write_job.py`; `main.py` delegates write/skip logging.
- `PIPE-P02-T003` completed: task payload conversion helpers extracted to `src/entrypoints/jobs/task_payloads.py`; `main.py` uses module imports.
- `PIPE-P03-T001` completed: task source-switch orchestration extracted to `src/entrypoints/jobs/source_switch_job.py`; `main.py` delegates repository swap policy.

## Verification
- `python -m py_compile main.py src/entrypoints/jobs/readmodel_freshness.py`
- `python -m unittest tests.services.test_pipeline_runtime tests.api.test_frontend_api_routing -v`
- `python -m py_compile main.py src/entrypoints/jobs/hash_gate_job.py src/entrypoints/jobs/legacy_store_write_job.py tests/services/test_hash_gate_job.py tests/services/test_legacy_store_write_job.py`
- `python -m unittest tests.services.test_hash_gate_job tests.services.test_legacy_store_write_job tests.services.test_pipeline_runtime tests.api.test_frontend_api_routing -v`
- `python -m py_compile main.py src/entrypoints/jobs/task_payloads.py tests/services/test_task_payloads_job.py`
- `python -m unittest tests.services.test_task_payloads_job tests.services.test_hash_gate_job tests.services.test_legacy_store_write_job tests.services.test_pipeline_runtime tests.api.test_frontend_api_routing -v`
- `python -m py_compile main.py src/entrypoints/jobs/source_switch_job.py tests/services/test_source_switch_job.py`
- `python -m unittest tests.services.test_source_switch_job tests.services.test_task_payloads_job tests.services.test_hash_gate_job tests.services.test_legacy_store_write_job tests.services.test_pipeline_runtime tests.api.test_frontend_api_routing -v`

## Results
- `py_compile`: pass.
- `unittest`: pass (`Ran 23 tests`, `OK`).
