# DTM-80: Stage 9 docs/agile hygiene cleanup and archive normalization

## Context
- Current `agile/sprint_current.md` and `agile/context_registry.md` accumulated long historical logs and duplicate sections.
- The board must remain operational (current sprint state), while long evidence history must stay accessible but outside active board.

## Goal
- Normalize agile docs so current sprint control is concise, readable, and Jira-aligned.
- Preserve historical data via archive files, without loss of evidence.

## Non-goals
- No runtime/business logic changes.
- No Stage 9 feature-scope expansion beyond documentation/process hygiene.

## Plan
1. Archive pre-cleanup versions of oversized agile docs.
2. Rebuild `agile/sprint_current.md` as compact operational board.
3. Rebuild `agile/context_registry.md` as active trust registry with archive links.
4. Sync backlog docs with the new documentation contour.
5. Run lightweight smoke checks and complete Jira lifecycle.

## Checklist (DoD)
- [x] Jira key exists (`DTM-80`) and moved to `V rabote` before edits.
- [x] Pre-cleanup history archived in repository.
- [x] `agile/sprint_current.md` follows concise operational structure.
- [x] `agile/context_registry.md` contains active trust registry + archive pointers.
- [x] Jira evidence comment added.
- [x] Jira moved to `Gotovo`.
- [x] Telegram completion sent to owner with stage counter.

## Work log
- 2026-02-27: Jira task created (`DTM-80`) and moved to `V rabote`.
- 2026-02-27: Archived previous oversized agile docs to `agile/archive/*pre_hygiene.md`.
- 2026-02-27: Rebuilt sprint board and context registry into concise operational format.
- 2026-02-27: Jira evidence comment added, task moved to `Gotovo`, owner completion Telegram sent with Stage 9 counter `done 4 / remaining 2`.

## Links
- Jira: DTM-80
- Archive: `agile/archive/sprint_current_2026-02-27.pre_hygiene.md`
- Archive: `agile/archive/context_registry_2026-02-27.pre_hygiene.md`
