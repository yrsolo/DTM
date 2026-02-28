# DTM-197: Agile folder structure and freshness cleanup

## Context
- `agile/tasks` had too many files in one flat directory.
- Active agile docs were overloaded by long historical lists.

## Goal
- Restructure task storage into stage-based folders.
- Compact and refresh active agile control documents.

## Non-goals
- No production code behavior changes.
- No deletion of historical task content.

## Plan
1. Archive current agile snapshots.
2. Split `agile/tasks` into structured subfolders.
3. Refresh `agile/strategy.md`, `agile/sprint_current.md`, `agile/retro.md`, `agile/context_registry.md`.
4. Add task index doc for new structure.

## Checklist (DoD)
- [x] Task files moved from flat structure to stage-based folders.
- [x] Active agile docs compacted and updated.
- [x] Historical snapshots preserved in `agile/archive`.

## Work log
- 2026-02-28: Created archive snapshots for strategy/sprint/retro/context before cleanup.
- 2026-02-28: Moved task files into `stage_00_09`, `stage_10_19`, `stage_20_plus`, `foundation_misc`.
- 2026-02-28: Published `agile/tasks/README.md` and refreshed active agile docs.

## Links
- `agile/sprint_current.md`
- `agile/context_registry.md`
- `agile/tasks/README.md`
