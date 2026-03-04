# CAM-ENTRYPOINT-AND-PIPELINE-DEMONSTER-V1

## Goal
- Убрать функциональные `*Context` dataclass и lambda wiring в entrypoints/pipeline.
- Перейти на канонический `AppContext` + class-based route/handler/pipeline.

## Anti-goals
- Не добавлять новые `*Context` dataclass с callback/factory полями.
- Не передавать функции как параметры "для гибкости".
- Не переносить монстро-сигнатуры между файлами без упрощения.

## DoD
- В `index.py` и `src/entrypoints/http/*` нет функциональных context dataclass и inline lambda wiring.
- В `src/services/pipeline_runtime.py` нет `SyncReadmodelPipelineContext`.
- Канонический runtime:
  - `HttpRouter(ctx).dispatch(req)`
  - `TimerPipeline(ctx).run(run_request)`
- IDE navigation: route -> handler class -> service -> repo.

## Phases
- P01: Inventory monsters (`docs/system/demonster_inventory.md`)
- P02: Normalize `AppContext` and runtime dependency surface
- P03: HTTP demonster (`index.py`, `router.py`, handlers)
- P04: Pipeline demonster (`timer_pipeline.py`, mapper extraction, remove pipeline context)
- P05: Remove runtime mutation injection (`_apply_task_source_switches` contour)
- P06: Tests + grep gates + docs/evidence
