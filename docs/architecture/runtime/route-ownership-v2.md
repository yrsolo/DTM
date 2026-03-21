# Route Ownership V2

This document defines target ownership for active HTTP and trigger-facing routes/surfaces in the current runtime contour.

Governing source:
- [../module-first-recovery/README.md](../module-first-recovery/README.md)

## Route ownership

| Route / surface | Transport | Owner | Semantics |
|---|---|---|---|
| healthcheck | cloud event / HTTP-like | `platform.runtime` | sync |
| Telegram webhook path | HTTP | `telegram_interaction` | sync intake, async command enqueue |
| frontend/public API paths | HTTP | `access_api` | sync read |
| attachment admin request-upload/finalize/delete paths | HTTP | `attachments` | sync intake, async mutation enqueue where needed |
| attachment read/view/download paths | HTTP | `attachments` | sync read/access resolution |
| `/info` and runtime diagnostics | HTTP | `platform.runtime` | sync diagnostics |
| job status routes | HTTP | `platform.runtime` | sync status read |
| timer trigger surface | scheduled trigger | `platform.runtime` orchestration | accepted/async |
| morning trigger surface | scheduled trigger | `platform.runtime` orchestration | accepted/async |

## Rules

- route ownership is context-first, not folder-first
- entrypoint and platform may host shells, but business ownership belongs to the context listed here
- admin/runtime diagnostics remain platform-owned until a separate explicit context is intentionally introduced
