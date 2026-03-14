# Browser Auth Contract (Current)

## Purpose

This document records the current backend-facing browser auth contract for the 2026-03-12 execution wave.

Canonical operator runbook:
- `docs/system/browser_auth_runbook.md`

Reference-only handoff remains:
- `agent/intructions/DTM-test/BACKEND_AUTH_HANDOFF.md`

## Route namespace

Prod:
- browser data path: `/ops/api/v2/frontend`
- auth/session path: `/ops/auth/*`
- callback path: `/ops/auth/callback`

Test:
- browser data path: `/test/ops/api/v2/frontend`
- auth/session path: `/test/ops/auth/*`
- callback path: `/test/ops/auth/callback`

Shared infra path:
- `/grafana/*`

Current ownership split:
- external auth contour/function owns `/ops/auth/*` and `/test/ops/auth/*`
- backend function in this repo owns `/ops/api/*` and `/test/ops/api/*`

## Trust boundary

Browser traffic must be interpreted through trusted proxy/gateway chain only.

Chosen trusted-ingress mechanism for the current wave:
- auth proxy must send an internal service-secret header
- backend validates that header before trusting any `x-dtm-*` access headers
- browser requests without that secret are treated as untrusted direct calls

Configured backend secret source:
- env key: `BROWSER_AUTH_PROXY_SECRET`
- configured trusted header name: `X-DTM-Proxy-Secret`

Trusted proxy headers:
- `x-dtm-access-mode: full | masked`
- `x-dtm-authenticated: 1 | 0`
- `x-dtm-contour: test | prod`
- `x-dtm-user-id`
- `x-dtm-user-role`
- `x-dtm-user-status`

Browser-supplied `x-dtm-*` headers must not be trusted outside trusted ingress.

## Backend behavior

Required access model:
- build one canonical frontend payload shape
- apply access policy at the boundary
- apply masking as post-build transform when required

Full access:
- authenticated request
- trusted access mode is `full`
- approved user policy may return unmasked payload

Masked access:
- unauthenticated request, or
- trusted access mode is `masked`
- trusted ingress validation fails and backend downgrades to masked fallback
- payload shape stays the same, but sensitive display fields are deterministically rewritten

## Masking rules

Preserve as-is where possible:
- ids
- dates
- statuses
- milestone sequence
- counters and meta structure

Mask sensitive business display fields:
- task title
- brand
- customer
- show/group names
- person/designer names
- free-text notes/comments/history-like text

## Implementation direction

Preferred backend pipeline:
- HTTP -> AccessContext -> canonical payload build -> optional MaskingTransformer -> response

Current repo implementation:
- trusted ingress is resolved in `src/entrypoints/http/access_context.py`
- masking transform lives in `src/services/access/masking.py`
- frontend handler keeps one canonical payload build path in `src/entrypoints/http/frontend_v2_handler.py`
- secret bootstrap lives in `src/app/bootstrap.py`

Current deploy wiring:
- `.github/workflows/deploy_yc_function_main.yml` maps `BROWSER_AUTH_PROXY_SECRET` from Lockbox for `test`
- `.github/workflows/release_yc_function_prod.yml` maps `BROWSER_AUTH_PROXY_SECRET` from Lockbox for `prod`

Forbidden direction:
- separate masked query engine
- access checks scattered deep inside query logic
- random or non-deterministic masking

## Related docs

- `docs/system/browser_auth_runbook.md`
- `docs/system/auth_trust_boundary.md`
- `docs/system/config.md`
