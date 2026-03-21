# CAM-UNIFIED-API-INGRESS-V1 Evidence

- source: `config/runtime.yaml`
  last_verified_at: 2026-03-11
  verified_by: Codex
  evidence: `web.api_domain_test`, `web.api_domain_prod` still pointed to `dtm-api-test.solofarm.ru` and `dtm-api.solofarm.ru`; target canonical test path is `/test`
  trust_level: high
  notes: repo-side generated URLs still assumed separate hosts

- source: `src/entrypoints/http/info_handler.py`
  last_verified_at: 2026-03-11
  verified_by: Codex
  evidence: `/info` built `webhookUrl` from configured API domain, but did not expose UI base path
  trust_level: high
  notes: HTML page itself needed additive base-path awareness

- source: `src/entrypoints/http/templates/info.js`
  last_verified_at: 2026-03-11
  verified_by: Codex
  evidence: fetches and admin actions used absolute-root URLs like `/info`, `/admin/jobs`, `/api/v2/frontend`
  trust_level: high
  notes: this would break from browser-visible `/test/info` and root `/info`

- source: live Yandex API Gateway specs
  last_verified_at: 2026-03-11
  verified_by: Codex
  evidence: test gateway `d5dqk340tjat1ckobhev` and prod gateway `d5d1osrad1qhg1ajbhgo` each route root/proxy to a single function; certificate `fpqsk82473vprlt5fv8p` exists for `dtm.solofarm.ru`
  trust_level: high
  notes: unified path-based gateway can be introduced without deleting old domains

- source: live unified gateway rollout
  last_verified_at: 2026-03-11
  verified_by: Codex
  evidence: unified gateway `d5d84fgjajg4k61vh53h` created on `dtm.solofarm.ru`; direct gateway host returns `200` for `/test/info?format=json`, `/test/api/v2/frontend?limit=1`, `/info?format=json`, and `/api/v2/frontend?limit=1`
  trust_level: high
  notes: routing works before DNS propagation/cache expiry

- source: live canonical host verification after test path rename
  last_verified_at: 2026-03-11
  verified_by: Codex
  evidence: `https://dtm.solofarm.ru/test/ops/info?format=json`, `https://dtm.solofarm.ru/test/ops/api/v2/frontend?limit=1`, `https://dtm.solofarm.ru/ops/info?format=json`, and `https://dtm.solofarm.ru/ops/api/v2/frontend?limit=1` all return `200`
  trust_level: high
  notes: canonical test service ingress is `/test/ops/...`; canonical prod service ingress is `/ops/...`

- source: live canonical frontend/grafana/auth verification after full spec normalization
  last_verified_at: 2026-03-11
  verified_by: Codex
  evidence: `GET https://dtm.solofarm.ru/test` -> `200` with `x-serverless-gateway-path: /test`; `GET https://dtm.solofarm.ru/test/` -> `200` with `x-serverless-gateway-path: /test`; `GET https://dtm.solofarm.ru/grafana/login` -> `200` with `x-serverless-gateway-path: /grafana/{path+}`; `GET https://dtm.solofarm.ru/ops/auth/ping` -> `502` with `x-serverless-gateway-path: /ops/auth/{proxy+}`; `GET https://dtm.solofarm.ru/test/ops/auth/ping` -> `404` with `x-serverless-gateway-path: /test/ops/auth/{proxy+}`
  trust_level: high
  notes: routing is correct for frontend, Grafana, and both auth paths; auth function behavior is separate from gateway normalization

- source: live bucket-backed admin SPA fallback under normalized ingress
  last_verified_at: 2026-03-11
  verified_by: Codex
  evidence: `GET https://dtm.solofarm.ru/admin` -> `200` with `x-serverless-gateway-path: /admin`; `GET https://dtm.solofarm.ru/test/admin` -> `200` with `x-serverless-gateway-path: /test/admin`; both return bucket HTML entrypoint instead of `503`
  trust_level: high
  notes: admin remains frontend-owned and bucket-backed; no separate function route was introduced

- source: Yandex DNS zone `solofarm.ru`
  last_verified_at: 2026-03-11
  verified_by: Codex
  evidence: record `dtm.solofarm.ru.` replaced from `3e811a7d807cad98.topology.gslb.yccdn.ru.` to `d5d84fgjajg4k61vh53h.8wihnuyr.apigw.yandexcloud.net.`
  trust_level: high
  notes: local resolver may continue serving cached old target until TTL expiry

