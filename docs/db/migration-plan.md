# DTM DB Migration Plan (YDB)

## Rollout Modes
- `STORE_MODE=legacy|dual_write|ydb_primary|ydb_only`
- `READMODEL_SOURCE=legacy|ydb`
- `NOTIFY_SOURCE=legacy|ydb`
- `RENDER_SOURCE=legacy|ydb`

## Stage Order

### Stage 1: Dual-write baseline
- Enable `STORE_MODE=dual_write`.
- Keep read paths on legacy.
- Verify:
  - task upserts land in `dtm_tasks`
  - milestones land in `dtm_task_milestones`
  - `dtm_sync_state` updated by source-range hash.

### Stage 2: Readmodel materialization
- Run readmodel builder job into `dtm_readmodel_frontend_v2`.
- Verify row `frontend_v2:default` exists and updates on source hash changes.

### Stage 3: API v2 read from readmodel
- Set `READMODEL_SOURCE=ydb`.
- Verify API v2 does one readmodel query and returns stored `payload_json`.

### Stage 4: Render/Notify source switch
- Move render and notify to YDB-backed operational/readmodel sources.
- Verify regular timer/morning flows and smoke metrics.

### Stage 5: Primary and strict mode
- Switch `STORE_MODE=ydb_primary` then `STORE_MODE=ydb_only`.
- In production `ydb_only` has no JSON fallback.

## Safety Notes
- Use bounded retries and backoff for `RESOURCE_EXHAUSTED`.
- Keep schema creation idempotent (`ensure_tables`).
- Keep cloud verification evidence in sprint/task logs before promotion to prod.

