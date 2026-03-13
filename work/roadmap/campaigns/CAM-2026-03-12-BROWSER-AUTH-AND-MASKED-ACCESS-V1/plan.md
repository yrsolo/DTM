# CAM-2026-03-12-BROWSER-AUTH-AND-MASKED-ACCESS-V1

## Goal

Add browser-facing auth integration and masked/full access without duplicating canonical read-side business logic.

## Dependencies

- Stage 1 runtime/bootstrap facts must be stable
- Stage 2 read/perf facts must exist
- external handoff source: `agent/intructions/DTM-test/BACKEND_AUTH_HANDOFF.md`

## Scope

In scope:
- trusted access boundary for `/ops/*` and `/test/ops/*`
- `AccessContext` and trusted header resolution
- one canonical payload build path with optional masking transform
- deterministic masking dictionaries and mapping
- explicit trusted ingress validation and documented fallback for untrusted direct calls

Out of scope:
- separate masked query engine
- browser-trusted auth headers outside trusted ingress

## Concrete tasks

1. Verify route namespace and trusted ingress assumptions.
2. Introduce access context boundary and resolver.
3. Keep one canonical payload build path for full and masked modes.
4. Add deterministic masking transform with shape-preserving behavior.
5. Add tests for full vs masked shape parity, deterministic mapping, and trusted-header behavior.
6. Decide and document how backend recognizes trusted proxy chain vs direct/untrusted call.
7. Choose and implement fallback for untrusted ingress:
   - force masked mode, or
   - return `403`
8. Add canonical trust-boundary doc in main docs: `docs/system/auth_trust_boundary.md`

## Trusted ingress requirement

`x-dtm-*` headers are trusted only under an explicit validated ingress rule.

Allowed trust mechanisms to evaluate:
- internal-only gateway or network boundary
- internal service-secret header unavailable to browser
- proxy-to-backend signing or equivalent trusted hop mechanism
- deployment topology with no direct public access to browser-facing handler

## Acceptance criteria

- masked and full share one payload contract
- sensitive fields are deterministically masked
- trusted proxy headers drive access mode only under explicit validated ingress rule
- untrusted direct-call behavior is specified, implemented, and tested
- `docs/system/auth_trust_boundary.md` exists and documents the chosen trust rule
- masked path has explicit timing hooks and does not fork domain logic
