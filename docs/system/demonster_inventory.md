# Demonster Inventory (CAM-ENTRYPOINT-AND-PIPELINE-DEMONSTER-V1)

## Runtime Monsters Baseline

| File | Symbol/Pattern | Current Role | Target Replacement |
|---|---|---|---|
| `index.py` | `GroupQueryHandlerContext` + lambda notifier/loader wiring | Group query runtime composition | `GroupQueryHandler(AppContext)` with direct deps/services |
| `index.py` | `HttpRouterContext` | HTTP routing dependency bundle via callback fields | `HttpRouter(AppContext)` |
| `index.py` | `RuntimeExecutionContext` + notifier lambda | Runtime error boundary composition | direct `execute_runtime(...)` args or class without callback context |
| `src/entrypoints/http/router.py` | `HttpRouterContext` | callback-heavy router config | router class initialized by `AppContext` |
| `src/entrypoints/http/router.py` | `path_matches=lambda ...` | callback adapter in routing wiring | direct method/helper usage without lambda |
| `src/entrypoints/http/group_query_handler.py` | `GroupQueryHandlerContext` | callback bundle for parse/load/reply/notifier | handler class reading services from `AppContext` |
| `src/entrypoints/http/runtime_execution.py` | `RuntimeExecutionContext` | callback bundle for main/runtime/notifier/error boundary | direct typed execution contract without callback context |
| `src/entrypoints/http/frontend_v2_handler.py` | `FrontendV2HandlerContext` | callback-heavy V2 handler config | handler class with `AppContext` |
| `src/entrypoints/http/frontend_compat_handlers.py` | `FrontendRootHandlerContext` | callback-heavy root/doc handler config | handler class with `AppContext` |
| `src/services/pipeline_runtime.py` | `SyncReadmodelPipelineContext` | monolithic pipeline callback context | `TimerPipeline(AppContext)` + request DTO |
| `src/entrypoints/runtime/planner_runtime_entry.py` | pipeline lambda factories (`timer_pipeline_factory`, context/request factories) | indirection layer for pipeline wiring | direct `TimerPipeline(ctx).run(...)` |

## Inventory Notes
- `main.py` is already thin wrapper around `PlannerRuntimeRequest`, but runtime composition in `planner_runtime_entry.py` still relies on callback context objects.
- Existing `AppContext` is present, but runtime services are still mixed with callback/context wiring in entrypoints.
