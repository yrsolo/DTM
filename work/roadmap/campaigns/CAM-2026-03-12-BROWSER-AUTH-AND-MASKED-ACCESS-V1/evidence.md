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
