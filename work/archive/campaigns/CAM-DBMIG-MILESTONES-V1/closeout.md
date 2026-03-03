# CAM-DBMIG-MILESTONES-V1 Closeout

## Goal
Перевести контур milestones на versioned storage и закрепить readmodel как единый читаемый источник.

## Delivered
- Добавлена/закреплена схема `dtm_task_milestones_v`.
- Sync/write-path переведён на version-aware поведение.
- Readmodel builder читает milestones по `(task_id, current_version)`.
- Выполнен backfill и проверка миграции на выборке.
- Закрыт пакет тестов и smoke/evidence.

## Task List
- [x] `CAM-DBMIG-MILESTONES-V1-P01-T001`
- [x] `CAM-DBMIG-MILESTONES-V1-P01-T002`
- [x] `CAM-DBMIG-MILESTONES-V1-P01-T003`
- [x] `CAM-DBMIG-MILESTONES-V1-P02-T001`
- [x] `CAM-DBMIG-MILESTONES-V1-P02-T002`
- [x] `CAM-DBMIG-MILESTONES-V1-P02-T003`
- [x] `CAM-DBMIG-MILESTONES-V1-P03-T001`
- [x] `CAM-DBMIG-MILESTONES-V1-P03-T002`
- [x] `CAM-DBMIG-MILESTONES-V1-P03-T003`
- [x] `CAM-DBMIG-MILESTONES-V1-P04-T001`
- [x] `CAM-DBMIG-MILESTONES-V1-P04-T002`
- [x] `CAM-DBMIG-MILESTONES-V1-P05-T001`
- [x] `CAM-DBMIG-MILESTONES-V1-P05-T002`
- [x] `CAM-DBMIG-MILESTONES-V1-P05-T003`

## Evidence
- `work/archive/campaigns/CAM-DBMIG-MILESTONES-V1/evidence.md`
