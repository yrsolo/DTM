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

## Live verification (2026-03-12)
- deployed commit to `origin/test`: `96820f3`
- direct browser-like request to `https://dtm.solofarm.ru/test/ops/api/v2/frontend?statuses=work&limit=1` now returns:
  - `meta.access.mode = "masked"`
  - `meta.access.fallbackReason = "untrusted_ingress"`
  - masked task title like `Task-ef2f4915` instead of live business title
- rollout lag on test contour was observable: old unmasked response persisted for several polls, then switched to masked response on attempt 6
- conclusion:
  - live untrusted/direct path downgrade works on test contour
  - canonical payload remains available while browser-supplied `x-dtm-*` headers stay untrusted

## Current blocker
- accepted trusted-ingress full-mode path is implemented and covered by local tests, but not yet live-verified
- remaining blocker is infra-side:
  - test contour secret provisioning for `BROWSER_AUTH_PROXY_SECRET`
  - auth proxy or equivalent trusted hop that injects both proxy secret and `x-dtm-*` headers

## 2026-03-12 deploy wiring fix
- repo verification found that backend runtime already reads `BROWSER_AUTH_PROXY_SECRET` from env in `src/app/bootstrap.py`
- root cause on repo side was deploy wiring drift:
  - `.github/workflows/deploy_yc_function_main.yml` did not map `BROWSER_AUTH_PROXY_SECRET` from Lockbox into backend function env
  - `.github/workflows/release_yc_function_prod.yml` did not map `BROWSER_AUTH_PROXY_SECRET` from Lockbox into backend function env
- fix applied:
  - both workflows now inject `BROWSER_AUTH_PROXY_SECRET=${LOCKBOX_ID}/latest/BROWSER_AUTH_PROXY_SECRET`
  - `agent/prepare_prod_release.py` now treats `BROWSER_AUTH_PROXY_SECRET` as required for release prep
- expected outcome after next test deploy:
  - backend and auth-proxy use the same Lockbox-backed secret source
  - live trusted-ingress requests can be rechecked for `meta.access.mode = full`

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
