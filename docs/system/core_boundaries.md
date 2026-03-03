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
- `core/errors.py`
- `core/task_query_contract.py`
- `core/task_query_adapter.py`
- `core/api_payload.py`
- `core/api_payload_v2.py`
- `core/read_model.py`
- `core/group_query.py`

### Infra-coupled modules (migration candidates out of core)
- `core/bootstrap.py` (config/env + adapter composition + external clients)
- `core/repository.py` (Google Sheets IO + Telegram logging coupling)
- `core/people.py` (Google Sheets service coupling)
- `core/reminder.py` (Telegram/OpenAI/httpx/aiohttp IO adapters + orchestration)
- `core/planner.py` (runtime orchestration + sheet wiring)
- `core/manager.py` (render adapters + service helpers)

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
