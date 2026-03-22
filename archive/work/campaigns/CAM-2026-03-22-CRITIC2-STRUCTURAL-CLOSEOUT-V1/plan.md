# CAM-2026-03-22-CRITIC2-STRUCTURAL-CLOSEOUT-V1

## Goal

Close the highest-signal remaining structural critiques without speculative redesign:

- reduce `snapshot` runtime-binding gravity,
- make `access_api` read ownership calmer and less dispatcher-shaped,
- remove the leftover job-catalog public shape from `rendering`.

## Scope

1. Re-slice `snapshot` internals into role-true builders instead of one visible `runtime_binding` hub.
2. Reduce obvious dispatcher gravity in `access_api` without breaking active HTTP seams.
3. Simplify `rendering.public` so the canonical surface is the execution API plus queue handlers, not named jobs.

## Non-goals

- no product behavior change,
- no schema/storage migration,
- no speculative rewrite of the whole runtime shell layer,
- no changes to the blocked production attachments live-smoke campaign.

## Tasks

1. Register trust/evidence against current runnable code.
2. Refactor `snapshot` internal builders.
3. Tighten `access_api`/`rendering` surfaces and run targeted checks.
