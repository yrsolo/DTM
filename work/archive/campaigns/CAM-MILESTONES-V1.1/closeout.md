# CAM-MILESTONES-V1.1 Closeout

## Goal
Закрепить versioned milestones как единый источник истины для readmodel и безопасный sync/write-path.

## Delivered
- Подтверждена схема `dtm_task_milestones_v` и связь с активной версией задачи.
- Убран глобальный `DELETE` в milestones-потоке; оставлены только scoped операции.
- Добавлена утилита миграции текущих milestones в versioned таблицу.
- Подтверждён smoke-путь `sync -> build -> api/v2`.

## Task List
- [x] `CAM-MILESTONES-V1.1-P01-T001`
- [x] `CAM-MILESTONES-V1.1-P01-T002`
- [x] `CAM-MILESTONES-V1.1-P01-T003`
- [x] `CAM-MILESTONES-V1.1-P02-T001`
- [x] `CAM-MILESTONES-V1.1-P02-T002`
- [x] `CAM-MILESTONES-V1.1-P02-T003`
- [x] `CAM-MILESTONES-V1.1-P02-T004`
- [x] `CAM-MILESTONES-V1.1-P03-T001`
- [x] `CAM-MILESTONES-V1.1-P03-T002`
- [x] `CAM-MILESTONES-V1.1-P03-T003`
- [x] `CAM-MILESTONES-V1.1-P04-T001`
- [x] `CAM-MILESTONES-V1.1-P04-T002`
- [x] `CAM-MILESTONES-V1.1-P05-T001`
- [x] `CAM-MILESTONES-V1.1-P05-T002`
- [x] `CAM-MILESTONES-V1.1-P05-T003`

## Evidence
- `work/archive/campaigns/CAM-MILESTONES-V1.1/evidence.md`
