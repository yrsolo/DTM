# Configuration

DTM runtime is environment-driven.

## Core groups
- Google source/target sheets and credentials.
- Telegram tokens and chat settings.
- LLM provider configuration.
- YDB test/prod contour settings.

## Rollout switches
- `STORE_MODE`
- `READMODEL_SOURCE`
- `NOTIFY_SOURCE`
- `RENDER_SOURCE`
- `FORCE_REFRESH`

## References
- `.env.example`
- `.env.dev.example`
- `.env.prod.example`
- `docs/db/migration-plan.md`
