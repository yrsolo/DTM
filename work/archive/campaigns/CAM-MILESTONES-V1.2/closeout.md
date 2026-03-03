# CAM-MILESTONES-V1.2 Closeout

## Goal
Закалить контур milestones_v: убрать лишние legacy writes, гарантировать non-empty milestones и повысить консистентность bump-пути.

## Delivered
- Добавлен флаг `WRITE_LEGACY_MILESTONES` (default off), legacy write выключен по умолчанию.
- Builder получил hard-guard: synthetic `start`, если milestones_v пуст.
- Sync получил assert на пустую запись milestones при version bump.
- Улучшен порядок операций version bump для best-effort консистентности без транзакций.
- Пройден пакет unit/smoke проверок и собраны evidence.

## Task List
- [x] `CAM-MILESTONES-V1.2-P01-T001`
- [x] `CAM-MILESTONES-V1.2-P01-T002`
- [x] `CAM-MILESTONES-V1.2-P01-T003`
- [x] `CAM-MILESTONES-V1.2-P02-T001`
- [x] `CAM-MILESTONES-V1.2-P02-T002`
- [x] `CAM-MILESTONES-V1.2-P03-T001`
- [x] `CAM-MILESTONES-V1.2-P03-T002`
- [x] `CAM-MILESTONES-V1.2-P04-T001`
- [x] `CAM-MILESTONES-V1.2-P04-T002`
- [x] `CAM-MILESTONES-V1.2-P04-T003`
- [x] `CAM-MILESTONES-V1.2-P04-T004`

## Evidence
- `work/roadmap/campaigns/CAM-MILESTONES-V1.2/evidence.md`
