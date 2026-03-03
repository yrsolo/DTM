# DTM-236: Readmodel freshness markers for render/notify cloud parity checks

## Context
- Stage 23 needs freshness observability parity between API and non-API blocks.
- API v2 already exposes readmodel metadata in response.
- Render/notify paths lacked explicit readmodel freshness markers in runtime logs.

## Goal
- Add runtime marker for readmodel freshness when render/notify YDB contour is active.
- Keep marker deterministic and testable via helper unit test.

## Non-goals
- No source switching behavior changes.
- No API contract changes.

## Plan
1. Add helper to build normalized freshness marker payload.
2. Emit marker in runtime when YDB source for render/notify is enabled.
3. Add unit tests for helper output.
4. Run timer smoke and API/source-switch tests.

## Checklist (DoD)
- [x] Freshness marker helper added in `main.py`.
- [x] Runtime logs emit `readmodel_freshness=...` under YDB render/notify contour.
- [x] Unit tests added/passed for marker helper.
- [x] Timer smoke passed.

## Work log
- 2026-03-03: Added `_readmodel_freshness_marker` helper in `main.py`.
- 2026-03-03: Added conditional readmodel freshness log emission for render/notify YDB contour.
- 2026-03-03: Added `tests/core/test_main_readmodel_freshness.py`.
- 2026-03-03: Validation passed:
  - `.venv\\Scripts\\python.exe -m unittest tests.core.test_main_readmodel_freshness tests.core.test_main_source_switch tests.api.test_frontend_api_routing -v`
  - `cmd /c run_timer.cmd`

## Links
- Runtime file: `main.py`
