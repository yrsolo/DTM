# Архитектура

Здесь собраны материалы о том, как устроен текущий DTM runtime: основной контур, snapshot engine, границы системы и будущие skeleton-документы.

## Start here

- [runtime/README.md](runtime/README.md) — текущий production-like runtime
- [snapshot-engine/README.md](snapshot-engine/README.md) — read-side и snapshot model
- [future/README.md](future/README.md) — принятые skeleton-документы на будущие перестройки

## Deep dives

- [runtime/architecture.md](runtime/architecture.md)
- [runtime/dataflow.md](runtime/dataflow.md)
- [snapshot-engine/architecture.md](snapshot-engine/architecture.md)

## When to use this folder

Используй этот раздел, когда нужно:

- понять текущий runtime contour
- разобраться, где проходит граница между read path, async jobs и HTTP boundary
- быстро найти системный deep dive по нужному subsystem
