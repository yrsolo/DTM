

1. **пересобранный план** (в виде кампаний + приоритеты)
2. **скелеты модулей** для нового нотификатора и нового рендера (с сигнатурами, без реализаций) — чтобы агент опять сделал “почти идеально с первого раза”.

---

# 1) Пересобранный план выпиливания легаси

### Ключевая мысль

Сейчас у тебя Snapshot Engine быстрый и рабочий. Legacy надо выпиливать не “везде сразу”, а по **runtime-цепочкам потребителей**:

* API v2
* Notify
* Render

Самое важное — чтобы **каждый consumer** перестал тащить `core/*`, `planner`, pandas, “Person” и т.п.

---

## `CAM-LEGACY-CUT-API-V1` — API v2 полностью на SnapshotEngine без core/api_payload_v2

**Цель:** `SnapshotQueryEngine.query_frontend_v2()` не импортирует legacy builder, не тянет pandas/Person, строит v2 payload напрямую из PrepSnapshot.

### Почему это №1

Пока API payload строится через `core.api_payload_v2`, legacy будет жить вечно.

### Фазы/таски

* P01-T001: Зафиксировать текущий API v2 контракт (поле `status` и `history`, window фильтр, include_people) как “parity spec”.
* P01-T002: Создать новый модуль `src/snapshot_engine/frontend_v2_payload_builder.py` (см. скелет ниже).
* P02-T001: Перенести сборку `entities` (people/projects) из PrepSnapshot без `core.models.people.Person`.
* P02-T002: Убрать pandas (заменить на списки/словари).
* P03-T001: Подключить builder в `SnapshotQueryEngine`.
* P04-T001: Тесты на parity (минимум 5 кейсов: statuses, window, limit, include_people, history field).
* P05-T001: Grep gate: запрет импортов `core.api_payload_v2`, `pandas`, `core.models.people` внутри `src/snapshot_engine`.

**DoD:** API v2 runtime path вообще не импортирует `core/*` и pandas.

---

## `CAM-NOTIFY-MODULE-V1` — новый модуль напоминаний без legacy

**Цель:** новый notifier использует только SnapshotEngine (PrepSnapshot + QueryEngine), не знает про planner/legacy, форматирование и отправка разделены.

### Почему лучше “переписать”, чем адаптировать

Legacy notify почти всегда тащит core и старые форматы сообщений. А новый модуль проще сделать чистым: query → format → send.

### Фазы/таски

* P01: Ввести DTO запросов/результатов напоминаний.
* P02: Реализовать `ReminderUseCase` (логика выборки задач для окна, группировка).
* P03: Реализовать `ReminderFormatter` (чистая функция формата).
* P04: Реализовать `TelegramNotifierAdapter` (инфра).
* P05: Подключить в runtime `mode=reminder` / cron.
* P06: Тесты: “окно + статусы + группировка + лимиты”.

**DoD:** reminder path не импортирует `core/*` и не читает Sheets/YDB operational.

---

## `CAM-RENDER-MODULE-V1` — новый модуль рендера таблиц без legacy

**Цель:** новый render использует SnapshotEngine для выборки задач и отдельный SheetsRendererAdapter для батч-отрисовки.

### Почему лучше переписать

Старый sheet renderer обычно содержит тонны форматирования и “всё в одном”, его трудно отвязать от legacy.

### Фазы/таски

* P01: Ввести `RenderQuery` и `RenderPlan` (что рисовать).
* P02: Реализовать `RenderUseCase` (select tasks → build plan).
* P03: Реализовать `SheetsRendererAdapter` (батчи: values + formats).
* P04: Подключить в `mode=render`.
* P05: Тесты: “build plan” без доступа к Sheets (только pure).

**DoD:** render path не импортирует `core/*` и не читает Sheets “как источник данных” (только как target для записи).

---

## `CAM-HTTP-FALLBACK-REMOVAL-V1` — убрать fallback ветки в HTTP

**Цель:** API v2 всегда идёт через SnapshotEngine. Если PrepSnapshot отсутствует — возвращает понятную ошибку/пустой ответ быстро (без попыток собрать по legacy).

**DoD:** никакого “если нет snapshot → соберём по старому”.

---

## `CAM-LEGACY-PLANNER-DELETE-V1` — удаление planner world из runtime

**Цель:** выкинуть `GoogleSheetPlanner`, `build_planner_dependencies`, `_apply_task_source_switches` и т.п. из стандартных режимов.

* P01: Найти, где planner ещё используется в runtime.
* P02: Перевести эти режимы на SnapshotEngine (обычно это notify/render/group query).
* P03: Удалить/архивировать planner код.

---

## Приоритеты (`priorities_legacy_cut.md`)

1. `CAM-LEGACY-CUT-API-V1` (самый жёсткий разрыв с core/api_payload_v2)
2. `CAM-NOTIFY-MODULE-V1`
3. `CAM-RENDER-MODULE-V1`
4. `CAM-HTTP-FALLBACK-REMOVAL-V1`
5. `CAM-LEGACY-PLANNER-DELETE-V1`
   (ExtraStore scale можно отдельно, когда enrichment реально начнёт расти.)

---

# 2) Скелеты новых модулей (сигнатуры, без реализаций)

Ниже файлы. Копируй 1:1.

---

## 2.1 Новый builder для API v2 (замена legacy builder)

### `src/snapshot_engine/frontend_v2_payload_builder.py`

```py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from snapshot_engine.model import PrepSnapshot, TaskView, FrontendV2Query


@dataclass(frozen=True)
class FrontendV2Payload:
    """Exact external payload shape: meta + filters + summary + entities + tasks."""
    data: Dict[str, Any]


class FrontendV2PayloadBuilder:
    """
    Builds API v2 payload directly from PrepSnapshot.

    Hard rules:
    - DO NOT import legacy core/api_payload_v2.
    - DO NOT use pandas.
    - task.status  <- TaskView.sheet.status (normalized)
    - task.history <- TaskView.sheet.history (raw text)
    """

    def build(self, snap: PrepSnapshot, q: FrontendV2Query, selected: List[TaskView]) -> FrontendV2Payload:
        raise NotImplementedError

    # ---- pieces ----

    def build_meta(self, snap: PrepSnapshot, q: FrontendV2Query) -> Dict[str, Any]:
        raise NotImplementedError

    def build_filters_block(self, q: FrontendV2Query) -> Dict[str, Any]:
        raise NotImplementedError

    def build_entities(self, snap: PrepSnapshot, q: FrontendV2Query, selected: List[TaskView]) -> Dict[str, Any]:
        """
        entities should contain only what is needed by UI:
        - people (owners) if include_people
        - enums used (statuses, milestoneType, etc.)
        """
        raise NotImplementedError

    def build_tasks(self, selected: List[TaskView]) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def build_summary(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        raise NotImplementedError
```

### Изменение в `src/snapshot_engine/query_engine.py` (только сигнатуры)

Добавь зависимость builder’а (в конструктор) вместо legacy.

```py
class SnapshotQueryEngine:
    def __init__(self, frontend_builder: "FrontendV2PayloadBuilder"):
        self._frontend_builder = frontend_builder
```

---

## 2.2 Новый модуль напоминаний

### `src/notify/model.py`

```py
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional

from snapshot_engine.model import TaskView, Window


@dataclass(frozen=True)
class ReminderRequest:
    window: Window
    statuses: Optional[List[str]] = None
    group_by_owner: bool = True
    limit_per_owner: Optional[int] = None


@dataclass(frozen=True)
class ReminderGroup:
    owner_id: str
    tasks: List[TaskView]


@dataclass(frozen=True)
class ReminderResult:
    groups: List[ReminderGroup]
```

### `src/notify/usecase.py`

```py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List

from snapshot_engine.engine import SnapshotEngine
from snapshot_engine.model import ReminderQuery, Window
from .model import ReminderRequest, ReminderResult


class ReminderUseCase:
    """
    Pure selection + grouping.
    Does NOT format or send.
    """

    def __init__(self, engine: SnapshotEngine):
        self._engine = engine

    def run(self, req: ReminderRequest) -> ReminderResult:
        raise NotImplementedError
```

### `src/notify/formatter.py`

```py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .model import ReminderResult, ReminderGroup


@dataclass(frozen=True)
class FormattedMessage:
    chat_id: str
    text: str


class ReminderFormatter:
    """
    Converts ReminderResult into messages.
    No IO. No Telegram client here.
    """

    def format(self, result: ReminderResult) -> List[FormattedMessage]:
        raise NotImplementedError
```

### `src/notify/telegram_sender.py`

```py
from __future__ import annotations

from typing import Iterable

from .formatter import FormattedMessage


class TelegramClient:
    def send_message(self, chat_id: str, text: str) -> None:
        raise NotImplementedError


class TelegramReminderSender:
    def __init__(self, tg: TelegramClient):
        self._tg = tg

    def send(self, messages: Iterable[FormattedMessage]) -> None:
        raise NotImplementedError
```

### `src/notify/job.py`

```py
from __future__ import annotations

from .usecase import ReminderUseCase
from .formatter import ReminderFormatter
from .telegram_sender import TelegramReminderSender
from .model import ReminderRequest


class ReminderJob:
    """
    Orchestration boundary:
    query (usecase) -> format -> send
    """

    def __init__(self, usecase: ReminderUseCase, formatter: ReminderFormatter, sender: TelegramReminderSender):
        self._usecase = usecase
        self._formatter = formatter
        self._sender = sender

    def run(self, req: ReminderRequest) -> None:
        raise NotImplementedError
```

**Правило:** notify модуль **не импортирует** `core/*` и не читает Sheets.

---

## 2.3 Новый модуль рендера таблиц

### `src/render/model.py`

```py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from snapshot_engine.model import TaskView, Window


@dataclass(frozen=True)
class RenderRequest:
    window: Optional[Window] = None
    statuses: Optional[List[str]] = None


@dataclass(frozen=True)
class RenderCell:
    row: int
    col: int
    value: Any


@dataclass(frozen=True)
class RenderFormat:
    row: int
    col: int
    fmt: Dict[str, Any]  # background/text/bold/numberFormat etc.


@dataclass(frozen=True)
class RenderPlan:
    """
    Pure plan: what values to write and what formats to apply.
    """
    values: List[RenderCell]
    formats: List[RenderFormat]
```

### `src/render/usecase.py`

```py
from __future__ import annotations

from snapshot_engine.engine import SnapshotEngine
from snapshot_engine.model import RenderQuery
from .model import RenderRequest, RenderPlan


class RenderUseCase:
    """
    Pure transformation:
    snapshot -> selected tasks -> render plan
    No Google API calls here.
    """

    def __init__(self, engine: SnapshotEngine):
        self._engine = engine

    def build_plan(self, req: RenderRequest) -> RenderPlan:
        raise NotImplementedError
```

### `src/render/sheets_adapter.py`

```py
from __future__ import annotations

from .model import RenderPlan


class SheetsWriter:
    """
    Infra adapter that writes RenderPlan into Google Sheets in batches.
    """

    def apply(self, plan: RenderPlan) -> None:
        raise NotImplementedError
```

### `src/render/job.py`

```py
from __future__ import annotations

from .usecase import RenderUseCase
from .sheets_adapter import SheetsWriter
from .model import RenderRequest


class RenderJob:
    def __init__(self, usecase: RenderUseCase, writer: SheetsWriter):
        self._usecase = usecase
        self._writer = writer

    def run(self, req: RenderRequest) -> None:
        plan = self._usecase.build_plan(req)
        self._writer.apply(plan)
```

---

