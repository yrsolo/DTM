# Charter - CAM-2026-03-14-PEOPLE-SNAPSHOT-AND-SECRET-API-V1

## Goal
- Expand the people snapshot from a reminder-only subset into a full normalized registry based on the `Люди` worksheet.
- Expose the full registry through a secret-only internal API for auth-support use cases.

## Constraints
- Keep `frontend_v2` payload and browser auth behavior unchanged.
- Reuse existing trusted secret header and backend secret source.
- Preserve reminder compatibility.

## Acceptance
- `update_snapshot` writes a full-fidelity people snapshot with all mapped columns.
- `GET /api/v2/people` returns the full snapshot only when `X-DTM-Proxy-Secret` is valid.
- Existing reminder tests and frontend routing tests remain green.
