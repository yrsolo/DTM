# CAM-2026-03-21-CRITIQUE-CLOSEOUT-V1

## Smell
- owner critique in `agent/owner_inputs/crit.md` points to three still-visible transition seams:
  - `access_api` still reads through a thin public/module facade into a browser-route dispatcher
  - `reminders` still exports a job-shaped public seam
  - beauty audit language overclaims showcase-grade finish relative to the current code

## Target ideal
- `access_api` reads as the owner of the primary browser read surface, not as a thin facade over route handlers
- `reminders` no longer exports `SendRemindersJob` as a public seam
- active beauty docs describe the repo as strong-but-not-finished where that is what the code actually shows

## Kill criteria
- `src/contexts/access_api/public.py` exports one clear browser read entry instead of a decorative facade
- `src/contexts/reminders/public.py` no longer exports `get_send_reminders_job`
- `docs/architecture/module-first-recovery/repo-beauty-audit-2026-03-21.md` no longer claims showcase-grade closeout while `access_api`, `snapshot`, and `bootstrap` still have visible transitional weight

## Out of scope
- deep `snapshot` redesign
- large `bootstrap` decomposition
- full internal split of `PrimaryTaskListReadApi`
