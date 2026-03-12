# CAM-2026-03-10-DATALENS-OPS-DASHBOARD-V1 Evidence

## Trust Gate

### Source: current Monitoring baseline
- last_verified_at: 2026-03-10
- verified_by: Codex
- evidence:
  - `src/observability/metrics.py`
  - `src/infra/yc_monitoring.py`
  - `config/runtime.yaml`
- trust_level: high
- notes: Monitoring custom metrics backend already exists and emits real metrics on test contour.

### Source: Yandex DataLens Public API
- last_verified_at: 2026-03-10
- verified_by: Codex
- evidence:
  - `https://api.datalens.tech/json/`
  - authenticated `POST /rpc/getWorkbooksList`
- trust_level: high
- notes: API reachable; required headers confirmed as `x-yacloud-subjecttoken`, `x-dl-org-id`, `x-dl-api-version: 1`.

### Source: DataLens provisioning permissions
- last_verified_at: 2026-03-10
- verified_by: Codex
- evidence:
  - workbook created: `ppzr9qy22doe9`
  - connection created: `iisk41ymvyb02`
  - service account `aje1kqd422vq2vefkbbl` granted `monitoring.viewer`
- trust_level: medium
- notes: workbook and connection creation are proven. Chart payload shape still requires verification against live API.

## Provisioning baseline
- org_id: `bpf5f34jd486mus03s8i`
- cloud_id: `b1g6d49mf4scmtn4kjki`
- folder_id: `b1g42qj26s1u7gv7bufm`
- workbook_name: `DTM Observability`
- workbook_id: `ppzr9qy22doe9`
- connection_name_test: `DTM Monitoring Test`
- connection_id_test: `iisk41ymvyb02`

## Live provisioning results
- workbook create/find: success
- Monitoring connection create/get: success
- DataLens Public API auth: success with:
  - `x-yacloud-subjecttoken`
  - `x-dl-org-id`
  - `x-dl-api-version: 1`
- service account `aje1kqd422vq2vefkbbl` granted `monitoring.viewer`: success
- DataLens API caller `yrsolo` (`ajefe72hh45gqvhnje76`) granted:
  - `viewer`
  - `monitoring.viewer`
  on folder `b1g42qj26s1u7gv7bufm`: success
- `createQLChart` against Monitoring connection:
  - status: blocked
  - live error: `500 {"error":"Access service error"}`
  - observed for multiple payload variants:
    - connection entry payload variants
    - metric selector via direct metric name
    - selector via `service="custom", name="..."`
    - repeated after caller permission fix
  - conclusion: workbook/connection provisioning is proven; chart automation remains blocked by DataLens/Monitoring service behavior or unsupported QL semantics for this connection type in Public API.

## Current output of CAM
- repo now has typed `datalens` config
- thin DataLens API/spec modules exist
- `/info` exposes additive DataLens metadata
- local provisioning script exists:
  - `scripts/provision_datalens_dashboard.py`
- test-side Yandex objects created:
  - workbook
  - Monitoring connection
- dashboard/chart creation is not yet completed due external blocker above

## Notes
- Current one-function topology remains unchanged.
- Workbook import/export is not the primary path because Monitoring connection support is constrained there.
- Folder-access hypothesis is now exhausted:
  - connection service account has `monitoring.viewer`
  - real API caller has `viewer` and `monitoring.viewer`
  - blocker persists unchanged
