# Stage 15 Deploy Readiness and Render Freshness Guard

Date: 2026-02-28
Keys: `DTM-168`, `DTM-169`

## Scope
Introduced `agent/cloud_render_freshness_smoke.py` that combines:
1. Optional deploy wait gate via GitHub Actions API (`--wait-deploy`).
2. Cloud function invoke (`timer` mode).
3. Google Sheet corner timestamp read and freshness validation.

## Freshness Criterion
Minimum success criterion for task diagram rendering:
- Corner timestamp cell (default `A1`) must be close to now.
- Fails if `corner_age_minutes > max_age_minutes`.
- Default threshold: `20` minutes.

## Runtime Notes
- Default worksheet for task diagram: `Задачи`.
- Default timezone: `Europe/Moscow`.
- Timestamp parser supports English and Russian month names.

## Evidence (live)
- Function URL: `https://functions.yandexcloud.net/d4e81vgi5vri8poe7qba`
- Live invoke result: `invoke_status=200`, `invoke_body=!GOOD!`
- Parsed corner timestamp: `17:10 February 28`
- Freshness: `corner_age_minutes=0.8`
- Final verdict: `cloud_render_freshness_smoke_ok`

## Evidence (deploy wait gate)
- Latest deploy run reached: `run_id=22522250637`, `status=completed`, `conclusion=success`
- Final verdict: `deploy_ready run_id=22522250637`