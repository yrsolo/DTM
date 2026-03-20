# Обзор DTM

DTM — это внутренняя операционная система для команд, которые ведут задачи и людей вокруг Google Sheets, но хотят:

- стабильные browser-safe чтения;
- предсказуемую асинхронную обработку тяжёлых действий;
- единый диагностический контур;
- понятные контракты между backend, frontend и auth.

На практике DTM:

- собирает данные из Sheets;
- строит подготовленные snapshot-артефакты в Object Storage;
- отдаёт браузеру уже подготовленную картину;
- выносит тяжёлые и мутирующие действия в очередь и worker jobs.

Это позволяет держать чтение быстрым и безопасным, а сложные действия вроде attachment finalize, render и reminder — прозрачными и наблюдаемыми.

Attachment flow — хороший пример базового продуктового паттерна DTM:
- тяжёлая mutation идёт async;
- оператор ждёт не просто upload acceptance, а publication/readiness;
- браузер потом читает уже подготовленный cached или snapshot-backed payload вместо тяжёлой сборки карточки на каждый запрос.

## Куда идти дальше

- [capabilities.md](capabilities.md)
- [../architecture/runtime/architecture.md](../architecture/runtime/architecture.md)
- [../operations/runbook.md](../operations/runbook.md)
