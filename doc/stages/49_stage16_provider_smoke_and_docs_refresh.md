# Stage 16 Provider Smoke And Docs Refresh

## Smoke coverage
- Added deterministic local smoke:
  - `.venv\Scripts\python.exe -m agent.llm_provider_bootstrap_smoke`
- Validates:
  - `openai -> AsyncOpenAIChatAgent`
  - `google -> AsyncGoogleLLMChatAgent`
  - `yandex -> AsyncYandexLLMChatAgent`
  - `mock_external -> MockOpenAIChatAgent`
- No external network calls are required for this smoke.

## Supporting checks
- `python -m compileall config core agent`
- `python agent/reminder_fallback_smoke.py`

## Documentation updates
- `README.md`: provider matrix and environment variables.
- `doc/03_reconstruction_backlog.md`: Stage 16 status row added.
- `agile/context_registry.md`: Stage 16 trust/evidence entry added.
