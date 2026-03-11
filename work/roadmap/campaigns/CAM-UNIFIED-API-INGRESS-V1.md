# CAM-UNIFIED-API-INGRESS-V1

## Goal
Нормализовать ingress на единый host `dtm.solofarm.ru`:
- prod frontend on `/`
- prod API/admin on `/api/...` and `/info`
- prod auth on `/auth/...`
- test frontend on `/test`
- test API/admin on `/test/api/...` and `/test/info`
- test auth on `/test/auth/...`
- shared Grafana on `/grafana/...`

## Scope
- full repo-owned unified gateway spec
- config normalization for prod/test canonical URLs
- same-origin Grafana path under `/grafana/...`
- old `dtm-api-*` domains stay alive as rollback path until explicit cleanup

## DoD
- `/api/v2/frontend` routes to prod function
- `/info` routes to prod info/admin page
- `/auth/...` routes to prod auth function
- `/test/api/v2/frontend` routes to test function
- `/test/info` routes to test info/admin page
- `/test/auth/...` routes to test auth function
- `/grafana/...` proxies Grafana upstream
- root `/` serves prod frontend bucket and `/test` serves test frontend folder
- old domains are not removed in this CAM

## Result
- live gateway `d5d84fgjajg4k61vh53h` owns the canonical ingress on `dtm.solofarm.ru`
- prod canonical paths are:
  - `/`
  - `/api/...`
  - `/info`
  - `/auth/...`
- test canonical paths are:
  - `/test`
  - `/test/api/...`
  - `/test/info`
  - `/test/auth/...`
- same-origin Grafana is canonical under `/grafana/...`
- old `dtm-api-test.solofarm.ru` and `dtm-api.solofarm.ru` remain rollback-only hosts
