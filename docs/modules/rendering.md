# `rendering`

## Роль

`rendering` владеет sheet rendering use-cases:
- timeline rendering;
- designers rendering;
- representation/writeback для целевых таблиц.

## Главные входы

- queue-backed rendering commands;
- application-owned execution API для render jobs;
- queue handlers, собранные через module-owned surface, а не через public job catalog.

## Что модуль не должен делать

- владеть ingestion или snapshot assembly;
- импортировать snapshot internals напрямую;
- прятать business rules в trigger/runtime shell.

## Finish line

Rendering finish line — целевая таблица обновлена через канонический rendering flow, а не через ad-hoc запись из runtime-кода.
