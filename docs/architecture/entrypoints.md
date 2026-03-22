# Entry Points

## Принцип

Entry points в DTM должны быть тонкими.

Они могут:
- принять вход;
- собрать request/runtime context;
- вызвать module API или runtime shell;
- превратить результат в HTTP response или execution result.

Они не должны:
- хранить доменные правила;
- выбирать ownership за модули;
- тянуть тяжёлые adapters напрямую;
- собирать большой orchestration flow у себя.

## Текущие виды входа

- `root` — основной HTTP вход функции
- `http` — browser/admin/runtime handlers
- `runtime` — explicit runtime execution
- `triggers` — scheduled/event-based start
- queue/worker execution shells — command-backed execution

## Практическая проверка

Если сценарий нельзя объяснить через
`entrypoint -> platform/runtime shell -> owning module`,
значит архитектура начала терять форму.
