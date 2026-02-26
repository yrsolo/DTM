# ADR Index

## Шаблон ADR
- `id`: ADR-00X
- `title`
- `status`: proposed | accepted | deprecated
- `context`
- `decision`
- `consequences`
- `date`

## ADR-001
- title: Архитектура `Clean + Hexagonal`
- status: proposed
- context: текущий код сильно связан с внешними API и плохо тестируется.
- decision: разделить систему на `domain/application/ports/adapters/interfaces`.
- consequences: выше стартовые затраты, но ниже стоимость изменений и проще миграция UI.
- date: 2026-02-26

## ADR-002
- title: Разделение источника и приемника таблиц
- status: proposed
- context: нужен безопасный dev/test режим без риска записи в боевую таблицу.
- decision: ввести `SOURCE_SHEET_NAME` и `TARGET_SHEET_NAME`.
- consequences: чуть сложнее конфиг, но безопасная отладка и сравнение результатов.
- date: 2026-02-26

## ADR-003
- title: Канонические модели данных + strict validation
- status: proposed
- context: разношерстные данные из Sheets приводят к нестабильности пайплайна.
- decision: все входы приводить к типизированным моделям (`TaskRecord`, `PersonRecord` и т.д.).
- consequences: раннее выявление проблем данных, меньше runtime-ошибок.
- date: 2026-02-26

## ADR-004
- title: Fallback-режим рассылки без LLM
- status: proposed
- context: OpenAI может быть недоступен, но рассылка должна продолжать работать.
- decision: отправлять deterministic черновик при ошибке LLM.
- consequences: менее "живой" текст, но стабильная доставка напоминаний.
- date: 2026-02-26

## ADR-005
- title: Стратегия хранения: этапно Google Sheets -> PostgreSQL
- status: proposed
- context: нужно сохранить текущий процесс и подготовить масштабируемую основу.
- decision: сначала канонический слой + read-model, затем перенос source of truth в PostgreSQL.
- consequences: временно гибридная схема, но контролируемый переход без big-bang.
- date: 2026-02-26
