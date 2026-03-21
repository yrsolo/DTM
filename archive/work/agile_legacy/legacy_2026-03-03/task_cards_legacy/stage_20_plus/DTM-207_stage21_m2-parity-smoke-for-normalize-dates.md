# DTM-207: Stage 21 M2 parity smoke for normalize dates

## Context
- Migration plan requires parity smoke between legacy and new normalize behavior before wiring consumers.
- Full legacy bootstrap is heavy for narrow checks; need lightweight deterministic comparator.

## Goal
- Add parity smoke script for controlled fixtures:
  - legacy-style date extraction (`dd.mm` at line start)
  - new normalize extraction (`... dd.mm` in stage text)
- Compare planned dates and fail on mismatch.

## Non-goals
- No full parity of all fields and edge cases.
- No runtime switching to new normalize path.

## Plan
1. Add smoke script under `agent/`.
2. Add two representative fixtures (simple and year-boundary).
3. Run script and capture pass.

## Checklist (DoD)
- [x] Script committed.
- [x] Script returns success on current fixtures.
- [x] Result payload printed in structured JSON.

## Work log
- 2026-03-02: Added `agent/normalize_parity_smoke.py`.
- 2026-03-02: Implemented controlled parity check for planned stage dates.
- 2026-03-02: Ran smoke script successfully.

## Links
- `agent/normalize_parity_smoke.py`
