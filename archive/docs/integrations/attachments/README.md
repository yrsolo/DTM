# Attachments

Эта папка описывает attachment flow DTM: backend-owned lifecycle, browser/frontend contract, product scenario и operator diagnostics.

## Start here

- [backend-flow.md](backend-flow.md)
- [frontend-handoff.md](frontend-handoff.md)
- [frontend-card-publication.md](frontend-card-publication.md)

## Deep dives

- [../browser-auth/contract.md](../browser-auth/contract.md)
- [../../operations/runbook.md](../../operations/runbook.md)

## When to use this folder

Используй этот раздел, когда нужно:
- реализовать attachment UI;
- отладить attachment contour;
- проверить текущий контракт между frontend, auth и backend;
- понять продуктовый смысл потока от upload до появления attachment в карточке.

Reading split:
- `frontend-handoff.md` описывает текущий frontend/backend contract и операционные шаги интеграции.
- `frontend-card-publication.md` описывает продуктовый сценарий и архитектурный ownership потока от mutation до cached card delivery.
