# Risk Register

## Формат
- `id`
- `risk`
- `probability` (`low|medium|high`)
- `impact` (`low|medium|high|critical`)
- `mitigation`
- `owner`
- `status`

## Активные риски
1. `R-001`
- risk: запись в боевую таблицу из локального/тестового запуска.
- probability: medium
- impact: critical
- mitigation: `SOURCE_SHEET_NAME`/`TARGET_SHEET_NAME`, hard guard по `ENV`, dry-run по умолчанию для dev.
- owner: tech lead
- status: open

2. `R-002`
- risk: утечка секретов (токены, ключи, proxy credentials) в git.
- probability: high
- impact: critical
- mitigation: secret scanner в pre-commit/CI, `.env` only, sanitation tracked файлов.
- owner: tech lead
- status: open

3. `R-003`
- risk: дубли Telegram-напоминаний при повторном триггере.
- probability: medium
- impact: high
- mitigation: idempotency key (`date+designer+run_id`), журнал отправок.
- owner: backend
- status: open

4. `R-004`
- risk: ошибки дат/таймзоны (неверный день и дедлайн).
- probability: medium
- impact: high
- mitigation: единая зона в domain, тесты на пятница/выходные/переход месяца.
- owner: backend
- status: open

5. `R-005`
- risk: лимиты/деградация Google API.
- probability: medium
- impact: high
- mitigation: retry/backoff, батчирование, метрики ошибок квоты.
- owner: backend
- status: open

6. `R-006`
- risk: недоступность OpenAI и срыв рассылки.
- probability: medium
- impact: medium
- mitigation: fallback на deterministic черновик без LLM.
- owner: backend
- status: open
