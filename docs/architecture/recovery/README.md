# Architecture Recovery

This folder is the canonical architecture program for the next DTM recovery wave.

It replaces `docs/architecture/runtime/modular-monolith-v2.md` as the primary normative source for future architecture work.

## Start here

- [goals-and-principles.md](goals-and-principles.md)
- [target-system-map.md](target-system-map.md)
- [ownership-and-boundaries.md](ownership-and-boundaries.md)
- [runtime-canon.md](runtime-canon.md)
- [migration-rules.md](migration-rules.md)
- [../../integrations/attachments/frontend-card-publication.md](../../integrations/attachments/frontend-card-publication.md) for the governing attachment publication scenario

## Program control

- [implementation-order.md](implementation-order.md)
- [success-criteria.md](success-criteria.md)
- [checklists/final-review.md](checklists/final-review.md)
- [notes-for-maintainers.md](notes-for-maintainers.md)

## Reading policy

Use this folder when:
- opening a new architecture-recovery campaign
- deciding whether a change improves or worsens ownership
- checking whether an old bridge should be removed instead of wrapped again

For attachment-related waves, read the frontend card publication scenario before decomposing work:
- `attachments mutation -> platform/runtime invalidation/orchestration -> snapshot projection -> access_api cached delivery`

Current descriptive evidence still lives in:
- `docs/architecture/runtime/module-map.md`
- `docs/architecture/runtime/modularity-audit-2026-03-19.md`

Those files describe the current system state.
This folder defines the target canon.
