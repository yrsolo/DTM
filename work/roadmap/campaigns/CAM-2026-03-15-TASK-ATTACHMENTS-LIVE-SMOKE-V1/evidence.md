# Evidence - CAM-2026-03-15-TASK-ATTACHMENTS-LIVE-SMOKE-V1

## Trust gate
- source: deployed `test` and `prod` attachment routes, current active attachment docs, current attachment code, current production release workflow
- last_verified_at: 2026-03-21
- verified_by: Codex
- evidence:
  - `docs/modules/attachments.md`
  - `docs/operations/runbook.md`
  - `src/entrypoints/http/admin_task_attachments_handler.py`
  - `src/contexts/access_api/internal/task_attachment_read_api.py`
  - `.github/workflows/release_yc_function_prod.yml`
  - deployed `test` contour
  - deployed `prod` contour
- trust_level: high
- notes:
  - attachment contour is deployed on `test`
  - `prod` live verification still requires the manual `Release Yandex Cloud Function (prod manual)` workflow; push to `main` alone does not deploy the live function
  - this campaign is verification-first and should change code only if smoke finds a defect

## Planned live checks
- `POST /ops/admin/task-attachments/request-upload`
- direct PUT to returned `uploadUrl`
- `POST /ops/admin/task-attachments/finalize`
- `GET /ops/api/v2/frontend`
- `GET /ops/api/task-attachments/{attachment_id}/view`
- `GET /ops/api/task-attachments/{attachment_id}/download`
- `POST /ops/admin/task-attachments/delete`

## Live verification

### Test contour
- verified_at: 2026-03-15
- result: passed
- contour_url: `https://dtm.solofarm.ru/test/ops`
- tested task id: `d92f8536-095f-4d64-865d-fb72b9fd05c1`
- tested attachment id: `a612e1eabbb7495c9275149ec5453296`
- checks:
  - `request-upload` returned `attachment_upload_request`
  - direct Object Storage `PUT` returned `200`
  - `finalize` returned `202` with `attachment_finalize_enqueued`
  - trusted/full primary task-list payload published the attachment after worker execution
  - masked browser payload returned zero attachments for the same task
  - `view` returned `302`
  - `download` returned `302`
  - `delete` returned `202` with `attachment_delete_enqueued`
  - trusted/full primary task-list payload no longer published the attachment after delete
- known caveats:
  - none observed on `test`

### Prod contour
- verified_at: 2026-03-15
- result: blocked
- contour_url: `https://dtm.solofarm.ru/ops`
- evidence:
  - canonical request-upload route returned runtime noop response:
    - `artifact=dtm_runtime_noop`
    - `message=HTTP request does not trigger planner without explicit mode.`
- conclusion:
  - live prod function is not on the attachment-v1 runtime yet
  - production smoke must be rerun after manual release workflow execution
  - as of 2026-03-21 the active repo still uses a manual prod release workflow, so this remains the only repo-local blocker for campaign closeout
