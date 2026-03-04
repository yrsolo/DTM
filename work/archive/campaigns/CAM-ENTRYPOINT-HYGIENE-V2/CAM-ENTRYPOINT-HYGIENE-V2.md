# CAM-ENTRYPOINT-HYGIENE-V2 - Unichtozhit giperfunktsii: Context + DTO + Router/Pipeline objects

## Goal
Izbavitsya ot "prostyney parametrov" i neocherednykh perenaznacheniy:
- hyperfunctions prevrashchayutsya v obekty s ctx
- vmesto peredachi funktsiy/lyambda - yavnye servisy i klassy
- graf zavisimostey statichen i ponyaten IDE

## DoD
- Net funktsiy/fabrik, prinimayushchikh desyatki parametrov.
- Net runtime mutation injection (perenaznacheniya repo vglub obektov).
- Navigatsiya IDE: route -> handler -> service -> repo bez prygkov po lyambdam.

## PHASE P01 - DTO
### CAM-ENTRYPOINT-HYGIENE-V2-P01-T001
- Vvesti `HttpRequest` i `HttpResponse` DTO (esli uzhe est - ispolzovat).
- Vvesti `RunRequest` DTO dlya main/jobs.

### CAM-ENTRYPOINT-HYGIENE-V2-P01-T002
- Perevesti router/handlers na DTO, ubrat ad-hoc dict passing.

## PHASE P02 - AppContext as single dependency carrier
### CAM-ENTRYPOINT-HYGIENE-V2-P02-T001
- Ubeditsya, chto `AppContext` soderzhit:
  - cfg
  - ydb client + repos
  - sheet reader
  - services (sync/readmodel/render/notify)
  - logger/clock
- Zapret: peredacha creds/konfigov otdelnymi parametrami gluboko v funktsii.

### CAM-ENTRYPOINT-HYGIENE-V2-P02-T002
- V bootstrap vybrat policy realizatsii odin raz (injection), bez dalneyshikh perenaznacheniy.

## PHASE P03 - Replace build_*_handlers hyperfunction with Router object
### CAM-ENTRYPOINT-HYGIENE-V2-P03-T001
- Udalit/deprekate `build_http_dispatch_handlers(...)`.
- Realizovat `HttpRouter(ctx)`:
  - soderzhit route table
  - `dispatch(req) -> resp`
- Handlers kak klassy:
  - `FrontendV2Handler(ctx)`
  - `GroupQueryHandler(ctx)`
  - `HealthHandler(ctx)`

### CAM-ENTRYPOINT-HYGIENE-V2-P03-T002
- `index.py`: sozdat ctx, router i vyzvat dispatch.
- Nikakikh lyambd v parametrah.

## PHASE P04 - Replace run_ydb_sync_readmodel_pipeline hyperfunction with Pipeline object
### CAM-ENTRYPOINT-HYGIENE-V2-P04-T001
- Vynesti `run_ydb_sync_readmodel_pipeline(...)` v klass:
  - `TimerPipeline(ctx).run(run_request)`
- Vnutri pipeline:
  - snapshot_reader iz ctx
  - sync_service iz ctx
  - readmodel_builder iz ctx
  - mapper iz ctx
- Zapret: peredavat safe_print/read_source_snapshot/mapper kak argumenty.

### CAM-ENTRYPOINT-HYGIENE-V2-P04-T002
- Perenesti `_task_to_operational_payload` iz main v mapper module:
  - `src/services/mappers/task_payload_mapper.py`
- Pokryt testom (minimum).

## PHASE P05 - Remove mutation injection
### CAM-ENTRYPOINT-HYGIENE-V2-P05-T001
- Udalit `_apply_task_source_switches` ili zamenit na bootstrap selection.
- Zapret: `obj.a.b.repo = repo` posle sozdaniya obektov.

## PHASE P06 - Evidence
### CAM-ENTRYPOINT-HYGIENE-V2-P06-T001
- Evidence: poisk v kode:
  - net `build_http_dispatch_handlers(` v runtime
  - net funktsiy s >7 parametrov v entrypoints/services (minimalnyy grep rule)
