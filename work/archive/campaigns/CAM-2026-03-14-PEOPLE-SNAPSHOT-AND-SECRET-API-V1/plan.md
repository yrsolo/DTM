# Plan - CAM-2026-03-14-PEOPLE-SNAPSHOT-AND-SECRET-API-V1

1. Verify current people/auth/runtime paths and capture trust evidence.
2. Expand people snapshot model, updater, and serialization to retain all mapped columns and canonical auth fields.
3. Add secret-only `GET /api/v2/people` route and response contract.
4. Add/update tests for snapshot roundtrip, updater coverage, and route security.
5. Update current docs and record rollout evidence.
