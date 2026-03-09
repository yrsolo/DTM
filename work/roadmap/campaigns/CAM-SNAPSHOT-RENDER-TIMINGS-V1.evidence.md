# CAM-SNAPSHOT-RENDER-TIMINGS-V1 Evidence

## Trust gate

- source: active runtime code and metrics schema
- last_verified_at: 2026-03-09
- verified_by: Codex
- evidence:
  - `src/jobs/update_snapshot_job.py`
  - `src/snapshot_engine/update_job.py`
  - `src/jobs/render_timeline_job.py`
  - `src/jobs/render_designers_job.py`
  - `src/render/job.py`
  - `src/render/usecase.py`
  - `src/render/sheets_adapter.py`
  - `docs/system/metrics_schema.md`
- trust_level: high
- notes:
  - coarse total timings already exist
  - detailed snapshot/render timing metric names are already declared in docs
  - implementation gap is inside active runtime, not in Monitoring backend

## Baseline facts

- snapshot currently emits only `dtm.snapshot.update_duration_ms`
- render currently emits only `dtm.render.duration_ms`
- detailed metric names already exist in `docs/system/metrics_schema.md`
