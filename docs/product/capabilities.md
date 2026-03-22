# Возможности DTM

Ключевые пользовательские и операторские возможности текущего DTM:

- чтение подготовленного task payload для browser/UI;
- people snapshot и служебные people reads;
- async refresh и queue-backed command execution;
- render-потоки для Sheets-представлений;
- reminders и Telegram-related runtime;
- attachment lifecycle:
  - request-upload
  - direct upload to storage
  - finalize
  - async attach/delete jobs
  - view/download/delete
- `/info` как операторская точка диагностики и live smoke;
- observability через status records, metrics, Grafana и DataLens.

## Куда идти дальше

- [../modules/attachments.md](../modules/attachments.md)
- [../reference/browser-auth.md](../reference/browser-auth.md)
- [../operations/observability/README.md](../operations/observability/README.md)
