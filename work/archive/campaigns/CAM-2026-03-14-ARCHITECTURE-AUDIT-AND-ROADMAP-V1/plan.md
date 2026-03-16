# CAM-2026-03-14-ARCHITECTURE-AUDIT-AND-ROADMAP-V1 Plan

## Summary

This campaign is analysis-only. It documents the current runtime shape, scores the main subsystems against target architecture values, and defines the recommended refactor order.

## Audit Model

### Dimensions
- entry boundary purity
- composition root quality
- separation of transport/application/domain concerns
- read-side architecture quality
- async command/event-driven quality
- dependency direction and coupling
- transitional legacy leakage
- operability/observability cost and placement
- testability and local reasoning cost
- runtime simplicity for a new maintainer

### Rating scale
- `good`
- `acceptable but transitional`
- `needs refactor`
- `architecturally wrong for target shape`

## Recommended Refactor Roadmap

### Wave 1 - Entrypoint Boundary Cleanup
- goal: make transport boundaries truly thin and easier to reason about
- target subsystems:
  - `src/entrypoints/index_dispatcher.py`
  - `src/entrypoints/http/http_shell.py`
  - `src/entrypoints/http/router.py`
  - `src/entrypoints/http/runtime_execution.py`
- key changes:
  - move outer tracing/header plumbing out of dispatcher/shell orchestration branches
  - separate HTTP read handling from runtime-mode fallback handling
  - keep routing/transport translation distinct from observability decoration
  - remove transport-level error/reporting behavior that belongs in dedicated adapters
- acceptance:
  - `index.py` remains thin
  - `IndexDispatcher` becomes a small event-kind router
  - `HttpShell` focuses on request translation + response translation only
  - runtime fallback and outer instrumentation become dedicated collaborators
- intentionally not solved:
  - bootstrap wiring complexity
  - frontend handler size
  - transitional runtime adapter existence
- expected payoff:
  - clearer mental model for request flow
  - lower risk when changing HTTP behavior
  - easier testing of transport concerns in isolation

### Wave 2 - Bootstrap / Composition Root Cleanup
- goal: reduce `build_app_context()` from a large feature-wiring matrix into a real composition root
- target subsystems:
  - `src/app/bootstrap.py`
  - supporting bootstrap factory modules to be introduced under `src/app/` or `src/bootstrap/`
- key changes:
  - split config/env secret extraction from service assembly
  - split metrics sink/client assembly
  - split queue producer/status store/worker assembly
  - split job dispatcher construction from base app context construction
- acceptance:
  - `build_app_context()` becomes a shallow orchestration function
  - queue/metrics/job wiring each have their own factory seam
  - tests can validate factories independently without loading the full runtime graph
- intentionally not solved:
  - planner runtime compatibility path
  - frontend handler decomposition
- expected payoff:
  - lower coupling
  - better testability
  - easier future removal of transitional paths

### Wave 3 - Frontend Handler Decomposition
- goal: turn `FrontendV2Handler` into a thin boundary over dedicated collaborators
- target subsystem:
  - `src/entrypoints/http/frontend_v2_handler.py`
- key changes:
  - extract query parsing
  - extract cache eligibility/freshness orchestration
  - extract access application and masked/full response shaping
  - extract response/debug-header decoration
- acceptance:
  - handler coordinates collaborators instead of owning the full request algorithm
  - cache-hit and cache-miss paths are easy to read and test
  - tracing/debug concerns do not dominate the business flow
- intentionally not solved:
  - planner runtime adapter
  - frozen notify/telegram redesign
- expected payoff:
  - easier reasoning about read-path behavior
  - easier performance tuning
  - smaller blast radius for frontend API changes

### Wave 4 - Transitional Runtime Adapter Reduction
- goal: shrink planner-era compatibility logic until it is no longer an architectural center
- target subsystems:
  - `src/entrypoints/runtime/planner_runtime_entry.py`
  - `src/entrypoints/runtime/runtime_shell.py`
  - `src/entrypoints/http/runtime_execution.py`
- key changes:
  - isolate runtime-mode bridging from concrete job/use-case construction
  - remove direct concrete adapter assembly from the transitional runtime path where possible
  - reduce "one huge runtime function" behavior into smaller mode-specific execution seams
- acceptance:
  - transitional runtime path remains compatible but no longer feels like the conceptual center
  - explicit runtime modes become easier to map to concrete use-cases
- intentionally not solved:
  - frozen contours redesign
- expected payoff:
  - cleaner mental model
  - easier eventual retirement of planner-era adapter

### Wave 5 - Frozen Contour Review (Optional)
- goal: decide whether `telegram` / `notify` need architectural cleanup or should remain frozen
- trigger condition:
  - only open if they still distort active architecture or block earlier waves
- expected payoff:
  - avoid unnecessary rewrites while keeping room for later cleanup
