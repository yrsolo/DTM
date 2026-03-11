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

## Local verification

- added `UpdateResult.timings_ms` in `src/snapshot_engine/model.py`
- added detailed timing capture in `src/snapshot_engine/update_job.py`
- added `RenderApplyResult.build_plan_ms|write_sheet_ms|total_duration_ms` in `src/render/model.py`
- added detailed render timing capture in `src/render/job.py`
- wrapper metric emission updated in:
  - `src/jobs/update_snapshot_job.py`
  - `src/jobs/render_timeline_job.py`
  - `src/jobs/render_designers_job.py`
- tests:
  - `tests/snapshot_engine/test_update_job_timings.py`
  - `tests/render/test_render_job_timings.py`
  - existing render and observability tests remain green

## Live test evidence

- deployed on `test` and triggered:
  - `POST /admin/commands/update-snapshot`
  - `POST /admin/commands/render-timeline`
- terminal job summaries now include `timings_ms`
- visible metric names in Yandex Monitoring:
  - `dtm.snapshot.fetch_sheet_ms`
  - `dtm.snapshot.normalize_ms`
  - `dtm.snapshot.build_prep_ms`
  - `dtm.snapshot.write_raw_ms`
  - `dtm.snapshot.write_prep_ms`
  - `dtm.snapshot.update_duration_ms`
  - `dtm.render.build_plan_ms`
  - `dtm.render.write_sheet_ms`
  - `dtm.render.duration_ms`

## Dashboard update

- test dashboard `fbe6m08jl1vj212t5v0c` updated
- current widgets include:
  - snapshot stage timings
  - snapshot total duration
  - render stage timings
  - render total duration
