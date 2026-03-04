# CAM-ENTRYPOINT-DEHYBRID-V1 — Убрать смешение legacy и modern путей (index/main не склеивают миры)

## Goal
Развести слои так, чтобы entrypoints перестали тянуть legacy `core/*` и вызывать друг друга:
- `index.py` не импортирует `core.*` и не вызывает `main.main`
- `index.py` → router → handlers → services
- `main.py` → job runner → jobs/services
- один “источник истины” для API: readmodel snapshot

## Problem statement
Сейчас entrypoints — гибрид: `index.py` и `main.py` одновременно используют:
- legacy core (planner/group_query/reminder/api_payload)
- modern src (ydb repos/services)
Это делает код запутанным и порождает круги зависимостей.

## Scope
- Вынести group_query в отдельный handler в `src/handlers/` (или `src/entrypoints/http/handlers/`).
- Вынести API v2 handler в `src/handlers/api_v2.py`, где он читает только readmodel.
- Удалить вызов main из index.
- main перестаёт собирать старый planner world в runtime ветке, если не нужен.

## Non-goals
- Не делать полный “тонкий main/index” (это отдельная кампания hygiene).
- Не переписывать доменные алгоритмы.

## Deliverables
- `index.py` только разбирает HTTP event и диспатчит handler.
- `main.py` только диспатчит job.
- Legacy core используется только в legacy режимах (явно помечено) или вынесен в отдельный namespace.

## Phases & tasks

### P01 — Stop index -> main coupling
- T001: Найти вызовы main из index и удалить.
- T002: В index сделать прямую маршрутизацию на handlers.

### P02 — Handlers separation
- T001: API v2 handler читает YDB readmodel (1 query).
- T002: group_query handler изолирован, не тянет planner внутрь index.
- T003: единый формат HttpRequest/HttpResponse DTO (если уже есть — использовать).

### P03 — De-legacy entrypoints
- T001: Запретить импорты `core.*` из `index.py`.
- T002: Из main убрать сборку planner deps из пути timer, если это legacy слой.
- T003: Если legacy остаётся — отделить в `src/legacy/*` и выключить по умолчанию.

### P04 — Evidence
- T001: smoke: /api/v2/frontend читает readmodel и отвечает
- T002: smoke: timer run не вызывает legacy planner

## DoD
- index.py не вызывает main и не импортирует core.*
- main.py не тащит legacy слой в стандартном timer path
- API v2 использует readmodel snapshot
