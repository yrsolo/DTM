# CAM-2026-03-10-DATALENS-OPS-DASHBOARD-V1

## Goal
Create a test-first operator dashboard in Yandex DataLens over existing Yandex Monitoring custom metrics.

## Scope
- Add typed DataLens config and metadata plumbing.
- Add thin DataLens Public API adapter and declarative dashboard specs.
- Provision Monitoring connection, workbook, charts, and dashboard for `env=test`.
- Expose additive dashboard metadata in `/info`.
- Capture provisioning and smoke evidence.

## Non-goals
- No workbook JSON import/export flow.
- No dataset-first BI layer.
- No change to Monitoring metric schema or runtime instrumentation.
- No automatic prod rollout in this CAM.

## Delivery
- `config/runtime.yaml` + typed schema/loader updated with `datalens` section.
- `src/infra/datalens_api.py` and `src/infra/datalens_specs.py` implemented.
- `/info` includes additive DataLens metadata.
- Test DataLens dashboard exists and is backed by live Monitoring metrics.

## Implementation skeleton reference
- Primary implementation source: `docs/system/yc_monitoring_integration.md`
- Current runtime touchpoints: `src/config/schema.py`, `src/config/loader.py`, `src/entrypoints/http/info_handler.py`, `src/infra/yc_iam.py`
- Forbidden shortcuts: workbook JSON import/export as primary path, dataset layer in v1, topology changes
