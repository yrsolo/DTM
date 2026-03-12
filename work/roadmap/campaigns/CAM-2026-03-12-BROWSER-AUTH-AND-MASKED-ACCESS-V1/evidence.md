# Evidence - CAM-2026-03-12-BROWSER-AUTH-AND-MASKED-ACCESS-V1

## Trust gate
- source: external auth handoff, owner-provided reference bundle, verified route/config code
- last_verified_at: 2026-03-12
- verified_by: Codex
- evidence:
  - `agent/intructions/DTM-test/BACKEND_AUTH_HANDOFF.md`
  - `agent/intructions/DTM-test/work/roadmap/MASTER_EXECUTION_BRIEF_2026-03-12.md`
  - active ingress route docs/code
- trust_level: medium
- notes:
  - handoff file exists and can be used as external browser-facing contract source
  - concrete implementation assumptions still need verification against active backend route handling

## Verified baseline findings
- external handoff defines canonical namespaces `/ops/api/*`, `/test/ops/api/*`, `/ops/auth/*`, `/test/ops/auth/*`
- shared infra route `/grafana/*` is aligned with current unified gateway
- architecture direction requires one canonical payload path with masking as post-build transform

## 2026-03-12 implementation evidence
- chosen trusted-ingress rule:
  - internal service-secret header `X-DTM-Proxy-Secret`
  - bootstrap/env secret `BROWSER_AUTH_PROXY_SECRET`
  - untrusted direct calls downgrade to masked payload instead of `403`
- code pointers:
  - `src/entrypoints/http/access_context.py` validates proxy secret and resolves `AccessContext`
  - `src/entrypoints/http/frontend_v2_handler.py` builds one canonical payload path, appends `meta.access`, and applies masking only as post-build transform
  - `src/services/access/masking.py` performs deterministic masking of sensitive display fields and emits `dtm.api.masking_ms`
  - `src/app/bootstrap.py` loads `BROWSER_AUTH_PROXY_SECRET` only in bootstrap/deps
  - `config/runtime.yaml` declares `auth_trusted_secret_header`, `auth_trusted_fallback`, and `auth_mask_dictionary_version`
- local verification:
  - `python -m unittest tests.api.test_frontend_api_routing`
  - `python -m unittest tests.api.test_frontend_api_v2_payload tests.snapshot_engine.test_query_engine`
- tests now cover:
  - accepted trusted-ingress full path
  - forced masked fallback for untrusted direct/browser-supplied headers
  - deterministic masked output stability
  - masked/full payload shape parity
  - masking timing hook emission

## Remaining verification
- live contour verification still needs deploy to `test`
- full trusted-ingress live verification remains dependent on test contour secret provisioning and proxy wiring

## Required evidence during execution
- code pointers for route namespace and trusted ingress handling
- code pointers for trusted-ingress validation rule
- tests for accepted trusted ingress path
- tests for direct/untrusted fallback behavior
- full vs masked shape parity tests
- deterministic masking stability tests
- before/after response timings including masking stage

## Risks
- over-masking can break useful UI
- under-masking can leak business context
- naive deep traversal can make masked mode too slow
