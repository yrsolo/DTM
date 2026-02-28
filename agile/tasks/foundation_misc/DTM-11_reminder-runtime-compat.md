# DTM-11: Reminder runtime compatibility fix (httpx proxy + unicode logging)

## Context
- `local_run.py --mode reminders-only --dry-run` failed on pre-existing reminder path.
- Root causes:
  - incompatible `httpx.AsyncClient(proxies=...)` argument with current runtime stack,
  - console `UnicodeEncodeError` risk on non-UTF terminals during fallback logging.

## Goal
- Restore stable reminder dry-run execution without changing business reminder behavior.

## Non-goals
- No change to reminder content logic.
- No change to delivery routing policy.

## Mode
- Execution mode

## Plan
1) Make OpenAI HTTP client proxy setup compatible with current `httpx` signature.
2) Add safe console printing helper for unicode-heavy logs.
3) Verify reminder dry-run flow and close Jira lifecycle.

## Checklist (DoD)
- [x] Reminder client no longer uses incompatible `proxies=` arg.
- [x] Reminder fallback logging is unicode-safe on constrained terminals.
- [x] Smoke-check passes for reminder path.
- [x] Jira evidence comment + status `Gotovo`.

## Work log
- 2026-02-27: Jira issue DTM-11 created and moved to `V rabote`.
- 2026-02-27: Updated `core/reminder.py`:
  - added `_safe_print` and `_sanitize_proxy_url`,
  - switched proxy wiring to `httpx.AsyncClient(proxy=...)` with sanitized URL,
  - replaced unsafe console print points in reminder runtime paths.
- 2026-02-27: Smoke checks passed:
  - `.venv\Scripts\python.exe -m py_compile core\reminder.py`
  - `.venv\Scripts\python.exe local_run.py --help`
  - `.venv\Scripts\python.exe local_run.py --mode reminders-only --dry-run`
- 2026-02-27: Jira evidence comment added; issue transitioned to `Gotovo`.

## Links
- Jira: DTM-11
- Notes: doc/03_reconstruction_backlog.md
