# DTM-81: Documentation readability refactor

## Context
- `doc/*` became hard to navigate after many stage additions.
- `doc/03_reconstruction_backlog.md` accumulated too much historical detail for day-to-day reading.

## Goal
- Make documentation understandable for a new reader in one pass.
- Introduce a clear documentation map and concise current-state backlog doc.

## Non-goals
- No runtime behavior changes.
- No architecture changes in code.

## Plan
1. Archive current verbose `doc/03` snapshot.
2. Add a documentation navigation map (`doc/00_documentation_map.md`).
3. Rewrite `doc/03` into concise status/queue format.
4. Sync sprint/task/process docs with new doc contour.
5. Complete Jira lifecycle + owner notification.

## Checklist (DoD)
- [x] Jira key exists (`DTM-81`) and status moved to `V rabote` before edits.
- [x] Historical verbose `doc/03` saved in archive.
- [x] Documentation map added.
- [x] Backlog document rewritten to concise readable format.
- [x] Jira evidence comment added.
- [x] Jira moved to `Gotovo`.
- [x] Telegram completion sent.

## Work log
- 2026-02-27: Created `DTM-81`, moved to `V rabote`.
- 2026-02-27: Archived old backlog doc to `doc/archive/03_reconstruction_backlog_2026-02-27.pre_readability.md`.
- 2026-02-27: Added documentation map and concise backlog format.
- 2026-02-27: Added Jira evidence comment, moved issue to `Gotovo`, and sent owner Telegram completion note (Stage 9: done 5 / remaining 2).

## Links
- Jira: DTM-81
- New map: `doc/00_documentation_map.md`
- Archive: `doc/archive/03_reconstruction_backlog_2026-02-27.pre_readability.md`
