# CAM-2026-03-15-TASK-ATTACHMENTS-LIVE-SMOKE-V1

## Goal
Verify the full task-attachment lifecycle on live contours:
- `request-upload`
- direct upload to Object Storage
- `finalize`
- publication into `frontend_v2`
- `view` / `download`
- `delete`

## Steps
1. Pick one live task id per contour using current `frontend_v2`.
2. Run canonical smoke on `test`.
3. If `test` passes, run the same smoke on `prod`.
4. Record evidence, caveats, and exact routes/status codes.
5. If smoke finds a defect, fix only the issue required to pass the lifecycle.

## Acceptance
- `request-upload` returns a valid upload contract
- direct PUT succeeds
- `finalize` returns `202 accepted`
- attachment appears in trusted/full `frontend_v2`
- `view` and `download` return redirect/presigned read URLs
- masked `frontend_v2` keeps attachments hidden
- `delete` removes the attachment from published payload

## Notes
- main test file format: `docx`
- optional second format: `image/png`
- compatibility paths are checked only as backward-compat, not as canonical operator flow
