# Настройка очереди

## Очереди по контурам

### Test

- `dtm-test-commands`
- `dtm-test-commands-dlq`

### Prod

- `dtm-prod-commands`
- `dtm-prod-commands-dlq`

## Зачем нужна DLQ

Основная очередь обрабатывает команды.  
DLQ хранит проблемные сообщения, которые исчерпали retry-политику на уровне очереди.

## Рекомендуемые параметры

- тип очереди: `Standard`
- `visibility timeout`: `60-180s`
- `max receive count`: `5-10`
- dead-letter queue: отдельная DLQ того же контура

## Текущая topology

DTM сейчас не использует отдельную worker function.

В каждом контуре один и тот же Cloud Function object принимает:
- HTTP gateway events;
- Message Queue trigger events.

Именно это и считается канонической текущей topology.

## Практические замечания

- для каждой основной очереди должен быть свой trigger;
- очередь и trigger должны жить в той же cloud/folder схеме, что ожидает deploy;
- поведение очереди должно совпадать с [queue-retry-policy.md](queue-retry-policy.md).
