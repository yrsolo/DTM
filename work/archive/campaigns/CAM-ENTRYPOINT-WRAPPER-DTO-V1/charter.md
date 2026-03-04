# CAM-ENTRYPOINT-WRAPPER-DTO-V1 - Replace Remaining `**kwargs` Wrappers with DTO

## Goal
Finish hygiene for runtime entry wrappers by replacing `**kwargs` compatibility entrypoints with explicit request DTO flow, while keeping behavior unchanged.

## Scope
- `src/entrypoints/runtime/planner_runtime_entry.py`
- `main.py`
- `src/entrypoints/http/runtime_execution.py`
- `index.py` runtime handoff wiring
- tests touched by these boundaries

## Deliverables
- Canonical runtime entry accepts typed request object (no `**kwargs` in runtime entry method).
- `main.py` remains thin and explicit (no `**kwargs` passthrough).
- HTTP runtime execution passes typed request to runtime entry.
- Smoke tests green.

## Non-goals
- No business logic changes.
- No source-selection/pipeline behavior changes.
- No API contract changes.

## DoD
- No `**kwargs` in active runtime entry methods (`main.py`, runtime entry canonical method).
- Runtime behavior and smoke pack unchanged.
