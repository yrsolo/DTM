# Evidence - CAM-2026-03-22-BOOTSTRAP-SHELL-EXTRACTION-V1

## Trust gate
- source: current `src/platform/bootstrap.py`, current `src/platform/shell/__init__.py`, current top-level entrypoint path, current guardrails/tests, owner critique
- last_verified_at: 2026-03-22
- verified_by: Codex
- evidence:
  - `agent/owner_inputs/crit.md`
  - `src/platform/bootstrap.py`
  - `src/platform/shell/__init__.py`
  - `src/entrypoints/root/handler.py`
  - `index.py`
  - `tests/entrypoints/root/test_handler.py`
  - `tests/architecture/test_guardrails_v0.py`
- trust_level: high
- notes:
  - this wave is bounded to shell/top-entry seams; context/dependency assembly stays in `bootstrap`

## Result
- lazy shell singletons and top-entry runtime seams now live in `src/platform/shell`
- `src/platform/bootstrap.py` is narrowed back to config/env/context/dependency assembly plus `get_app_context` / `get_runtime_deps`
- `index.py` imports top-path shell/webhook/trigger seams from `src.platform.shell`, so `bootstrap` is no longer the visible runtime dispatch catalog

## Verification
- `python -m unittest tests.entrypoints.root.test_handler tests.entrypoints.root.test_parse_request tests.entrypoints.http.test_command_queue_foundation tests.architecture.test_guardrails_v0 tests.entrypoints.test_import_safety -v`
- Result: `73 tests`, `OK`
