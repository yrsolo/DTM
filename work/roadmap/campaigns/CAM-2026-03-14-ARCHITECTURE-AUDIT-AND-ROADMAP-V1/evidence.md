# Evidence - CAM-2026-03-14-ARCHITECTURE-AUDIT-AND-ROADMAP-V1

## Trust gate
- source: active runtime code, current runtime docs, direct static inspection of active modules
- last_verified_at: 2026-03-14
- verified_by: Codex
- evidence:
  - `index.py`
  - `src/app/bootstrap.py`
  - `src/entrypoints/index_dispatcher.py`
  - `src/entrypoints/http/http_shell.py`
  - `src/entrypoints/http/router.py`
  - `src/entrypoints/http/frontend_v2_handler.py`
  - `src/entrypoints/http/runtime_execution.py`
  - `src/entrypoints/runtime/runtime_shell.py`
  - `src/entrypoints/runtime/planner_runtime_entry.py`
  - `src/snapshot_engine/query_engine.py`
  - `src/worker/worker.py`
  - `src/worker/dispatcher.py`
  - `docs/system/architecture_values.md`
  - current runtime docs in `docs/system/*` and `docs/snapshot_engine/*`
- trust_level: high
- notes:
  - this audit is based on the active runtime path and current docs only
  - archived/legacy docs were not used as the source of truth for the verdict

## Static complexity snapshot
- `index.py` - 53 lines
- `src/app/bootstrap.py` - 177 lines
- `src/entrypoints/index_dispatcher.py` - 141 lines
- `src/entrypoints/http/http_shell.py` - 329 lines
- `src/entrypoints/http/router.py` - 60 lines
- `src/entrypoints/http/frontend_v2_handler.py` - 436 lines
- `src/entrypoints/runtime/runtime_shell.py` - 16 lines
- `src/entrypoints/runtime/planner_runtime_entry.py` - 351 lines
- `src/snapshot_engine/query_engine.py` - 47 lines
- `src/worker/worker.py` - 205 lines
- `src/worker/dispatcher.py` - 66 lines

## Top-level verdict
- the project is materially closer to the target architecture than it feels from a quick glance
- `index.py` itself is not the main problem; it is already thin, lazy, and import-safe
- the cleanest parts are the snapshot read-side core and the command/worker direction
- the real architectural dirt sits at the boundary/orchestration layer:
  - `build_app_context()`
  - `IndexDispatcher`
  - `HttpShell`
  - `FrontendV2Handler`
  - `planner_runtime_entry`
- the system is not "architecturally wrong everywhere"; it is a mostly healthy core wrapped in noisy transport and composition layers

## Subsystem scorecard

### Entry boundary purity
- rating: `acceptable but transitional`
- clean:
  - `index.py` is thin and lazy
  - `HttpRouter` is small and understandable
- impure:
  - `IndexDispatcher` mixes event-kind dispatch with HTTP outer tracing/header surgery
  - `HttpShell` mixes transport translation, runtime fallback, metrics, tracing, and response decoration
- target shape:
  - thin event router
  - thin HTTP shell
  - observability/runtime-fallback extracted into dedicated collaborators

### Composition root quality
- rating: `needs refactor`
- clean:
  - config is typed and centralized
  - bootstrap is the recognized composition root
- impure:
  - `build_app_context()` reads many env secrets and assembles metrics, queue, status store, producer, dispatcher, worker, and concrete jobs in one function
  - composition root doubles as a feature-wiring matrix
- target shape:
  - shallow composition root calling focused factories for metrics, queue, worker, and jobs

### Separation of transport/application/domain concerns
- rating: `acceptable but transitional`
- clean:
  - snapshot query engine is separate from HTTP shell
  - worker dispatcher is separate from queue shell
- impure:
  - `FrontendV2Handler` still owns too much request algorithm and observability logic
  - runtime execution path still wires user-notification behavior in transport-adjacent layer
- target shape:
  - handlers coordinate collaborators, not own end-to-end algorithms

### Read-side architecture quality
- rating: `good`
- clean:
  - snapshot-first read side is clear
  - `SnapshotQueryEngine` is small and focused
  - browser auth and masking remain boundary concerns
- debt:
  - read boundary is still harder to reason about than the core because `FrontendV2Handler` is too large
- target shape:
  - keep current snapshot-first contour
  - decompose handler without changing read-side model

### Async command / event-driven quality
- rating: `good`
- clean:
  - mutation path is queue-backed
  - worker and dispatcher are explicit
  - trigger fan-out and command types are concrete and understandable
- debt:
  - still some coupling through bootstrap assembly
- target shape:
  - keep command-driven mutation contour, simplify assembly around it

### Dependency direction / coupling
- rating: `acceptable but transitional`
- clean:
  - domain/query pieces are mostly isolated from transport
- impure:
  - transitional runtime path imports concrete adapters and use-cases directly
  - bootstrap produces broad concrete dependency graph in one place
- target shape:
  - more explicit factories and smaller seams between runtime bridge and concrete adapters

### Transitional legacy leakage
- rating: `needs refactor`
- clean:
  - planner-era story is no longer the official architecture
- impure:
  - `planner_runtime_entry.py` is still a large compatibility adapter
  - `runtime_shell` and HTTP runtime execution still route through it
- target shape:
  - compatibility path kept but clearly reduced and boxed in

### Operability / observability cost and placement
- rating: `needs refactor`
- clean:
  - observability abstractions exist
  - past metric spam issue was partially corrected
- impure:
  - outer tracing/header decoration still lives in boundary orchestrators
  - transport code remains too aware of observability mechanics
- target shape:
  - observability retained, but with lower transport-layer noise and lower hot-path coupling

### Testability and local reasoning cost
- rating: `acceptable but transitional`
- clean:
  - small components like query engine and dispatcher are easy to reason about
  - import-safety was improved
- impure:
  - a maintainer still has to read too much shell/bootstrap code to understand one request end-to-end
- target shape:
  - smaller boundary classes with narrower responsibilities

### Runtime simplicity for a new maintainer
- rating: `needs refactor`
- clean:
  - the target story is now documented and mostly true
- impure:
  - the runtime still looks more complex than it actually is because orchestration code is concentrated in a few large files
- target shape:
  - smaller entry/runtime components
  - composition root that reads like assembly, not business logic

## Prioritized findings

### F01 - `index.py` is not the real problem
- severity: medium
- where: `index.py`
- why it matters:
  - team intuition currently over-focuses on `index.py`
- actual finding:
  - `index.py` is already thin, lazy, and import-safe
  - it is acceptable for the target shape
- practical conclusion:
  - do not spend the first refactor wave on `index.py` itself

### F02 - `build_app_context()` is the biggest composition-root smell
- severity: high
- where: `src/app/bootstrap.py`
- principle violated:
  - composition root only
- current cost:
  - one function wires secrets, metrics sinks, queue producer, status store, command dispatcher, worker, and jobs
  - broad blast radius for any assembly change
  - hard to reason about dependency graph in slices
- timing:
  - worth touching soon

### F03 - HTTP boundary orchestration is too thick
- severity: high
- where:
  - `src/entrypoints/index_dispatcher.py`
  - `src/entrypoints/http/http_shell.py`
  - `src/entrypoints/http/runtime_execution.py`
- principle violated:
  - thin entrypoints / transport shells
- current cost:
  - tracing, metrics, runtime fallback, and header plumbing crowd request flow
  - harder to understand what is transport vs runtime behavior vs observability
- timing:
  - best first refactor wave

### F04 - `FrontendV2Handler` is doing boundary work and orchestration work at once
- severity: high
- where: `src/entrypoints/http/frontend_v2_handler.py`
- principle violated:
  - handlers should coordinate collaborators, not be mini orchestrators
- current cost:
  - parsing, access resolution, cache orchestration, payload build, masking, metrics, debug headers, and response shaping live together
  - high cognitive load for any frontend API change
- timing:
  - second or third wave, after boundary cleanup

### F05 - Transitional runtime adapter still carries too much weight
- severity: medium
- where:
  - `src/entrypoints/runtime/planner_runtime_entry.py`
  - `src/entrypoints/runtime/runtime_shell.py`
- principle violated:
  - transitional adapter should not feel like runtime center
- current cost:
  - explicit runtime modes still route through a large, concrete, planner-era compatibility function
- timing:
  - after entrypoint and bootstrap cleanup

### F06 - The project core is cleaner than it feels
- severity: positive finding
- where:
  - `src/snapshot_engine/query_engine.py`
  - `src/worker/dispatcher.py`
  - queue-backed mutation contour overall
- why it matters:
  - refactor strategy should preserve this clean core instead of rewriting it
- practical conclusion:
  - do not start with deep read-side redesign or event-model churn

## Explicit answers
- Is `index.py` actually dirty?
  - No. It is mostly fine and already close to the intended thin-entrypoint shape.
- If not, where is the real dirt?
  - In boundary orchestration and composition:
    - `build_app_context()`
    - `IndexDispatcher`
    - `HttpShell`
    - `FrontendV2Handler`
    - `planner_runtime_entry.py`
- What should we touch first?
  - First: entrypoint/runtime boundary cleanup
  - Second: bootstrap/composition-root cleanup
  - Third: frontend handler decomposition
