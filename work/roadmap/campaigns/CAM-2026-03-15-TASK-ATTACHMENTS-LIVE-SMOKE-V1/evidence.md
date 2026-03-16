# Evidence - CAM-2026-03-15-TASK-ATTACHMENTS-LIVE-SMOKE-V1

## Trust gate
- source: deployed `test` and `prod` attachment routes, current attachment docs, current attachment code
- last_verified_at: 2026-03-15
- verified_by: Codex
- evidence:
  - `docs/integrations/attachments/backend-flow.md`
  - `src/entrypoints/http/admin_task_attachments_handler.py`
  - `src/entrypoints/http/task_attachment_read_handler.py`
  - deployed `test` contour
  - deployed `prod` contour
- trust_level: high
- notes:
  - attachment contour is deployed on `test`
  - `prod` live verification requires manual production release workflow; push to `main` alone does not deploy live function
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
  - trusted/full `frontend_v2` published the attachment after worker execution
  - masked `frontend_v2` returned zero attachments for the same task
  - `view` returned `302`
  - `download` returned `302`
  - `delete` returned `202` with `attachment_delete_enqueued`
  - trusted/full `frontend_v2` no longer published the attachment after delete
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
