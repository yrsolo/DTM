# priorities_pipeline.md — Приоритеты кампаний “выпрямления” пайплайна

## Priority 0 — Прямой путь данных (убрать блуждание)
1) **CAM-PIPELINE-STRAIGHTEN-V1**
- даёт один gate и один sync
- делает preflight реально дешёвым
- резко упрощает reasoning и снижает лишние fetch

## Priority 1 — Убрать hybrid legacy/modern смешение
2) **CAM-ENTRYPOINT-DEHYBRID-V1**
- убирает круги index↔main
- устраняет смешение core legacy в entrypoints
- делает “источник истины” очевидным

## Priority 2 — Убрать гиперфункции и стабилизировать границы
3) **CAM-ENTRYPOINT-HYGIENE-V1**
- делает код читабельным и предотвращает повторное зарастание if-ами/аргументами
- желательно делать после того, как пайплайн выпрямлен и hybrid снят

## Notes
- Если CAM-CONFIG-REFORM-V0 ещё не завершена полностью (ENV→YAML), то сначала закончить её, но по твоему скрину она отмечена done.
- Дедуп legacy можно делать “вставками” в рамках STRAIGHTEN/DEHYBRID, но без расползания в большой CAM-DEDUP, чтобы не потерять фокус.
