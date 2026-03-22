# DTM

DTM — внутренняя операционная система для команд, которые ведут задачи, сроки, людей и вложения вокруг Google Sheets, но хотят читать данные быстро, мутировать их безопасно и сопровождать всё это без ручной магии.

Проще говоря, репозиторий решает три задачи:
- собирает и нормализует данные из рабочих таблиц;
- строит стабильный read-model для браузера и операторских сценариев;
- выносит тяжёлые и рискованные действия в явные асинхронные команды.

## Что здесь важно

- Браузер читает уже подготовленный payload, а не собирает карточки на лету.
- Refresh, reminders, rendering и attachment-mutations идут через очередь и worker.
- `/info` служит операторской точкой входа для диагностики и live-smoke.
- Вложения считаются опубликованными только когда они появились в основном browser read-model.

## Для кого проект

- для design operations и production-команд;
- для инженеров, которые поддерживают внутренний planning/runtime contour;
- для операторов, которым нужны понятные runbook'и и диагностические инструменты.

## Технологии

`python` `yandex-cloud` `yandex-message-queue` `object-storage` `google-sheets` `telegram` `grafana`

## Куда читать дальше

- [Карта документации](docs/README.md)
- [Короткий обзор продукта](docs/product/overview.md)
- [Текущая архитектура](docs/architecture/README.md)
- [Модули и зоны ответственности](docs/modules/README.md)
- [Эксплуатация и runbook](docs/operations/README.md)
- [Конфиг и контракты](docs/reference/README.md)
- [Текущее выполнение и tracking](work/README.md)

## Быстрый путь по репозиторию

1. [docs/product/overview.md](docs/product/overview.md)
2. [docs/architecture/overview.md](docs/architecture/overview.md)
3. [docs/modules/access_api.md](docs/modules/access_api.md)
4. [docs/modules/attachments.md](docs/modules/attachments.md)
5. [index.py](index.py)

## Принципы репозитория

DTM сознательно предпочитает:
- стабильные read-paths вместо тяжёлых live-сборок;
- явные async-команды вместо скрытых side effects;
- небольшие понятные контракты вместо универсальных фасадов;
- операционную прозрачность вместо clever-решений.

История миграций, старые аудиты и superseded документы лежат в [archive/docs/README.md](archive/docs/README.md) и [archive/work/README.md](archive/work/README.md).
