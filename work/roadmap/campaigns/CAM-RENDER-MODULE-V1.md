# CAM-RENDER-MODULE-V1

## Goal
Build a new render module with pure render plan generation from Snapshot Engine and separate Sheets writer adapter.

## Scope
- New render module skeleton and contracts.
- `build_plan` pure logic from Snapshot query output.
- Batch write adapter for Google Sheets target.

## Phases and Tasks
### P01 - Module skeleton
- P01-T001: Add `src/render/{model,usecase,sheets_adapter,job}.py` + `__init__.py`.

### P02 - Pure render use case
- P02-T001: Implement task selection via Snapshot Query Engine.
- P02-T002: Build `RenderPlan` values/formats without IO.

### P03 - Sheets writer
- P03-T001: Implement batch values/formats write.
- P03-T002: Add small smoke path for reduced range.

### P04 - Runtime wiring
- P04-T001: Add `render_v2` mode wiring.
- P04-T002: Disable legacy render path for standard runtime modes.

### P05 - Tests
- P05-T001: Unit tests for `RenderUseCase.build_plan`.
- P05-T002: Adapter test for batching logic.

## DoD
- Render runtime path uses Snapshot Engine as source.
- No imports from `core/*`/planner in `src/render`.
