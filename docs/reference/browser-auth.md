# Browser Auth Reference

## Purpose

Этот документ фиксирует текущий backend-facing browser auth contract.

## Route namespace

Prod:
- browser data path: `/ops/api/v2/frontend`
- auth/session path: `/ops/auth/*`
- callback path: `/ops/auth/callback`

Test:
- browser data path: `/test/ops/api/v2/frontend`
- auth/session path: `/test/ops/auth/*`
- callback path: `/test/ops/auth/callback`

Attachment facade:
- `/ops/auth/attachments/*`
- `/test/ops/auth/attachments/*`

## Trusted ingress

Backend доверяет `x-dtm-*` только после валидации trusted ingress.

Текущий механизм:
- trusted secret header: `X-DTM-Proxy-Secret`
- backend secret source: `BROWSER_AUTH_PROXY_SECRET`
- trusted access headers:
  - `x-dtm-access-mode`
  - `x-dtm-authenticated`
  - `x-dtm-contour`
  - `x-dtm-user-id`
  - `x-dtm-user-role`
  - `x-dtm-user-status`

Если trusted ingress не подтверждён, backend деградирует в masked mode.

## Access policy

Full access требует:
- trusted ingress;
- `x-dtm-authenticated: 1`;
- `x-dtm-access-mode: full`;
- `x-dtm-user-status: approved`.

Masked access применяется, если:
- запрос намеренно masked;
- пользователь не аутентифицирован;
- trusted ingress не подтверждён;
- contour/header state противоречив.

## Related config

- `runtime.api.auth_trusted_secret_header`
- `runtime.api.auth_trusted_fallback`
- `runtime.api.auth_mask_dictionary_version`
- `BROWSER_AUTH_PROXY_SECRET`

## Related docs

- [../operations/browser-auth.md](../operations/browser-auth.md)
- [configuration.md](configuration.md)
