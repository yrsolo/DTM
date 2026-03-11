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
  notes: this would break from browser-visible `/test/info` and `/prod/info`

- source: live Yandex API Gateway specs
  last_verified_at: 2026-03-11
  verified_by: Codex
  evidence: test gateway `d5dqk340tjat1ckobhev` and prod gateway `d5d1osrad1qhg1ajbhgo` each route root/proxy to a single function; certificate `fpqsk82473vprlt5fv8p` exists for `dtm.solofarm.ru`
  trust_level: high
  notes: unified path-based gateway can be introduced without deleting old domains

- source: live unified gateway rollout
  last_verified_at: 2026-03-11
  verified_by: Codex
  evidence: unified gateway `d5d84fgjajg4k61vh53h` created on `dtm.solofarm.ru`; direct gateway host returns `200` for `/test/info?format=json`, `/test/api/v2/frontend?limit=1`, `/prod/info?format=json`, `/prod/api/v2/frontend?limit=1`
  trust_level: high
  notes: routing works before DNS propagation/cache expiry

- source: live canonical host verification after test path rename
  last_verified_at: 2026-03-11
  verified_by: Codex
  evidence: `https://dtm.solofarm.ru/test/info?format=json`, `https://dtm.solofarm.ru/test/api/v2/frontend?limit=1`, `https://dtm.solofarm.ru/prod/info?format=json`, and `https://dtm.solofarm.ru/prod/api/v2/frontend?limit=1` all return `200`
  trust_level: high
  notes: canonical test ingress is now `/test`; `/test-front` is retired

- source: Yandex DNS zone `solofarm.ru`
  last_verified_at: 2026-03-11
  verified_by: Codex
  evidence: record `dtm.solofarm.ru.` replaced from `3e811a7d807cad98.topology.gslb.yccdn.ru.` to `d5d84fgjajg4k61vh53h.8wihnuyr.apigw.yandexcloud.net.`
  trust_level: high
  notes: local resolver may continue serving cached old target until TTL expiry
