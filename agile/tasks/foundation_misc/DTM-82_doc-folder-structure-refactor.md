# DTM-82: Doc folder structure refactor

## Context
- Top-level `doc/` looked overloaded (many numbered files with mixed purpose).
- Strategic docs and historical/stage artifacts were mixed in one flat list.

## Goal
- Make `doc/` readable at first glance by separating documents by purpose.
- Keep strategic docs in top-level, move operational/governance/stage packages into dedicated subfolders.

## Non-goals
- No runtime behavior changes.
- No business logic changes.

## Plan
1. Move docs into `doc/ops`, `doc/governance`, `doc/stages`.
2. Keep strategic core files in top-level `doc/`.
3. Update active references in README/agile/current docs.
4. Verify that no active reference points to moved old paths.
5. Close Jira lifecycle and send completion Telegram.

## Checklist (DoD)
- [x] Jira key exists (`DTM-82`) and moved to `V rabote` before edits.
- [x] Top-level doc clutter reduced via folder split.
- [x] Documentation map updated to new structure.
- [x] Active links updated in README and current docs.
- [x] Jira evidence comment added.
- [x] Jira moved to `Gotovo`.
- [x] Telegram completion sent.

## Work log
- 2026-02-27: Created `DTM-82`, moved to `V rabote`.
- 2026-02-27: Moved operational/governance/stage docs into subfolders.
- 2026-02-27: Updated active references and backlog/map docs to new structure.
- 2026-02-27: Added Jira evidence comment, moved issue to `Gotovo`, and sent owner Telegram completion note (Stage 9: done 6 / remaining 2).

## Links
- Jira: DTM-82
- Map: `doc/00_documentation_map.md`
