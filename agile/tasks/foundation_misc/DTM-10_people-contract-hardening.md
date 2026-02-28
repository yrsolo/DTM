# DTM-10: Stage 1 people contract normalization and lookup hardening

## Context
- Stage 1 requires input-contract stabilization not only for tasks, but also for people data used in reminders.
- `core/people.py` had fragile points:
  - preloaded people mapping bug in `PeopleManager.__init__`,
  - unsafe person mapping for missing columns,
  - `get_designers` returned keys instead of `Person` objects,
  - nullable text/id fields were not normalized.

## Goal
- Make people mapping robust for nullable/malformed sheet payloads.
- Ensure people collections and lookup helpers return stable expected types.

## Non-goals
- No reminder message content changes.
- No Telegram delivery policy changes.

## Mode
- Execution mode

## Plan
1) Add null-safe normalization helpers for people field parsing.
2) Fix people collection/mapping bugs in manager helpers.
3) Run smoke checks, sync docs/Jira, close lifecycle.

## Checklist (DoD)
- [x] `Person` fields are null-safe normalized.
- [x] `PeopleManager.__init__` and `get_designers` return correct structures.
- [x] Sheet row mapping tolerates missing nullable values.
- [x] Smoke checks passed.
- [x] Jira evidence comment + status `Gotovo`.

## Work log
- 2026-02-27: Jira issue DTM-10 created and moved to `V rabote`.
- 2026-02-27: Implemented Stage 1 people contract hardening in `core/people.py`:
  - `_is_nullish` / `_normalize_text`,
  - safer preload mapping in `PeopleManager.__init__`,
  - safe mapping via `.get` in `_create_person`,
  - fixed `get_designers` to return person objects.
- 2026-02-27: Smoke checks:
  - `.venv\Scripts\python.exe -m py_compile core\people.py` passed.
  - `.venv\Scripts\python.exe local_run.py --help` passed.
  - targeted module smoke passed (`people_smoke_ok`) for normalization + manager behavior.
  - `.venv\Scripts\python.exe local_run.py --mode reminders-only --dry-run` failed on pre-existing reminder/OpenAI path (`httpx.AsyncClient(... proxies=...)`), recorded as follow-up risk outside DTM-10 scope.
- 2026-02-27: Jira evidence comment added; issue transitioned to `Gotovo`.

## Links
- Jira: DTM-10
- Notes: doc/03_reconstruction_backlog.md (Stage 1)
