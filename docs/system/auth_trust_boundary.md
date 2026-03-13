# Auth Trust Boundary

## Purpose

This document defines how backend code may trust browser-facing auth headers for the current auth wave.

## Rule

Backend must not trust `x-dtm-*` headers unless the request is confirmed to have arrived through a trusted ingress chain.

Chosen rule for the current implementation:
- trusted ingress is established by an internal service-secret header unavailable to browser clients
- configured header name: `X-DTM-Proxy-Secret`
- secret value is supplied through bootstrap/env only: `BROWSER_AUTH_PROXY_SECRET`
- backend trusts `x-dtm-*` access headers only after this secret passes validation

## Untrusted direct calls

If trusted ingress is not confirmed, backend behavior must be explicitly chosen and implemented:
- force masked mode

Current repo implementation does not return `403` for direct browser calls. It downgrades them to masked payloads so the canonical frontend contract remains available without trusting browser-supplied auth headers.

This choice must not be left implicit.

## Required implementation behavior

- `x-dtm-*` headers are ignored unless trusted ingress validation passes
- trusted ingress validation happens before full-access authorization decisions
- trusted full mode additionally requires:
  - `x-dtm-authenticated: 1`
  - `x-dtm-access-mode: full`
  - `x-dtm-user-status: approved`
- tests must cover both:
  - accepted trusted-ingress path
  - rejected or downgraded direct/untrusted path

## Related docs

- `docs/system/browser_auth_contract.md`
- `docs/system/architecture_values.md`
