# Stage 18 Provider Reliability Runtime

## Config knobs
- `LLM_HTTP_TIMEOUT_SECONDS` (default `25`)
- `LLM_HTTP_RETRY_ATTEMPTS` (default `2`)
- `LLM_HTTP_RETRY_BACKOFF_SECONDS` (default `0.8`)

## Applied to adapters
- `AsyncOpenAIChatAgent`
- `AsyncGoogleLLMChatAgent`
- `AsyncYandexLLMChatAgent`

## Retry policy
- Retries on transient failures:
  - timeout/transport errors,
  - HTTP `408/425/429/500/502/503/504`,
  - known transient text markers.
- Uses exponential backoff:
  - `backoff_seconds * 2^(attempt-1)`.
- On exhausted retries:
  - adapter returns `None`,
  - reminder falls back to draft message path.
