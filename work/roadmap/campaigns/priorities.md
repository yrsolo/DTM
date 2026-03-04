# priorities.md — Приоритеты кампаний (порядок запуска)

## Priority 0 (blockers for clean pipeline)
1) **CAM-CONFIG-REFORM-V0**  
   Почему: убирает хаос env/const, делает возможным чистый bootstrap и уменьшает if-ад в пайплайне.

2) **CAM-PIPELINE-CLEAN-SKELETON-V1**  
   Почему: фиксирует “чистый сценарий” и границы ответственности (use-cases vs entrypoints).

## Priority 1 (структурное облегчение entrypoints)
3) **CAM-ENTRYPOINT-REFORM-V1**  
   Почему: index/main перестают быть местом, где живёт архитектурная грязь.

## Priority 2 (доменная чистота)
4) **CAM-CORE-CLEANUP-V1**  
   Почему: закрепляет границы и снижает риск “всё подряд в core”.

## Priority 3 (снижение сложности и техдолга)
5) **CAM-DEDUP-LEGACY-REMOVAL-V1**  
   Почему: уменьшает параллельные реализации и ускоряет понимание кода. Лучше делать после того, как bootstrap/entrypoints стабилизированы.

## Notes
- Если в процессе CAM-CONFIG-REFORM-V0 обнаружатся критические legacy-дубли (например, два sync_service в runtime path), допускается сделать небольшой hotfix под CAM-DEDUP… в диапазоне “T900–T999” как вставку, но не разворачивать полностью кампанию раньше времени.
- Owner decision (2026-03-04): API v1 support is discontinued; roadmap and active docs should assume API v2-only maintenance path.
