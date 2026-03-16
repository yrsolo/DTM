# Browser Auth Contract (Current)

## Purpose

This document records the current backend-facing browser auth contract for the 2026-03-12 execution wave.

Canonical operator runbook:
- `docs/integrations/browser-auth/runbook.md`

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

Attachment harness uses the existing browser-safe attachment auth facade:
- `/ops/auth/attachments/*`
- `/test/ops/auth/attachments/*`
- these routes are not a generic BFF/proxy namespace
- `/info` relies on this existing attachment facade for reserved probe-task operations

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

- `docs/integrations/browser-auth/runbook.md`
- `docs/integrations/browser-auth/trust-boundary.md`
- `docs/reference/configuration.md`

## Attachment harness facade contract

The external auth contour already exposes browser-safe attachment facade routes that `/info` may reuse for operator diagnostics.

Expected browser-facing routes:
- `POST /ops/auth/attachments/request-upload`
- `POST /test/ops/auth/attachments/request-upload`
- `POST /ops/auth/attachments/finalize`
- `POST /test/ops/auth/attachments/finalize`
- `POST /ops/auth/attachments/delete`
- `POST /test/ops/auth/attachments/delete`
- `GET /ops/auth/attachments/jobs/{job_id}`
- `GET /test/ops/auth/attachments/jobs/{job_id}`
- `GET /ops/auth/attachments/{attachment_id}/view`
- `GET /test/ops/auth/attachments/{attachment_id}/view`
- `GET /ops/auth/attachments/{attachment_id}/download`
- `GET /test/ops/auth/attachments/{attachment_id}/download`

Facade behavior:
- validate browser session/cookie using the existing auth contour
- inject `X-DTM-Proxy-Secret`
- inject trusted `x-dtm-*` headers
- preserve method, query, JSON body, response status, response body, and redirect semantics
- forward only to matching backend-owned routes needed by the attachment harness

Backend route mapping:
- `request-upload` -> `/ops/admin/task-attachments/request-upload`
- `finalize` -> `/ops/admin/task-attachments/finalize`
- `delete` -> `/ops/admin/task-attachments/delete`
- `jobs/{job_id}` -> `/ops/admin/jobs/{job_id}`
- `view` -> `/ops/api/task-attachments/{attachment_id}/view`
- `download` -> `/ops/api/task-attachments/{attachment_id}/download`

Deliberate non-goal:
- direct Object Storage binary upload is not proxied through `/ops/auth/*`
- returned presigned `uploadUrl` is used directly by browser

## Secret-only internal people route

Contract:
- prod path: `/ops/api/v2/people`
- test path: `/test/ops/api/v2/people`
- requires valid `X-DTM-Proxy-Secret`
- does not use `x-dtm-*` browser auth headers
- returns `403` on missing/invalid secret
- returns the full normalized people registry snapshot for internal auth-support consumers
- people registry distinguishes:
  - `contactEmail` for ordinary human contact
  - `yandexEmail` for Yandex-account resolution
- API response returns the stable canonical fields only; raw mapped row attributes stay internal to the snapshot storage contract
