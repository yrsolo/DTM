# CAM-DEDUP-LEGACY-REMOVAL-V1 — Удаление дублей и legacy-хвостов

## Goal
Убрать параллельные реализации одних и тех же ролей (sync, repo, readmodel, etc.), которые тянутся из старых решений и засоряют архитектуру.

## Problem statement
В проекте одновременно живут старые и новые модули, что:
- создаёт путаницу “какой слой истина”
- увеличивает вероятность багов
- делает entrypoints толстыми

## Scope
- Найти дубли по ключевым ролям: sync, repository, readmodel builder/query, sheets renderer, notify.
- Для каждого дубля:
  - определить “истину” (keep)
  - определить migration plan и удалить/архивировать остальное
- Делать маленькими PR.

## Non-goals
- Не переписывать функционал, если можно удалить дубль без изменения поведения.

## Deliverables
- `docs/system/dedup_plan.md` (таблица: role → keep → remove → why → risk)
- серия небольших PR.

## Phases & tasks
### P01 — Identify
- T001: список дублей (файл/класс/использование)
- T002: выбрать keep/remove

### P02 — Remove
- T001: удалить неиспользуемое
- T002: smoke tests
- T003: обновить docs

## DoD
- Для каждой роли осталась одна реализация в runtime path.
- Уменьшены импорты legacy слоёв в entrypoints.