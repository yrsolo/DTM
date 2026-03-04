# CAM-ENTRYPOINT-REFORM-V1 — Тонкие entrypoints: index.py и main.py

## Goal
Сделать `index.py` и `main.py` тонкими, понятными, без бизнес-логики и без инфраструктурных деталей.

## Problem statement
В entrypoints сейчас смешаны:
- parsing event,
- routing,
- orchestration пайплайна,
- доступ к YDB/Sheets,
- флаги миграции,
- обработка ошибок и качество данных.

## Scope
- `index.py` оставить как thin HTTP router:
  - parse event → dispatch → return response
- `main.py` оставить как thin job runner:
  - parse run_mode → call job

Вынести:
- HTTP handlers → `src/entrypoints/http/handlers/*` или `src/handlers/*`
- jobs → `src/entrypoints/jobs/*`
- bootstrap → `src/app/bootstrap.py` (использует cfg из CAM-CONFIG-REFORM-V0)

## Non-goals
- Не менять бизнес поведение пайплайна.
- Не менять API payload структуру.

## Deliverables
- `src/entrypoints/http/index_handler.py` (или аналог)
- `src/entrypoints/jobs/{timer_job.py,db_migrate_job.py,...}`
- `index.py` и `main.py` становятся thin wrappers.

## Phases & tasks
### P01 — HTTP entrypoint
- T001: Извлечь parsing event в `src/entrypoints/http/event_parser.py`
- T002: Извлечь routing table в `src/entrypoints/http/router.py`
- T003: `index.py` делегирует в router и handlers.

### P02 — Job entrypoint
- T001: `main.py` выбирает job по cfg/run_mode
- T002: job реализован отдельным модулем и вызывает use-cases через ctx

## DoD
- `index.py` ≤ 150 строк, `main.py` ≤ 200 строк (ориентир).
- В entrypoints нет импорта YDB schema/SQL, нет парсинга таймингов, нет readmodel builder логики.