# DTM-194: Stage 20 documentation structure hygiene and stale-tail register

## Context
- Even with cleaned structure, repository should clearly separate active docs from historical artifacts.
- Owner requested logical ordering and stale-tail visibility.

## Goal
- Improve discoverability and publish explicit stale-tail register without destructive cleanup.

## Non-goals
- No deletion of historical files.

## Plan
1. Audit `doc/` and `agile/` tree for active vs historical boundaries.
2. Update map/index docs to make navigation straightforward.
3. Publish stale-tail register and handling policy.

## Checklist (DoD)
- [x] Documentation map reflects current folder semantics and read order.
- [x] Stale-tail register published in ops/governance docs.
- [x] Sprint/backlog references point only to active sources.

## Work log
- 2026-02-28: Updated stage index in `doc/00_documentation_map.md` through Stage 19 and active Stage 20 pointer.
- 2026-02-28: Published stale-tail register `doc/ops/stage20_stale_tail_register.md` with keep/archive policy.

## Links
- `doc/00_documentation_map.md`
- `doc/ops/`
- `doc/archive/`
