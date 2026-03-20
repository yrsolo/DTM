# Trigger Orchestration V2

This document defines target orchestration ownership for scheduled triggers.

Governing source:
- [../module-first-recovery/README.md](../module-first-recovery/README.md)

## Trigger ownership

| Trigger | Orchestration owner | Emitted commands | Expected result |
|---|---|---|---|
| `timer` | `platform.runtime` | `update_snapshot`, `render_timeline_sheet`, `render_designers_sheet` | accepted + queued batch |
| `morning` | `platform.runtime` | `send_reminders` | accepted + queued command |

## Rules

- triggers are orchestration-only
- trigger shells do not own business logic
- trigger orchestration may assemble command plans and enqueue them
- trigger orchestration must not become a second business layer
- trigger execution results should remain transport/status oriented
