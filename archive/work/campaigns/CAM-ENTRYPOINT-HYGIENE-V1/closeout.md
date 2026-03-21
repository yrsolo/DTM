# CAM-ENTRYPOINT-HYGIENE-V1 Closeout

## Result
- Replaced hyperfunction argument sheets with typed DTOs in active entrypoint/runtime path:
  - `HttpDispatchHandlersContext`
  - `RuntimeExecutionContext` + `RuntimeExecutionRequest`
  - `PlannerPipelineContext` + `PlannerPipelineRequest`
  - `SyncReadmodelPipelineContext` + `SyncReadmodelPipelineRequest`
  - `GroupQueryHandlerContext` + `GroupQueryHandlerRequest`
- `index.py` and runtime wiring now compose context/request objects instead of passing long keyword lists.

## Verification
- Signature audit confirms no parameter-sheet signatures in the active runtime methods touched by this campaign.
- Smoke pack is green:
  - `tests.api.test_frontend_api_routing`
  - `tests.services.test_pipeline_runtime`
  - `tests.services.test_planner_pipeline_job`
  - `tests.services.test_sync_source_hash_gate`

## Notes
- `main.py` and `run_planner_runtime(**kwargs)` remain intentionally thin compatibility wrappers.
