# Engineering Standards

## 1. Code Organization
1. Layered structure:
   - `core`: pure logic (no IO)
   - `adapters`: external systems
   - `services`: orchestration/use-cases
   - `handlers`: runtime entrypoints
2. No business rules inside adapters.
3. Strangler pattern only: new path in parallel, switch consumers gradually.

## 2. Naming and Typing
1. Use explicit names (`sync_service`, `readmodel_builder`).
2. Public functions/classes must have type hints.
3. Domain models should be dataclasses/typed objects, not untyped dicts where avoidable.

## 3. Logging Standard
- Structured JSON log payload with fields:
  - `job_id`
  - `source_id`
  - `stage`
  - `duration_ms`
  - `error_code`
  - `sync_skipped` (for hash gate)
  - `source_hash` / `previous_hash` (when applicable)

## 4. Error Standard
1. Use unified error family (`AppError`, `ErrorCode`) for new path.
2. Every error category maps to retry policy:
   - `retryable`
   - `non_retryable`
3. Do not swallow exceptions silently.

## 5. Idempotency
1. Sync:
   - run only when source hash changed.
2. Store:
   - upsert by stable `task_id` and stage keys.
3. Notifications:
   - no duplicate send in same cycle and with delivery log key.

## 6. Config and Secrets
1. Config through env vars only.
2. Secrets only from Lockbox/Secret Manager/env injection.
3. Never store secrets in git, logs, or docs.
4. Rollout switches are mandatory for staged migration:
   - `STORE_MODE=legacy|dual_write|ydb_primary|ydb_only`
   - `READMODEL_SOURCE=legacy|ydb`
   - optional `NOTIFY_SOURCE`, `RENDER_SOURCE`
5. YDB config keys:
   - `YDB_ID`
   - `YDB_ENDPOINT`
   - `YDB_DATABASE`

## 7. Integration Standards

## Google APIs
1. Reader and renderer are different adapters.
2. Reader consumes source ranges only.
3. Renderer writes target ranges only.

## Telegram
1. Delivery errors are classified (`transient/permanent`).
2. Retry with bounded attempts and backoff.
3. Delivery log written for idempotency.

## LLM (OpenAI/Google/Yandex)
1. Provider adapters must share common enhancer interface.
2. Timeout and retry are bounded.
3. Fallback policy:
   - `draft_only`
   - or configured provider failover.
4. Optional short-term cache for identical prompt payload.

## 8. Testing Standards
1. Unit tests (mandatory for new core code):
   - stage parser
   - date inference
   - normalize task
2. Snapshot tests:
   - read model outputs from fixtures.
3. Smoke:
   - compile/import checks for new modules
   - existing runtime smoke remains green.

## 9. Observability Metrics
Track at least:
1. sync latency
2. render latency
3. batch update count
4. LLM request latency
5. LLM failures by provider
6. Telegram send retries/exhausted
7. source hash gate hit rate (skipped vs executed)

## 10. Definition of Done for Migration Tasks
1. Contract updated if data shape changed.
2. Tests or smoke evidence attached.
3. No breaking changes to current entrypoints by default.
4. Rollback note exists for stage-level changes.
