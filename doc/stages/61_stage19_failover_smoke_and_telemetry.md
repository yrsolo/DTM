# Stage 19 Failover Smoke And Telemetry

## New telemetry fields
- `reminder_enhancer_failover_mode`
- `reminder_enhancer_failover_primary_provider`
- `reminder_enhancer_failover_fallback_provider`
- `reminder_enhancer_failover_calls`
- `reminder_enhancer_failover_success_count`

## Smoke coverage
- `.venv\Scripts\python.exe -m compileall config core agent main.py`
- `.venv\Scripts\python.exe -m agent.llm_provider_bootstrap_smoke`
- `.venv\Scripts\python.exe -m agent.llm_failover_provider_smoke`
- `.venv\Scripts\python.exe -m agent.reminder_enhancer_counters_smoke`

## Notes
- Failover remains single-hop by design.
- Draft fallback behavior remains final safety net.
