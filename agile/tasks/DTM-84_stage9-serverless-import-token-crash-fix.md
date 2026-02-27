# DTM-84: Serverless import token crash fix + invoke smoke script

## Context
- Cloud function returned `InvalidToken` during module import.
- Root cause: eager `TelegramNotifier` construction at import/startup paths.

## Goal
- Prevent import/startup crash when Telegram token is invalid or absent.
- Keep reminder logging/send behavior fail-safe.
- Add a simple reproducible invoke smoke script for cloud endpoint checks.

## Non-goals
- No business logic redesign for reminders.
- No migration of secret strategy in this task.

## Plan
1. Remove eager notifier creation in utility import path.
2. Switch `TelegramNotifier` to lazy bot creation in send path.
3. Add `agent/invoke_function_smoke.py` for direct endpoint check.
4. Run smoke checks and update docs/tracking.

## Checklist (DoD)
- [x] Jira key exists (`DTM-84`) and moved to `V rabote` before changes.
- [x] Import-time notifier side effect removed.
- [x] Telegram bot initialization is lazy and fail-safe.
- [x] Cloud function invoke smoke utility script added.
- [ ] Jira evidence comment added.
- [ ] Jira moved to `Gotovo`.
- [ ] Telegram completion sent.

## Work log
- 2026-02-27: Created `DTM-84`, moved to `V rabote`.
- 2026-02-27: Removed eager notifier in `utils/service.py`; implemented lazy bot init in `core/reminder.py`.
- 2026-02-27: Added `agent/invoke_function_smoke.py` for endpoint smoke checks.

## Links
- Jira: DTM-84
- Failing endpoint: `https://functions.yandexcloud.net/d4e81vgi5vri8poe7qba`
