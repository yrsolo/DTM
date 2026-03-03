# DTM-226: Stage 21 timing year inference hardening

## Context
- Legacy source rows often store milestone dates as `dd.mm` without year.
- Current parser uses previous-task context year + +-5 month correction and `mean` pivot.
- On year boundaries and outliers this may drift; need safer modes without breaking legacy.

## Goal
- Add `TIMING_YEAR_MODE=legacy|anchors|chain`.
- Keep `legacy` behavior stable.
- Add incremental improvements:
  - `anchors`: explicit `dd.mm.yyyy` / `dd.mm.yy` anchors.
  - `chain`: robust pivot (`median`) and guarded year-shift heuristic in chain.
- Add tests for legacy regression and year-boundary chain behavior.

## Non-goals
- No full parser rewrite.
- No breaking contract changes in task payload.

## Plan
1. Add runtime config flag for timing year mode.
2. Extend `TimingParser` with explicit-anchor parsing in non-legacy modes.
3. Keep legacy branch behavior untouched; use `mean` pivot only in legacy.
4. Add chain mode post-parse shift heuristic and diagnostics.
5. Add/extend tests.

## Checklist (DoD)
- [x] `TIMING_YEAR_MODE` added and validated.
- [x] `legacy` mode preserves old behavior.
- [x] `anchors` supports explicit-year dates.
- [x] `chain` applies median pivot and guarded shift on year-boundary jumps.
- [x] Tests cover legacy regression + anchors + chain boundary case.

## Work log
- 2026-03-03: Task started.
- 2026-03-03: Added `TIMING_YEAR_MODE` to `config/constants.py` with allowed values `legacy|anchors|chain`.
- 2026-03-03: Hardened `TimingParser`:
  - legacy branch preserved,
  - explicit-year anchors (`dd.mm.yyyy` / `dd.mm.yy`) for non-legacy modes,
  - parser diagnostics with `year_source` events.
- 2026-03-03: Replaced task-chain pivot to `median` in non-legacy modes; kept `mean` in `legacy`.
- 2026-03-03: Added guarded chain year shift heuristic for Jan-Mar rollover after Q4 context.
- 2026-03-03: Added tests `tests/core/test_timing_year_modes.py` and passed:
  - `.venv\\Scripts\\python.exe -m unittest tests.core.test_timing_year_modes -v`
  - `.venv\\Scripts\\python.exe -m unittest tests.core.test_manager_calendar_empty -v`
  - `.venv\\Scripts\\python.exe -m unittest tests.core.test_use_cases -v`

## Links
- `core/repository.py`
- `config/constants.py`
- `tests/core/test_timing_year_modes.py`
