# Evidence

## Trust Gate

- source: `config/llm.yaml`, `src/contexts/reminders/module.py`, `src/contexts/reminders/internal/job_runner.py`, `src/entrypoints/runtime/planner_runtime_entry.py`
- last_verified_at: 2026-04-26
- verified_by: Codex
- evidence: reminder model selection is owned by the reminders module and consumed by both queued and direct planner reminder paths.
- trust_level: high
- notes: Follow-up refinement to keep model routing in config shape rather than encoding one config key per runtime mode.

## Verification

- 2026-04-26: `python -m pytest tests/contexts/reminders/test_reminder_model_selection.py tests/contexts/reminders/test_send_reminders_job.py tests/entrypoints/test_planner_runtime_entry.py tests/platform/test_orchestration.py -q` passed, 18 tests.
- 2026-04-26: `python -m pytest tests/config/test_runtime_loader.py tests/architecture/test_guardrails_v0.py -q` passed, 55 tests.
- 2026-04-26: config load check printed `openai_default=gpt-4o` and `openai_by_mode={'morning': 'gpt-5.5'}`.
