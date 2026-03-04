# CAM-API-V2-CONTRACT-RESTORE-V1 Evidence

## Trust Registry
| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| `core/api_payload_v2.py`, `src/services/readmodel_builder.py`, `src/entrypoints/http/frontend_v2_docs.py`, `src/entrypoints/http/frontend_v2_handler.py` | 2026-03-04 | TeamLead agent | direct code scan (`Get-Content`, `rg`) | high | confirms: readmodel builder stores payload with `include_people=False`; task payload omits `brand/format_/customer`; docs have no request examples block |
| `tests/api/test_frontend_api_v2_payload.py`, `tests/api/test_frontend_api_routing.py`, snapshots | 2026-03-04 | TeamLead agent | direct test/snapshot scan | high | baseline for contract update |

## Execution Log
- `APICONTRACT-P02-T001` completed: task payload now includes `brand`, `format_`, `customer` in `tasks[]`; snapshots/tests updated.
- `APICONTRACT-P02-T002` completed: readmodel builder now populates people from task owner rows and stores snapshot with `include_people=true` by default.
- `APICONTRACT-P02-T003` completed: API v2 docs now contain practical query examples in JSON and HTML docs.
- `APICONTRACT-P03-T001` completed: targeted smoke contour passed.

## Verification
- `python -m unittest tests.api.test_frontend_api_v2_payload tests.api.test_frontend_api_routing tests.services.test_readmodel_uses_milestones_table tests.services.test_pipeline_runtime tests.services.test_planner_pipeline_job tests.services.test_sync_source_hash_gate -v`
- `rg -n "include_people=False|brand|format_|customer|examples" core src/entrypoints/http src/services tests -S`
