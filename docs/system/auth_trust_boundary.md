# Auth Trust Boundary

## Purpose

This document defines how backend code may trust browser-facing auth headers for the current auth wave.

## Rule

Backend must not trust `x-dtm-*` headers unless the request is confirmed to have arrived through a trusted ingress chain.

Trusted ingress may be established only by an explicit validated rule chosen during the auth campaign, such as:
- internal-only gateway or network boundary
- internal service-secret header unavailable to browser
- proxy-to-backend signing or equivalent trusted hop mechanism
- deployment topology with no direct public access to the browser-facing handler

## Untrusted direct calls

If trusted ingress is not confirmed, backend behavior must be explicitly chosen and implemented:
- force masked mode, or
- return `403`

This choice must not be left implicit.

## Required implementation behavior

- `x-dtm-*` headers are ignored unless trusted ingress validation passes
- trusted ingress validation happens before full-access authorization decisions
- tests must cover both:
  - accepted trusted-ingress path
  - rejected or downgraded direct/untrusted path

## Related docs

- `docs/system/browser_auth_contract.md`
- `docs/system/architecture_values.md`
