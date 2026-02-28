# Stage 20 Release Readiness Checklist

## Goal
Provide one concise go/no-go gate before pushing current `dev` state to `main`.

## Automated checks (local)
- `python -m compileall config core agent main.py index.py`
- `python -m agent.llm_provider_bootstrap_smoke`
- `python -m agent.llm_failover_provider_smoke`
- `python -m agent.group_query_smoke`
- `python -m agent.reminder_fallback_smoke`
- `python -m agent.reminder_enhancer_counters_smoke`

## Latest evidence (2026-02-28)
- All automated checks above passed on `dev`.
- Provider routing and failover wrappers are consistent.
- Group-query parser/render smoke passed.
- Reminder fallback and enhancer counter smokes passed.

## Manual cloud checks (required before final production go)
1. Confirm latest `Deploy Yandex Cloud Function (main)` workflow run is `success`.
2. Run endpoint smoke:
   - healthcheck (`agent/invoke_function_smoke.py --healthcheck`)
   - timer dry-run (`agent/invoke_function_smoke.py --mode timer --dry-run --mock-external`)
3. Validate rendered sheet freshness:
   - corner timestamp is close to current time, not stale.
4. Verify no alert-level regression in latest quality report.

## Go/No-go rule
- `GO`: all automated checks green + all manual cloud checks green.
- `NO-GO`: any failed smoke or stale render freshness.
