# Pipeline Cleanup Plan (main.py thinning)

## Current hotspots in `main.py`
- Freshness marker helper and safe-print helper.
- Source hash-gate block (`build_hash_basis` + `evaluate_hash_gate` + `save_last_hash`).
- Legacy blob write block (`build_operational_store` + reporting).
- Operational payload conversion helpers.

## Ordered extraction plan
1. Extract small pure helpers first (done: readmodel freshness helper).
2. Extract hash-gate branch into dedicated job helper module. (done)
3. Extract legacy store-write/reporting branch into dedicated job helper module. (done)
4. Re-check if task payload conversion helpers should stay near entrypoint or move to service boundary. (done: moved to `src/entrypoints/jobs/task_payloads.py`)
5. Extract source-switch orchestration block to dedicated job helper module. (done: `src/entrypoints/jobs/source_switch_job.py`)
6. Extract readmodel freshness probe/logging branch to dedicated job helper module. (done: `src/entrypoints/jobs/readmodel_probe_job.py`)
7. Extract quality-report summary formatter/printer to dedicated job helper module. (done: `src/entrypoints/jobs/quality_report_job.py`)

## Constraints
- No behavior changes in sync/readmodel path.
- Keep `main.py` as mode-router plus high-level orchestration.
