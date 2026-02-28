# Stage 19 Failover Policy Runtime

## Policy modes
- `LLM_FAILOVER_MODE=draft_only` (default)
  - enhancer uses only primary provider;
  - on empty/error response reminder falls back to draft message.
- `LLM_FAILOVER_MODE=provider`
  - enhancer uses primary provider first;
  - on empty/error response tries fallback provider from `LLM_FAILOVER_PROVIDER`;
  - if fallback also fails/empty, reminder falls back to draft message.

## Config
- `LLM_FAILOVER_MODE=draft_only|provider`
- `LLM_FAILOVER_PROVIDER=openai|google|yandex`
  - ignored when mode is `draft_only`,
  - ignored when same as primary provider.

## Implementation
- `core/reminder.py`:
  - `FallbackChatAdapter` wrapper with policy-aware behavior.
- `core/bootstrap.py`:
  - failover adapter composition for runtime.
- `config/constants.py`:
  - failover env parsing and validation.
