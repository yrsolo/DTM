# DTM-17: Stage 1 timing parse diagnostics and non-fatal error accounting

## Context
- `TimingParser` handles malformed date lines non-fatally, but diagnostics are log-only and not structured for accounting.
- Stage 1 needs explicit parse-error accounting to support quality reporting and safe incremental hardening.

## Goal
- Add structured timing parse diagnostics.
- Keep parsing non-fatal and preserve pipeline continuity.
- Surface timing parse errors in row-level accounting.

## Non-goals
- No reminder delivery behavior changes.
- No broad rewrite of timing grammar.

## Mode
- Execution mode

## Plan
1) Add typed timing parse issue model and parser-side diagnostics buffer.
2) Wire parser diagnostics into task row-level issue accounting.
3) Run smoke checks and sync Jira/docs/sprint.

## Risks
- Diagnostic over-reporting on noisy data.
- Unintended behavior drift in date fallback paths.

## Acceptance Criteria
- Timing parse failures are captured as structured diagnostics.
- Task loader records timing parse diagnostics in row issues without crashing.
- Existing dry-run runtime flows remain green.

## Checklist (DoD)
- [x] Structured timing parse diagnostics added.
- [x] Non-fatal accounting wired to repository row issues.
- [x] Smoke checks passed.
- [x] Jira evidence comment + status `Gotovo`.

## Work log
- 2026-02-27: Jira issue DTM-17 created and moved to `V rabote`.
- 2026-02-27: Added `TimingParseIssue` and parser diagnostics accounting (`parse_issues`, `total_parse_errors`) in `TimingParser`.
- 2026-02-27: Wired timing diagnostics into task row accounting:
  - each parse error is tracked in parser diagnostics;
  - task row gets `row_issues` record with `timing parse errors: <count>`.
- 2026-02-27: Hardened sync-path diagnostics output for parse failures (unicode-safe print, no Telegram log in sync context).
- 2026-02-27: Smoke checks passed:
  - `.venv\Scripts\python.exe -m py_compile core\errors.py core\repository.py core\people.py core\contracts.py`
  - `.venv\Scripts\python.exe local_run.py --mode timer --dry-run`
  - `.venv\Scripts\python.exe local_run.py --mode reminders-only --dry-run`
  - targeted timing diagnostics smoke (`timing_diagnostics_smoke_ok`)
- 2026-02-27: Jira evidence comment added and issue moved to done category (`Gotovo`).

## Links
- Jira: DTM-17
- Sprint: agile/sprint_current.md
