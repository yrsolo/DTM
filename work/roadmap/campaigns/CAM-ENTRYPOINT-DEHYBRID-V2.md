# CAM-ENTRYPOINT-DEHYBRID-V2 - Razvyazat index/main ot legacy core i drug ot druga

## Goal
Ubrat smeshenie legacy i modern putey v entrypoints:
- `index.py` ne vyzyvaet `main` i ne importiruet `core.*`
- API v2 handler chitaet tolko readmodel snapshot (1 query)
- group_query vynesen v otdelnyy handler
- `main.py` timer path ne sobiraet legacy planner world

## DoD
- `index.py`: tolko parse -> dispatch -> response
- `main.py`: tolko run_mode -> job
- entrypoints ne importiruyut `core/*` (legacy) v standartnom rezhime
- API v2: 1 zapros k readmodel

## PHASE P01 - Stop index -> main coupling
### CAM-ENTRYPOINT-DEHYBRID-V2-P01-T001
- Nayti i udalit vyzov `main.main()` iz index path.
- Zamenit na pryamoy vyzov handlerov/routera.

### CAM-ENTRYPOINT-DEHYBRID-V2-P01-T002
- Udalit import `main` iz `index.py`.

## PHASE P02 - Remove legacy imports from index
### CAM-ENTRYPOINT-DEHYBRID-V2-P02-T001
- Nayti vse importy `core.*` v `index.py`:
  - api_payload_v2, group_query, reminder i t.p.
- Zamenit na analogi v `src/handlers/*` ili sozdat minimalnye handlers.

### CAM-ENTRYPOINT-DEHYBRID-V2-P02-T002 - API v2 handler fast path
- Sozdat/obnovit `src/handlers/api_v2_frontend.py`:
  - read readmodel row
  - apply filters
  - return payload
- Zapret: nikakoy planner/Sheets/tasks rebuild vnutri handler.

### CAM-ENTRYPOINT-DEHYBRID-V2-P02-T003 - Group query handler isolation
- Vynesti group query v `src/handlers/group_query.py`.
- index router dispatchit na nego po konkretnomu route.
- Zapret: group query ne dolzhen tashchit planner world v API v2 handler.

## PHASE P03 - Remove legacy planner from main timer path
### CAM-ENTRYPOINT-DEHYBRID-V2-P03-T001
- Nayti v main timer path sozdanie:
  - `build_planner_dependencies(...)`
  - `GoogleSheetPlanner(...)`
  - `_apply_task_source_switches(...)` (mutation injection)
- Ubrat iz standartnogo timer rezhima.

### CAM-ENTRYPOINT-DEHYBRID-V2-P03-T002
- Esli planner nuzhen dlya legacy rezhimov - vynesti v otdelnyy legacy mode:
  - `mode=legacy_planner_*`
  - vyklyucheno po umolchaniyu.

## PHASE P04 - Docs + evidence
### CAM-ENTRYPOINT-DEHYBRID-V2-P04-T001
- Obnovit `docs/system/entrypoints_index_main.md`:
  - index routes -> handlers
  - main modes -> jobs
  - legacy vydelen otdelno

### CAM-ENTRYPOINT-DEHYBRID-V2-P04-T002
- Evidence: log/grep podtverzhdenie "index.py does not import core.*; index does not import main".
