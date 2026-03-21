# Stage 10 Owner Quickstart Checklist (Daily Serverless Operations)

## 5-Minute Daily Routine
1. Open latest `Deploy Yandex Cloud Function (main)` run in GitHub Actions.
2. Confirm workflow is green and deploy step concluded `success`.
3. Run endpoint health check:
   - `.venv\Scripts\python.exe agent\invoke_function_smoke.py --url <function_url> --healthcheck`
4. Run lightweight timer check:
   - `.venv\Scripts\python.exe agent\invoke_function_smoke.py --url <function_url> --mode timer --dry-run --mock-external`
5. Save normalized run evidence:
   - `.venv\Scripts\python.exe agent\deploy_run_evidence_report.py --per-page 1 --output-file artifacts/tmp/deploy_run_evidence.json`

## Weekly Check
1. Review rollback drill doc:
   - `doc/ops/stage10_function_rollback_drill.md`
2. Confirm Lockbox secret id and runtime service account values are unchanged in GitHub Actions config.
3. Ensure Stage 10 counters in `agile/sprint_current.md` are updated.

## Escalation Rule
- If health or timer dry-run returns `!!!EGGORR!!!`, freeze new deploys and execute rollback drill immediately.
