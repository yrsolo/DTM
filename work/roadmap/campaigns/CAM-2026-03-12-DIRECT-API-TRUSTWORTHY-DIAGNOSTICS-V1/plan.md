# Plan - CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1

## P01
- `CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1-P01-T001` split direct `/api` outer timing into `router_precheck_total`, `router_handler_total`, `router_total`, `http_shell_post_router`, `function_total`
- `CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1-P01-T002` add `query_parse` and `handler_total` to `FrontendV2Handler` and remove conflicting total ownership

## P02
- `CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1-P02-T001` update `/info`, Grafana spec, and metrics docs to the new direct `/api` diagnostic contract
- `CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1-P02-T002` extend unit tests so direct `/api` traces are internally consistent and free of duplicate totals

## P03
- `CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1-P03-T001` deploy to `test`
- `CAM-2026-03-12-DIRECT-API-TRUSTWORTHY-DIAGNOSTICS-V1-P03-T002` capture live `Server-Timing` and `/info` detail evidence for one direct `/api` cache-hit request
