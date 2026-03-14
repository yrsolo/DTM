# Evidence - CAM-2026-03-14-PEOPLE-SNAPSHOT-AND-SECRET-API-V1

## Trust gate
- source: verified runtime code, config, current docs
- last_verified_at: 2026-03-14
- verified_by: Codex
- evidence:
  - `src/snapshot_engine/update_job.py`
  - `src/snapshot_engine/serialization.py`
  - `src/snapshot_engine/engine.py`
  - `src/entrypoints/http/router.py`
  - `src/entrypoints/http/access_context.py`
  - `config/tables.yaml`
  - `config/runtime.yaml`
  - `docs/system/config.md`
  - `docs/system/architecture.md`
- trust_level: high
- notes:
  - current people snapshot is partial and reminder-oriented
  - current frontend `entities.people` is derived from task owners, not from people snapshot
  - existing trusted secret contract is code-backed and can be reused for a secret-only internal people API

## 2026-03-14 execution evidence
- implemented:
  - full-fidelity people snapshot model with canonical fields plus mapped `attributes`
  - updater now reads all mapped people columns from `config/tables.yaml`
  - secret-only `GET /api/v2/people`
  - snapshot engine lookup helpers for `telegram_id`, `chat_id`, `email`, and `name`
- verified by code pointers:
  - `src/snapshot_engine/update_job.py`
  - `src/snapshot_engine/serialization.py`
  - `src/snapshot_engine/engine.py`
  - `src/entrypoints/http/people_snapshot_handler.py`
  - `src/entrypoints/http/router.py`
  - `config/tables.yaml`
- docs aligned:
  - `docs/system/config.md`
  - `docs/system/architecture.md`
  - `docs/system/browser_auth_contract.md`
  - `docs/system/dataflow.md`
- retained distinction:
  - `frontend_v2.entities.people` remains derived from selected task owners
  - people snapshot is the canonical registry for reminder/auth use cases
