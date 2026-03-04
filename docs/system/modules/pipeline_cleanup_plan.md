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
4. Re-check if task payload conversion helpers should stay near entrypoint or move to service boundary.

## Constraints
- No behavior changes in sync/readmodel path.
- Keep `main.py` as mode-router plus high-level orchestration.
