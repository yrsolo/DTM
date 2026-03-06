# CAM-NOTIFY-MODULE-V1

## Goal
Introduce new notification module that uses Snapshot Engine only (`query -> format -> send`) and does not depend on legacy planner/core reminder stack.

## Scope
- New notify module skeleton and contracts.
- Runtime wiring for new reminder mode.
- Remove legacy notify path from standard runtime modes.

## Phases and Tasks
### P01 - Module skeleton
- P01-T001: Add `src/notify/{model,usecase,formatter,telegram_sender,job}.py` + `__init__.py`.

### P02 - Use case
- P02-T001: Implement `ReminderUseCase.run(req)` using Snapshot Engine query.
- P02-T002: Support window/status/default active-status policy and grouping by owner.

### P03 - Formatter and sender
- P03-T001: Implement pure formatter.
- P03-T002: Implement telegram sender adapter.

### P04 - Runtime wiring
- P04-T001: Add `reminder_v2` mode wiring.
- P04-T002: Disable legacy reminder flow for standard runtime path.

### P05 - Tests
- P05-T001: Unit tests for selection/grouping/window/status.
- P05-T002: Snapshot tests for formatted message output.

## DoD
- Notify runtime path uses Snapshot Engine only.
- No imports from `core/*` or planner legacy modules inside `src/notify`.
