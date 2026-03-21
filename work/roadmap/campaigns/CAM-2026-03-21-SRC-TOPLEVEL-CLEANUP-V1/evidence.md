# CAM-2026-03-21-SRC-TOPLEVEL-CLEANUP-V1 Evidence

## Trust Gate

- source: current top-level `src/` tree and active import graph
  - last_verified_at: `2026-03-21`
  - verified_by: `Codex`
  - evidence:
    - `Get-ChildItem src -Directory`
    - `Get-ChildItem src/jobs,src/render,src/notify,src/snapshot_engine,src/telegram,src/handlers,src/entrypoints_adapters -Force`
    - `rg -n "^from src\\.(...)" src tests`
  - trust_level: `high`
  - notes: current inspection shows several top-level roots no longer contain live Python code, while `src/entrypoints_adapters` survives only as a stray adapter shelf for logic that belongs inside `access_api`.

## Active Tasks

- [x] remove dead top-level historical roots
- [x] remove stray `entrypoints_adapters` root by moving its live helper into `access_api`
- [x] strengthen guardrails so removed roots must not reappear
- [x] verify active tests/imports remain green

## Iteration Notes

- removed dead top-level roots that survived only as pycache or empty historical directories:
  - `src/jobs`
  - `src/render`
  - `src/notify`
  - `src/snapshot_engine`
  - `src/telegram`
  - `src/handlers`
- removed `src/entrypoints_adapters` after moving `build_frontend_query` into `src/contexts/access_api/internal/frontend_query.py`
- moved browser masking from `src/services/access/masking.py` into `src/contexts/access_api/internal/masking.py`, so `services/access` is no longer an owning-looking shelf in the repo map
- top-level `src/` map now reads through active architecture zones only:
  - `adapters`, `app`, `archive`, `commands`, `config`, `contexts`, `core`, `entrypoint`, `entrypoints`, `infra`, `observability`, `platform`, `services`, `worker`
- `src/__pycache__` may reappear during local test runs; it is treated as Python runtime noise rather than an architecture root and is no longer part of the structural kill criteria.
- guardrail strengthened in `tests/architecture/test_guardrails_v0.py` so removed top-level historical roots and `entrypoints_adapters` must not exist as live Python roots.
- verification after this cut stayed green:
  - `python -m unittest tests.contexts.access_api.test_masking tests.api.test_frontend_api_routing tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety tests.api.test_command_queue_foundation tests.contexts.attachments.test_attach_task_file_job tests.services.test_pipeline_runtime -v`
- next blocker is no longer a stray shelf but the remaining `src/services` core, which mixes shared errors, timer runtime, source ingestion, and older service-era modules.
