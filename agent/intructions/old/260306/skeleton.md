Ок — я могу, но прямо сейчас **не получается собрать и приложить архив**: инструменты, которые обычно пишут файлы в sandbox и упаковывают zip, возвращают ошибку (ClientResponseError). Поэтому сделаю максимально полезное: **дам полный набор черновиков модулей и документации “как файлы”** — ты копипастишь их в репо 1:1. Как только архиватор снова будет работать, я смогу упаковать это в zip.

Ниже — структура и содержимое.

---

## Структура

```
docs/snapshot_engine/README.md
docs/snapshot_engine/architecture.md
docs/snapshot_engine/migration_plan.md

src/snapshot_engine/__init__.py
src/snapshot_engine/model.py
src/snapshot_engine/interfaces.py
src/snapshot_engine/prep_builder.py
src/snapshot_engine/update_job.py
src/snapshot_engine/query_engine.py
src/snapshot_engine/engine.py

src/snapshot_engine/stores/README.md
src/snapshot_engine/stores/ydb_store.py
src/snapshot_engine/stores/s3_store.py  (опционально)

src/entrypoints_adapters/api_v2_adapter.py
src/entrypoints_adapters/notifier_adapter.py
```

---

## `docs/snapshot_engine/README.md`

```md
# Snapshot Engine (Draft)

Skeleton modules + documentation for a clean data path:

**Google Sheets → Normalize → RawCache → Merge Extra → PrepCache → QueryEngine → (API/Notify/Render)**

This is signatures-only (no implementations).

Goals:
- Keep the main pipeline readable (no feature-flag matrices in the middle).
- Store **two caches** (Raw + Prep) and a separate **ExtraStore** keyed by `task_id` (UUID from Sheets).
- Provide one unified module to query the snapshot for different consumers (API v2, notifier, renderer).
```

---

## `docs/snapshot_engine/architecture.md`

```md
# New Architecture (Draft)

## Components
- SheetsSource: reads values+colors
- Normalizer: produces TaskSheet objects + ensures milestones non-empty (adds 'start')
- RawCache: stores normalized tasks keyed by task_id, plus source_hash
- ExtraStore: enrichment keyed by task_id (docs/links/notes/artifacts)
- PrepCache: merged view + indexes for fast reads
- SnapshotQueryEngine: unified querying for API/notify/render

## Update job (timer)
1) fetch sheet snapshot
2) compute source_hash
3) if unchanged (and not forced) → stop
4) normalize → RawSnapshot
5) write RawCache
6) load extra for task_ids; mark extra orphaned for deleted ids
7) build PrepSnapshot (merge + indexes)
8) write PrepCache

## Read path
All consumers read PrepCache and query through SnapshotQueryEngine.

## Notes
- Diff is used primarily to manage lifecycle of Extra (new/orphan), not for performance.
- Indexes are optional (1000 tasks can be filtered linearly), but useful for clarity and future growth.
```

---

## `docs/snapshot_engine/migration_plan.md`

```md
# Migration plan (high level)

1) Implement SheetsSource/Hasher/Normalizer and caches.
2) Produce PrepSnapshot compatible with current API v2.
3) Switch API v2 handler to use SnapshotEngine (store+query), behind an entrypoint-only flag.
4) Switch notifier/render to use SnapshotEngine.
5) Deprecate legacy planner world usage for these consumers.
```

---

## `src/snapshot_engine/__init__.py`

```py
from .engine import SnapshotEngine
```

---

## `src/snapshot_engine/model.py`

```py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class SheetSnapshot:
    range_a1: str
    values: List[List[Any]]
    colors: Optional[List[List[Any]]] = None


@dataclass(frozen=True)
class Milestone:
    idx: int
    type: str
    planned: Optional[date] = None
    actual: Optional[date] = None
    status: Optional[str] = None
    raw_text: Optional[str] = None


@dataclass(frozen=True)
class TaskSheet:
    """
    Canonical task representation derived from Sheets only.

    status  = normalized status derived from colors (work/pre_done/wait/done)
    history = raw textual status from the sheet (free-form text), used for display/audit
    """
    task_id: str
    title: str = ""
    owner_id: str = ""
    group_id: str = ""
    brand: str = ""
    format_: str = ""
    customer: str = ""
    raw_timing: str = ""

    history: str = ""     # <-- ADD (raw textual status from source) :contentReference[oaicite:2]{index=2}
    status: str = ""      # normalized status (color-derived) :contentReference[oaicite:3]{index=3}

    date_start: Optional[date] = None
    date_end: Optional[date] = None
    milestones: List[Milestone] = field(default_factory=list)


@dataclass(frozen=True)
class RawSnapshot:
    """Normalized tasks snapshot derived from one SheetSnapshot."""
    source_hash: str
    fetched_at_utc: datetime
    tasks_by_id: Dict[str, TaskSheet]


@dataclass(frozen=True)
class TaskExtra:
    """Additional data not present in Sheets. Stored separately."""
    task_id: str
    orphaned: bool = False
    updated_at_utc: Optional[datetime] = None

    docs: List[Dict[str, Any]] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    notes: str = ""
    artifacts: List[Dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class TaskView:
    """Task view as consumed by API/notify/render."""
    task_id: str
    sheet: TaskSheet
    extra: Optional[TaskExtra] = None


@dataclass(frozen=True)
class PrepIndexes:
    by_status: Dict[str, List[str]] = field(default_factory=dict)
    by_owner: Dict[str, List[str]] = field(default_factory=dict)


@dataclass(frozen=True)
class PrepSnapshot:
    built_at_utc: datetime
    raw_source_hash: str
    tasks_by_id: Dict[str, TaskView]
    indexes: PrepIndexes = field(default_factory=PrepIndexes)


@dataclass(frozen=True)
class Window:
    start: date
    end: date
    mode: str = "intersects"


@dataclass(frozen=True)
class FrontendV2Query:
    statuses: Optional[List[str]] = None
    owner_ids: Optional[List[str]] = None
    window: Optional[Window] = None
    limit: Optional[int] = None
    include_people: bool = True


@dataclass(frozen=True)
class ReminderQuery:
    statuses: Optional[List[str]] = None
    window: Optional[Window] = None
    group_by_owner: bool = True
    limit_per_owner: Optional[int] = None


@dataclass(frozen=True)
class RenderQuery:
    statuses: Optional[List[str]] = None
    window: Optional[Window] = None
```

---

## `src/snapshot_engine/interfaces.py`

```py
from __future__ import annotations

from datetime import datetime
from typing import Protocol, Optional, Dict, Iterable

from .model import SheetSnapshot, RawSnapshot, PrepSnapshot, TaskExtra


class SheetsSource(Protocol):
    def fetch_snapshot(self) -> SheetSnapshot: ...


class Hasher(Protocol):
    def hash_sheet_snapshot(self, snapshot: SheetSnapshot) -> str: ...


class Normalizer(Protocol):
    def normalize(self, snapshot: SheetSnapshot, source_hash: str, fetched_at_utc: datetime) -> RawSnapshot:
        """
        Normalize raw snapshot into canonical tasks.
        Must fill:
        - TaskSheet.status (color-derived)
        - TaskSheet.history (raw textual status)
        """
        ...


class RawCache(Protocol):
    def get(self) -> Optional[RawSnapshot]: ...
    def put(self, raw: RawSnapshot) -> None: ...


class PrepCache(Protocol):
    def get(self) -> Optional[PrepSnapshot]: ...
    def put(self, prep: PrepSnapshot) -> None: ...


class ExtraStore(Protocol):
    def get_many(self, task_ids: Iterable[str]) -> Dict[str, TaskExtra]: ...
    def upsert(self, extra: TaskExtra) -> None: ...
    def mark_orphaned(self, task_id: str, orphaned: bool = True) -> None: ...
```

---

## `src/snapshot_engine/prep_builder.py`

```py
from __future__ import annotations

from typing import Dict, Iterable, Tuple, Optional

from .interfaces import ExtraStore
from .model import RawSnapshot, PrepSnapshot, TaskExtra, TaskView, PrepIndexes


class PrepBuilder:
    """Builds PrepSnapshot from RawSnapshot + ExtraStore."""

    def __init__(self, extra_store: ExtraStore):
        self._extra_store = extra_store

    def build(self, raw: RawSnapshot) -> PrepSnapshot:
        raise NotImplementedError

    def merge_task(self, sheet_task, extra: Optional[TaskExtra]) -> TaskView:
        raise NotImplementedError

    def build_indexes(self, tasks_by_id: Dict[str, TaskView]) -> PrepIndexes:
        """
        Indexing rule:
        - by_status uses TaskView.sheet.status (normalized color-derived status)
        - TaskView.sheet.history is NOT used for indexing (display only)
        """
        raise NotImplementedError

    def compute_id_sets(self, raw_task_ids: Iterable[str]) -> Tuple[Iterable[str], Iterable[str]]:
        """Return (active_ids, orphan_ids)."""
        raise NotImplementedError
```

---

## `src/snapshot_engine/update_job.py`

```py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .interfaces import SheetsSource, Hasher, Normalizer, RawCache, PrepCache
from .prep_builder import PrepBuilder


@dataclass(frozen=True)
class UpdateResult:
    source_hash: str
    changed: bool
    fetched_at_utc: datetime
    raw_written: bool
    prep_written: bool


class UpdateJob:
    """Periodic job: Sheets -> hash -> normalize -> RawCache -> PrepCache."""

    def __init__(
        self,
        source: SheetsSource,
        hasher: Hasher,
        normalizer: Normalizer,
        raw_cache: RawCache,
        prep_cache: PrepCache,
        prep_builder: PrepBuilder,
    ):
        self._source = source
        self._hasher = hasher
        self._normalizer = normalizer
        self._raw_cache = raw_cache
        self._prep_cache = prep_cache
        self._prep_builder = prep_builder

    def run(self, force: bool = False) -> UpdateResult:
        raise NotImplementedError

    def _now_utc(self) -> datetime:
        return datetime.now(timezone.utc)
```

---

## `src/snapshot_engine/query_engine.py`

```py
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional

from .model import PrepSnapshot, TaskView, FrontendV2Query, ReminderQuery, RenderQuery, Window


@dataclass(frozen=True)
class FrontendV2Payload:
    """Stable API v2 payload container."""
    data: Dict


@dataclass(frozen=True)
class ReminderModel:
    by_owner: Dict[str, List[TaskView]]


class SnapshotQueryEngine:
    """Unified querying for different consumers."""

    def query_frontend_v2(self, snap: PrepSnapshot, q: FrontendV2Query) -> FrontendV2Payload:
        raise NotImplementedError

    def query_reminders(self, snap: PrepSnapshot, q: ReminderQuery) -> ReminderModel:
        raise NotImplementedError

    def query_render(self, snap: PrepSnapshot, q: RenderQuery) -> List[TaskView]:
        raise NotImplementedError

    # Shared primitives
    def select_by_status(self, snap: PrepSnapshot, statuses: Optional[List[str]]) -> List[TaskView]:
        """
        Filter rule:
        - compares statuses with TaskView.sheet.status (normalized)
        - does NOT filter by TaskView.sheet.history (raw text)
        """
        raise NotImplementedError

    def filter_by_owner(self, tasks: List[TaskView], owner_ids: Optional[List[str]]) -> List[TaskView]:
        raise NotImplementedError

    def filter_by_window(self, tasks: List[TaskView], window: Optional[Window]) -> List[TaskView]:
        raise NotImplementedError

    def apply_limit(self, tasks: List[TaskView], limit: Optional[int]) -> List[TaskView]:
        raise NotImplementedError

    def _intersects(self, start: Optional[date], end: Optional[date], w: Window) -> bool:
        raise NotImplementedError
```

---

## `src/snapshot_engine/engine.py`

```py
from __future__ import annotations

from .interfaces import RawCache, PrepCache
from .model import FrontendV2Query, ReminderQuery, RenderQuery, PrepSnapshot
from .query_engine import SnapshotQueryEngine, FrontendV2Payload, ReminderModel


class SnapshotEngine:
    """Facade used by API/Notify/Render."""

    def __init__(self, raw_cache: RawCache, prep_cache: PrepCache, query_engine: SnapshotQueryEngine):
        self._raw_cache = raw_cache
        self._prep_cache = prep_cache
        self._query_engine = query_engine

    def get_prep(self) -> PrepSnapshot:
        snap = self._prep_cache.get()
        if snap is None:
            raise RuntimeError("PrepSnapshot is missing")
        return snap

    def frontend_v2(self, q: FrontendV2Query) -> FrontendV2Payload:
        return self._query_engine.query_frontend_v2(self.get_prep(), q)

    def reminders(self, q: ReminderQuery) -> ReminderModel:
        return self._query_engine.query_reminders(self.get_prep(), q)

    def render_selection(self, q: RenderQuery):
        return self._query_engine.query_render(self.get_prep(), q)
```

---

## `src/snapshot_engine/stores/README.md`

```md
# Stores (Draft)

Concrete implementations go here (YDB/S3/Redis/local json).

The skeleton provides signatures only.
```

---

## `src/snapshot_engine/stores/ydb_store.py`

```py
from __future__ import annotations

from typing import Optional, Dict, Iterable

from ..interfaces import RawCache, PrepCache, ExtraStore
from ..model import RawSnapshot, PrepSnapshot, TaskExtra


class YdbRawCache(RawCache):
    def __init__(self, client, table_name: str = "dtm_raw_snapshot"):
        self._client = client
        self._table = table_name

    def get(self) -> Optional[RawSnapshot]:
        raise NotImplementedError

    def put(self, raw: RawSnapshot) -> None:
        raise NotImplementedError


class YdbPrepCache(PrepCache):
    def __init__(self, client, table_name: str = "dtm_prep_snapshot"):
        self._client = client
        self._table = table_name

    def get(self) -> Optional[PrepSnapshot]:
        raise NotImplementedError

    def put(self, prep: PrepSnapshot) -> None:
        raise NotImplementedError


class YdbExtraStore(ExtraStore):
    def __init__(self, client, table_name: str = "dtm_task_extra"):
        self._client = client
        self._table = table_name

    def get_many(self, task_ids: Iterable[str]) -> Dict[str, TaskExtra]:
        raise NotImplementedError

    def upsert(self, extra: TaskExtra) -> None:
        raise NotImplementedError

    def mark_orphaned(self, task_id: str, orphaned: bool = True) -> None:
        raise NotImplementedError
```

---

## `src/snapshot_engine/stores/s3_store.py` (опционально)

```py
from __future__ import annotations

from typing import Optional

from ..interfaces import RawCache, PrepCache
from ..model import RawSnapshot, PrepSnapshot


class S3RawCache(RawCache):
    def __init__(self, s3_client, bucket: str, key: str):
        self._s3 = s3_client
        self._bucket = bucket
        self._key = key

    def get(self) -> Optional[RawSnapshot]:
        raise NotImplementedError

    def put(self, raw: RawSnapshot) -> None:
        raise NotImplementedError


class S3PrepCache(PrepCache):
    def __init__(self, s3_client, bucket: str, key: str):
        self._s3 = s3_client
        self._bucket = bucket
        self._key = key

    def get(self) -> Optional[PrepSnapshot]:
        raise NotImplementedError

    def put(self, prep: PrepSnapshot) -> None:
        raise NotImplementedError
```

---

## `src/entrypoints_adapters/api_v2_adapter.py`

```py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional

from snapshot_engine.engine import SnapshotEngine
from snapshot_engine.model import FrontendV2Query


@dataclass(frozen=True)
class ApiRequest:
    path: str
    query: Dict[str, str]
    body: Optional[Dict[str, Any]] = None


class ApiV2Adapter:
    """Parse HTTP request -> FrontendV2Query -> stable API v2 payload."""

    def __init__(self, engine: SnapshotEngine):
        self._engine = engine

    def handle_frontend_v2(self, req: ApiRequest) -> Dict[str, Any]:
        # TODO: parse query params into FrontendV2Query
        q = FrontendV2Query()
        payload = self._engine.frontend_v2(q)
        return payload.data
```

---

## `src/entrypoints_adapters/notifier_adapter.py`

```py
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from snapshot_engine.engine import SnapshotEngine
from snapshot_engine.model import ReminderQuery, Window


@dataclass(frozen=True)
class NotifyRequest:
    window_start: date
    window_end: date
    statuses: Optional[List[str]] = None


class NotifierAdapter:
    def __init__(self, engine: SnapshotEngine, notifier):
        self._engine = engine
        self._notifier = notifier

    def run(self, req: NotifyRequest) -> None:
        q = ReminderQuery(statuses=req.statuses, window=Window(req.window_start, req.window_end))
        model = self._engine.reminders(q)
        # TODO: format + send
        raise NotImplementedError
```

---

### Если хочешь, я добавлю ещё 2 “чистых” файла

1. `docs/snapshot_engine/api_v2_parity.md` — точные правила фильтров (statuses → owner → window(intersects) → limit) для совпадения с текущим API.
2. `src/snapshot_engine/adapters/api_v2_payload_mapper.py` — сигнатуры маппера из `TaskView` в твой текущий v2 контракт.

Скажи только: **в v2 payload вы хотите хранить `TaskView` как `sheet+extra` (внутри `tasks[]`) или `extra` должно быть отдельным полем/разделом?** Это влияет только на mapper, не на архитектуру.
