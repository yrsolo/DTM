# Архитектура

Здесь собраны материалы о том, как устроен текущий DTM runtime, и нормативные документы для modular-monolith refactor wave.

## Start here

- [runtime/modular-monolith-v2.md](runtime/modular-monolith-v2.md) — normative master text для будущих refactor campaigns
- [runtime/README.md](runtime/README.md) — текущий production-like runtime
- [snapshot-engine/README.md](snapshot-engine/README.md) — read-side и snapshot model
- [future/README.md](future/README.md) — принятые skeleton-документы на будущие перестройки

## Deep dives

- [runtime/architecture.md](runtime/architecture.md)
- [runtime/dataflow.md](runtime/dataflow.md)
- [runtime/context-ownership-map.md](runtime/context-ownership-map.md)
- [snapshot-engine/architecture.md](snapshot-engine/architecture.md)

## When to use this folder

Используй этот раздел, когда нужно:

- понять текущий runtime contour
- понять целевой modular-monolith contract для новых кампаний
- разобраться, где проходит граница между read path, async jobs и HTTP boundary
- быстро найти системный deep dive по нужному subsystem
