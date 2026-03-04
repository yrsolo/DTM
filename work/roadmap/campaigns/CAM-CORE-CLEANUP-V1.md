# CAM-CORE-CLEANUP-V1 — Core = домен, без инфраструктуры

## Goal
Оставить в `src/core/` только доменную логику и модели. Убрать из core всё техническое.

## Problem statement
Папка core сейчас воспринимается как “всё подряд”. Это разрушает границы и усложняет рефакторинг.

## Scope
- Определить список “допустимых” вещей в core:
  - доменные модели
  - чистые функции нормализации (восстановление года milestones, парсинг этапов)
  - правила и вычисления без IO
- Всё, что читает/пишет внешние системы → adapters/services/entrypoints

## Non-goals
- Не переписывать алгоритмы, если они корректны.
- Не внедрять сложные DDD паттерны.

## Deliverables
- Чёткая структура `src/core/*`
- Правила импорта (lint/grep): в core запрещены SDK клиенты/HTTP/YDB/Sheets/TG.
- Док: `docs/system/core_boundaries.md`

## Phases & tasks
### P01 — Inventory & classification
- T001: Список модулей core → classify: domain/application/infra
- T002: План переносов (map: file → new location)

### P02 — Move + stabilize
- T001: Перенести infra куски из core в adapters/services
- T002: Обновить импорты и тесты

## DoD
- `src/core` не импортирует внешние SDK.
- Domain тестируется без environment.