# Browser Auth Runbook (Current)

## Purpose

This runbook explains how browser auth works operationally in the current DTM contour:
- which routes belong to browser auth and browser data access,
- what the external auth contour/function is responsible for,
- how backend trust is established,
- how `BROWSER_AUTH_PROXY_SECRET` is wired for `test` and `prod`,
- how to verify rollout and diagnose masked/full behavior.

This is the canonical operator-facing runbook for the current auth wave.
Reference handoff remains archive-only input:
- `agent/intructions/DTM-test/BACKEND_AUTH_HANDOFF.md`

## Runtime components

Current browser auth contour has three components:

1. Browser SPA
   - chooses whether request is `full` or `masked`
   - `full` requests include auth cookie/session
   - `masked` requests intentionally omit auth cookie/session

2. External auth contour/function
   - owns `/ops/auth/*` and `/test/ops/auth/*`
   - validates browser session/cookies
   - decides browser-facing access mode
   - forwards trusted headers plus internal proxy secret to backend data routes

3. Backend function in this repo
   - serves browser data routes under `/ops/api/*` and `/test/ops/api/*`
   - trusts `x-dtm-*` headers only after proxy-secret validation
   - returns canonical payload shape
   - downgrades untrusted/direct calls to `masked`

Important:
- auth/session endpoints are not implemented by Python handlers in this repo
- this repo documents and validates the backend side of that contract
- `/info` remains backend-owned and reuses the existing browser-safe attachment facade under `/ops/auth/attachments/*`

## Public routes and callbacks

### Prod
- auth/session namespace: `/ops/auth/*`
- browser data namespace: `/ops/api/*`
- OAuth callback: `https://dtm.solofarm.ru/ops/auth/callback`

### Test
- auth/session namespace: `/test/ops/auth/*`
- browser data namespace: `/test/ops/api/*`
- OAuth callback: `https://dtm.solofarm.ru/test/ops/auth/callback`

### Reserved backend-owned service routes
- `/ops/api/*`
- `/ops/admin/*`
- `/ops/telegram*`
- `/test/ops/api/*`
- `/test/ops/admin/*`
- `/test/ops/telegram*`

### Browser-safe attachment facade used by `/info` harness
- `/ops/auth/attachments/*`
- `/test/ops/auth/attachments/*`

These are special-case attachment routes, not a generic BFF namespace. `/info` uses them for the reserved operator attachment probe.

### Shared infra route
- `/grafana/*`

## Trusted ingress contract

Backend trusted-ingress validation is implemented in:
- `src/entrypoints/http/access_context.py`

Current contract:
- trusted secret header name: `X-DTM-Proxy-Secret`
- trusted secret source in backend runtime: `BROWSER_AUTH_PROXY_SECRET`
- trusted access headers:
  - `x-dtm-access-mode`
  - `x-dtm-authenticated`
  - `x-dtm-contour`
  - `x-dtm-user-id`
  - `x-dtm-user-role`
  - `x-dtm-user-status`

Backend behavior:
- if proxy secret is valid and contour matches, backend may trust `x-dtm-*`
- if proxy secret is absent/invalid, backend ignores browser-supplied `x-dtm-*`
- current fallback is `masked`, not `403`

Full access requires all of:
- trusted ingress
- `x-dtm-authenticated: 1`
- `x-dtm-access-mode: full`
- `x-dtm-user-status: approved`

Masked access applies when:
- request is intentionally masked, or
- request is unauthenticated, or
- trusted ingress validation fails, or
- contour/header state is inconsistent

## Secret wiring

### Backend function
Backend secret bootstrap is code-backed:
- `src/app/bootstrap.py` reads `BROWSER_AUTH_PROXY_SECRET` from env
- `config/runtime.yaml` defines:
  - `runtime.api.auth_trusted_secret_header`
  - `runtime.api.auth_trusted_fallback`
  - `runtime.api.auth_mask_dictionary_version`

Current deploy workflows map the secret from Lockbox into backend env:
- test deploy: `.github/workflows/deploy_yc_function_main.yml`
- prod deploy: `.github/workflows/release_yc_function_prod.yml`

Current mapping form:
- `BROWSER_AUTH_PROXY_SECRET=${LOCKBOX_ID}/latest/BROWSER_AUTH_PROXY_SECRET`

### External auth contour
The external auth contour must use the same Lockbox secret value when forwarding `X-DTM-Proxy-Secret`.

This repo does not own that contour's code, so operator verification is required after rollout:
- confirm the auth contour is wired to the Lockbox key `BROWSER_AUTH_PROXY_SECRET`
- confirm forwarded header name is `X-DTM-Proxy-Secret`
- confirm the literal header value matches backend runtime env one-to-one

## Deploy and rollout procedure

### Test
1. Ensure backend `test` deploy uses the current Lockbox mapping for `BROWSER_AUTH_PROXY_SECRET`.
2. Ensure auth contour `test` runtime also reads the same Lockbox key.
3. Deploy `test`.
4. Open `/test/ops/info`.
5. Use API Request Builder in two modes:
   - `browser proxy (/bff/api)` or current browser-facing auth/proxy route if present in contour
   - `direct backend (/api)`
6. For `full (with cookie)` on trusted browser path, verify:
   - `meta.access.mode = full`
   - `trustedIngress = true`
   - `authenticated = true`
   - `userStatus = approved`
7. For direct backend `/api` call, verify:
   - `meta.access.mode = masked`
   - `trustedIngress = false`
   - `fallbackReason = untrusted_ingress`

### Prod
1. Confirm prod workflow still maps `BROWSER_AUTH_PROXY_SECRET` from Lockbox.
2. Confirm auth contour/proxy uses the same Lockbox key in prod.
3. Deploy prod.
4. Verify browser auth callback path:
   - `https://dtm.solofarm.ru/ops/auth/callback`
5. Repeat the same full-vs-direct verification using prod routes.

## Quick diagnosis guide

If browser route still returns masked payload:

1. Check `meta.access` in response.
2. If `trustedIngress=false` and `fallbackReason=untrusted_ingress`:
   - backend did not accept the proxy-secret chain
   - inspect auth contour header forwarding and backend env secret
3. If `trustedIngress=true` but `authenticated=false`:
   - trusted route is intact
   - browser session/cookie did not resolve to authenticated user
4. If `trustedIngress=true`, `authenticated=true`, `mode=full`, but payload still looks masked:
   - investigate backend masking branch after access resolution

## `/info` attachment harness support

Backend `/info` detail payload now includes `attachmentsHarness` metadata for a reserved probe task.

Operator/browser flow:
1. Open `/ops/info` or `/test/ops/info`
2. Use `Attachment Harness` section
3. Browser calls auth-facade routes under `/ops/auth/attachments/*` or `/test/ops/auth/attachments/*`
4. Auth contour forwards only those special routes to backend-owned attachment endpoints with trusted secret and trusted `x-dtm-*`
5. Browser uploads binary directly to returned Object Storage `uploadUrl`

Required auth-contour behavior:
- preserve JSON request/response bodies for:
  - `request-upload`
  - `finalize`
  - `delete`
  - `job status`
- preserve redirect behavior for:
  - `view`
  - `download`
- do not proxy binary upload to Object Storage

Probe-task policy:
- reserved task id comes from backend runtime config and is shown in `/info`
- task must exist in source data with service status `test`
- attachment readiness is checked in backend-owned `/info` detail payload via `attachmentsHarness.probeAttachments`

## Related docs

- `docs/system/browser_auth_contract.md`
- `docs/system/auth_trust_boundary.md`
- `docs/system/config.md`
- `docs/system/architecture.md`
- `docs/system/entrypoints_index_main.md`
