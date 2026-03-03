# Stage 20 Stale-Tail Register

Purpose: track non-blocking historical tails that are intentionally preserved, while keeping active docs concise.

## Classification
- `active`: source of truth for current work.
- `historical`: useful context, not primary source for current decisions.
- `tail`: candidate for future archival consolidation.

## Current register
| path | class | reason | action |
|---|---|---|---|
| `doc/archive/03_reconstruction_backlog_2026-02-27.pre_readability.md` | historical | full verbose snapshot before readability refactor | keep in archive |
| `agile/archive/sprint_current_2026-02-27.pre_hygiene.md` | historical | pre-hygiene board snapshot | keep in archive |
| `agile/archive/context_registry_2026-02-27.pre_hygiene.md` | historical | detailed trust log before compaction | keep in archive |
| `doc/stages/10_stage2_layer_inventory.md` | tail | also referenced by Stage 3 status; shared artifact naming may confuse newcomers | keep, annotate via map/backlog |
| `doc/stages/21_stage9_closeout_and_stage10_handoff.md` | tail | filename is stage-transition style, content is valid; name may look unusual | keep, rely on map index |

## Policy
- Do not delete historical docs without explicit owner approval.
- Keep active docs (`README`, `doc/00`, `doc/03`, `agile/sprint_current`) minimal and current.
- Prefer adding references in map/index docs instead of duplicating long historical lists.
