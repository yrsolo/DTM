# Evidence - CAM-2026-04-09-OBJECT-STORAGE-PUT-INVESTIGATION-V1

## Trust gate
- source: current bootstrap/runtime code, current snapshot/access/attachment storage code, current runtime config, current runtime docs
- last_verified_at: 2026-04-09
- verified_by: Codex
- evidence:
  - `src/platform/bootstrap.py`
  - `src/platform/runtime/queue_bootstrap.py`
  - `src/platform/runtime/worker/status_store.py`
  - `src/platform/runtime/worker/worker.py`
  - `src/contexts/snapshot/internal/engine/stores/s3_store.py`
  - `src/contexts/snapshot/internal/update_runtime.py`
  - `src/contexts/access_api/application/primary_task_list_read_service.py`
  - `src/contexts/access_api/internal/frontend_response_cache.py`
  - `src/platform/runtime/frontend_cache_invalidation.py`
  - `config/runtime.yaml`
  - `docs/reference/runtime-modes.md`
- trust_level: high
- notes:
  - active write contours are verified directly in code and current config
  - prod dominant-source claim is additionally backed by live bucket prefix scans and recent prod function logs

## Working notes
- investigation started from the owner-observed bucket metric pattern: frequent `PUT` traffic with unclear business justification

## Findings
- active high-frequency write contour is `jobs/prod/*`, not attachment binaries and not snapshot payload files
- `S3JobStatusStore` writes on every queue lifecycle transition:
  - enqueue: `status/{job_id}.json` + `latest/{command_type}.json`
  - worker start: same two keys again
  - worker finish: same two keys again + `history/index.json` + `history/by-command/{command_type}.json`
- one command execution therefore causes `8` explicit `put_object(...)` calls in `src/platform/runtime/worker/status_store.py`
- the active prod timer plan enqueues three commands every ~10 minutes:
  - `update_snapshot`
  - `render_timeline_sheet`
  - `render_designers_sheet`
- this means the timer alone produces about `24` job-status PUTs every 10 minutes, before counting any snapshot payload persistence
- `update_snapshot` additionally writes snapshot payloads to S3:
  - `snapshots/prod/raw/default.json`
  - `snapshots/prod/prep/default.json`
  - `snapshots/prod/people/default.json`
- those snapshot writes go through `_S3JsonStore.put(...)`, which performs `put_object(temp)` + `copy_object(final)` + `delete_object(temp)` per logical file
- attachment-related object writes are currently cold in prod:
  - `attachments/prod/*` had `0` objects modified in the last 24h
  - recent attachment command history stopped on `2026-03-25`
- response-cache writes are also not the main source right now:
  - `snapshots/prod/responses/*` had only `1` object modified in the last 24h
  - the cache path only writes for one exact cache-eligible frontend query shape, while the ordinary documented browser path defaults to a different query shape

## Runtime evidence
- bucket prefix scan, last 24h:
  - `jobs/prod/`: `445` modified objects
  - `snapshots/prod/`: `4` modified objects
  - `attachments/prod/`: `0` modified objects
  - `snapshots/test/`: `1` modified object
  - `attachments/test/`: `0` modified objects
- hottest prod prefixes:
  - `jobs/prod/status/*`: `434` modified objects
  - `jobs/prod/history/*`: `6` modified objects
  - `jobs/prod/latest/*`: `5` modified objects
- prod by-command history confirms cadence:
  - `update_snapshot` finishes every ~10 minutes
  - `render_timeline_sheet` finishes every ~10 minutes
  - `render_designers_sheet` finishes every ~10 minutes
  - `send_reminders` and `cleanup_job_statuses` run once per day around `07:03Z`
- prod attachment command history is stale relative to the current day:
  - `attach_task_file`: latest `2026-03-25T00:28:29Z`
  - `generate_attachment_preview`: latest `2026-03-25T00:28:36Z`

## Verification
- command:
  - `yc serverless function logs dtm-prod --since 2h --limit 400 | Select-String -Pattern 'worker_command_finished|/api/v2/frontend'`
  - inline boto3 bucket scan for `jobs/*`, `snapshots/*`, `attachments/*` prefixes and `LastModified`
  - inline boto3 read of `jobs/prod/history/by-command/*.json`
- result:
  - prod logs show regular `update_snapshot`, `render_timeline_sheet`, and `render_designers_sheet` completions roughly every 10 minutes
  - bucket scan shows the dominant hot write surface is `jobs/prod/*`
  - snapshot/attachment prefixes are comparatively cold and cannot explain the observed steady PUT pattern on their own

## Conclusion
- the observed steady bucket write traffic is primarily self-inflicted by the scheduled queue/job-status lifecycle, not by websites mutating business data
- the most likely operator-visible source of “many PUTs” is:
  - every 10-minute timer burst
  - three queued commands per burst
  - repeated job-status overwrites per command
  - plus the three snapshot payload refresh writes from `update_snapshot`
- if cost reduction is the goal, the first place to optimize is `jobs/{env}/*` persistence policy, not attachment upload flow and not frontend read APIs
