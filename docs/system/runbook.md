# Runbook (Current)

This is the minimal operator/developer runbook for the active runtime contour.

## 1) Local setup
1. Create `.env.dev` or copy from `.env.dev.example`.
2. Ensure Google credentials are available through the supported runtime inputs.
3. Ensure Object Storage credentials are available for snapshot/job-status paths.

## 2) Browser auth operations

Browser auth procedure is maintained separately:
- `docs/system/browser_auth_runbook.md`

Use that runbook for:
- auth/session route ownership
- callback paths
- proxy-secret/Lockbox wiring
- test/prod rollout verification

## 3) Snapshot refresh

Canonical refresh flow:
- fetch Sheets snapshot
- normalize to raw snapshot
- merge extra metadata into prep snapshot
- write raw/prep snapshots to Object Storage

Current data layout:
- raw snapshot
- prep snapshot
- extra bulk snapshot
- people snapshot

Canonical read path:
- API v2 reads prep snapshot
- render/reminder/group-query consume the same snapshot contour

## 4) Reminder and Telegram operations

Reminder runtime source:
- tasks from prep snapshot
- people routing from people snapshot

Webhook intake policy:
- webhook only, no polling
- validate Telegram secret header
- parse typed update
- map to internal command
- enqueue and return quickly

## 5) `/info` operator dashboard

`/info` is the operational dashboard for:
- snapshot state
- queue live state
- job history
- build/runtime metadata
- bottleneck traces and telemetry

Use `/info` first when diagnosing:
- queue/render/reminder behavior
- recent job state
- browser/API access behavior

## 6) Render safety

- render jobs may write only to approved target worksheets
- source worksheet `ТАБЛИЧКА` must never be a render target
- unsafe target returns structured blocked result

## 7) Branching and deploy

1. Development goes to `dev`.
2. Push/merge flow for `test` follows the active test deploy workflow.
3. Production release remains owner-controlled.

## 8) Guardrails

Use the anti-relapse checks before shipping architectural cleanup:
- `python scripts/check_no_monsters.py`
- `python scripts/check_no_legacy_entrypoint_imports.py`
- `python scripts/check_no_legacy_imports.py`

Purpose:
- prevent legacy contour from leaking back into active runtime paths
- keep shells thin and import-safe
- keep current runtime docs aligned with active code

## 9) Archive policy

Current runbook does not document historical planner-era or old database contours.
If historical troubleshooting detail is needed, use `docs/archive/*`.
