# Stage 7 Read-Model Consumer Policy

## Purpose
Define stable consumer rules for read-model usage and artifact storage in serverless runtime.

## 1) Compatibility Policy
- Contract source of truth: `doc/11_stage6_read_model_contract.md`.
- Mandatory top-level fields for consumers:
  - `schema_version`
  - `source`
  - `board`
  - `task_details`
  - `alerts`
  - `quality_summary`
- Compatibility rules:
  - Patch-level update: add optional fields only; existing fields and semantics unchanged.
  - Minor-level update: add new sections/fields with backward-compatible defaults.
  - Major-level update: allowed only when breaking field shape/semantics; requires migration note and consumer upgrade plan.
- Consumer guard:
  - Validate `schema_version` prefix and required fields before rendering.
  - Treat unknown fields as non-fatal.
  - Missing required fields -> fail-fast with explicit diagnostic.

## 2) Artifact Storage Contour (Serverless)
- Production/serverless runtime target: Yandex Object Storage (S3-compatible).
- Local filesystem artifacts (`artifacts/...`) remain dev-only and non-authoritative for cloud runs.
- Cloud storage is the primary location for:
  - `read_model.json`
  - `quality_report.json`
  - `alert_evaluation.json`
  - `schema_snapshot.json` (Stage 7+)
  - `fixture_bundle.json` (Stage 7+)

## 3) Key Naming Convention (Object Storage)
- Bucket: from environment (for example `DTM_ARTIFACTS_BUCKET`).
- Prefix template:
  - `dtm/<env>/<artifact_type>/<YYYY>/<MM>/<DD>/<run_id>.json`
- Example keys:
  - `dtm/prod/read_model/2026/02/27/run_20260227T181500Z.json`
  - `dtm/prod/schema_snapshot/2026/02/27/run_20260227T181500Z.json`

## 4) Runtime Modes
- `local/dev`:
  - write artifacts to `artifacts/...`
  - optional upload to Object Storage for parity checks.
- `serverless/prod`:
  - write artifacts directly to Object Storage.
  - filesystem path allowed only for temporary `/tmp` buffering.

## 5) Acceptance Gate for Stage 8
- Consumer prototype must use read-model only through this policy.
- Artifact location must be environment-driven (`local` vs `object_storage`) with no hardcoded local path in cloud runtime.
- Schema and fixture artifacts must be reproducible from the same run id.

## Runtime flags (current)
- `local_run.py --schema-snapshot-file <path>`: write local schema snapshot artifact.
- `local_run.py --schema-snapshot-s3-key <key>`: upload schema snapshot to Object Storage (requires S3 env credentials and bucket).
