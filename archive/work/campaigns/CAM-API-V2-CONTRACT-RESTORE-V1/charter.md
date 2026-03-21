# CAM-API-V2-CONTRACT-RESTORE-V1 - Restore API v2 default people and task business fields

## Goal
- Restore expected default API v2 behavior: people are present by default in response.
- Restore task fields in API payload by default: `brand`, `format_`, `customer`.
- Extend API docs with concrete query examples.

## Scope
- `core/api_payload_v2.py`
- `src/services/readmodel_builder.py`
- `src/entrypoints/http/frontend_v2_docs.py`
- related tests/snapshots

## Non-goals
- no business workflow changes in planner/sync logic
- no schema migrations

## DoD
- `/api/v2/frontend` default response includes non-empty `entities.people` when source has designers.
- API payload includes `brand`, `format_`, `customer` in each task by default.
- `/api/v2/frontend/doc` and JSON doc contain practical query examples.
- smoke tests green.
