# CAM-UNIFIED-API-INGRESS-V1

## Goal
Перенести test/prod API c отдельных hostnames на единый host `dtm.solofarm.ru` с path-based routing:
- `/test-front/...`
- `/prod/...`

## Scope
- repo-side base-path support for `/info`
- config URLs for test/prod path routing
- unified Yandex API Gateway on `dtm.solofarm.ru`
- old `dtm-api-*` domains stay alive as rollback path until explicit cleanup

## DoD
- `/test-front/api/v2/frontend` routes to test function
- `/prod/api/v2/frontend` routes to prod function
- `/test-front/info` operator page works with admin/API builder URLs under `/test-front`
- `/prod/info` operator page works under `/prod`
- old domains are not removed in this CAM
