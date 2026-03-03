### CAM-ENTRYPOINT-REFORM-V1 — Чистка entrypoints: `index.py` и `main.py`

**Цель**
Сделать `index.py` и `main.py` тонкими и понятными: они должны быть только “точками входа”, а не местом, где живёт бизнес-логика, разбор конфигов, orchestration и ветвления по флагам.

**Проблема сейчас**

* В `index.py` смешаны routing, бизнес-решения, работа с хранилищами, форматирование ответов.
* В `main.py` смешаны bootstrap, sync/build/readmodel, параметры окружения и сложное ветвление, от чего трудно безопасно менять архитектуру.

**Scope**

* Вынести orchestration/use-cases в `src/services/*`.
* Вынести HTTP handlers в `src/entrypoints/http/*`.
* Вынести jobs/cron/timer в `src/entrypoints/jobs/*`.
* Создать единый composition root/bootstrapping: сборка зависимостей и конфигов в одном месте (например `src/app/bootstrap.py`).
* Нормализовать обработку ошибок/логирование в entrypoints.

**Non-goals**

* Не переписывать бизнес-логику алгоритмов.
* Не менять функционал API-контрактов.
* Не делать “идеальный DI-фреймворк” — достаточно простой фабрики зависимостей.

**Deliverables**

* Новый слой `src/entrypoints/` (http + jobs).
* `index.py` превращён в thin router → handlers.
* `main.py` превращён в thin cli/job runner → services.
* Док: короткий `docs/system/entrypoints.md` (что где живёт и как запускается).

**Definition of Done**

* `index.py` читается сверху вниз за 2–3 минуты и не содержит бизнес-ветвлений.
* `main.py` не содержит больших блоков логики: только выбор “какую job запустить” и вызов сервиса.
* Большая часть логики перемещена в тестируемые модули (services).

---