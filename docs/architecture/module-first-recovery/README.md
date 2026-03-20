# Module-First Recovery

This folder is the primary normative architecture canon for the next DTM recovery wave.

It supersedes `docs/architecture/recovery/README.md` as the active architecture reading path while preserving the earlier recovery set as historical precedent.

## Start here

- [goals-and-principles.md](goals-and-principles.md)
- [current-scenarios.md](current-scenarios.md)
- [target-system-map.md](target-system-map.md)
- [publication-model.md](publication-model.md)
- [publication-states.md](publication-states.md)
- [ownership-and-boundaries.md](ownership-and-boundaries.md)
- [anti-fake-modularity-rules.md](anti-fake-modularity-rules.md)
- [top-path-readability.md](top-path-readability.md)
- [target-folder-structure.md](target-folder-structure.md)
- [runtime-canon.md](runtime-canon.md)
- [migration-rules.md](migration-rules.md)
- [reserve-capabilities.md](reserve-capabilities.md)
- [delta-audit-template.md](delta-audit-template.md)
- [../../integrations/attachments/frontend-card-publication.md](../../integrations/attachments/frontend-card-publication.md)

## Program control

- [implementation-order.md](implementation-order.md)
- [success-criteria.md](success-criteria.md)
- [checklists/final-review.md](checklists/final-review.md)
- [notes-for-maintainers.md](notes-for-maintainers.md)

## Main stance

- Active system is read through `entrypoint -> platform.runtime -> owning module`.
- The main browser read-side is the primary task-list payload with embedded card data and attachments.
- Attachment publication means visibility in that primary read-model, not upload acceptance or preview completion alone.
- Attachment readiness/status is an operational signal that tells the frontend when to refetch the main task-list payload.
- `platform.runtime` stays neutral and owns runtime concerns plus publication aftermath only.
- `telegram_interaction` remains in the codebase, but as a reserve, isolated, low-maintenance capability.
- Fake modularity is forbidden: wrappers, facades, or dispatchers count only if ownership moves and the old path dies.

## Reading policy

Use this folder when:
- opening a new architecture campaign
- deciding whether a change improves or worsens ownership
- checking whether a bridge should be removed instead of extended
- validating that browser read behavior is organized around the primary task-list payload

Current descriptive evidence still lives in:
- `docs/architecture/runtime/module-map.md`
- `docs/architecture/runtime/modularity-audit-2026-03-19.md`
- `docs/architecture/recovery/README.md`

Those files describe history or current state.
This folder defines the active canon.
