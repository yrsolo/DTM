# Browser Auth Contract (Current)

## Purpose

This document records the current backend-facing browser auth contract for the 2026-03-12 execution wave.

This is the main repo summary of the contract. The owner-provided handoff remains:
- `agent/intructions/DTM-test/BACKEND_AUTH_HANDOFF.md`

## Route namespace

Prod:
- browser data path: `/ops/api/v2/frontend`
- auth/session path: `/ops/auth/*`

Test:
- browser data path: `/test/ops/api/v2/frontend`
- auth/session path: `/test/ops/auth/*`

Shared infra path:
- `/grafana/*`

## Trust boundary

Browser traffic must be interpreted through trusted proxy/gateway chain only.

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

Forbidden direction:
- separate masked query engine
- access checks scattered deep inside query logic
- random or non-deterministic masking
