# Browser Auth Operations

## Что здесь важно

Browser auth в DTM состоит из трёх частей:

1. browser/UI;
2. внешний auth contour;
3. backend-функция из этого репозитория.

Этот репозиторий не владеет auth/session endpoints, но владеет backend side of the contract и operator verification.

## Runtime split

- `/ops/auth/*` и `/test/ops/auth/*` — внешний auth contour
- `/ops/api/*` и `/test/ops/api/*` — backend этого репозитория
- `/ops/auth/attachments/*` и `/test/ops/auth/attachments/*` — специальная browser-safe attachment facade

## Что проверять оператору

- `BROWSER_AUTH_PROXY_SECRET` проброшен в backend из Lockbox
- внешний auth contour использует тот же секрет
- trusted secret header совпадает с конфигом backend
- trusted browser route даёт full access только для approved user
- direct backend route деградирует в masked mode

## Где смотреть детали

- [../reference/browser-auth.md](../reference/browser-auth.md)
- [../reference/configuration.md](../reference/configuration.md)
- [runbook.md](runbook.md)
