"""Update job: Sheets -> normalize -> raw/prep snapshots."""

from __future__ import annotations

import hashlib
import json
from time import perf_counter
from datetime import date, datetime, timezone
from typing import Any

from src.snapshot_engine.interfaces import Hasher, Normalizer, PeopleStore, PrepCache, RawCache, SheetsSource
from src.snapshot_engine.model import Milestone, PeopleSnapshot, PersonView, RawSnapshot, SheetSnapshot, TaskSheet, UpdateResult
from src.snapshot_engine.prep_builder import PrepBuilder


class SheetSnapshotHasher:
    def hash_sheet_snapshot(self, snapshot: SheetSnapshot) -> str:
        payload = {
            "values": snapshot.values,
            "colors": snapshot.colors,
        }
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class SheetsTaskNormalizer:
    def normalize(self, *, source_id: str, source_hash: str, snapshot: SheetSnapshot, tasks: list[Any]) -> RawSnapshot:
        now = datetime.now(timezone.utc)
        tasks_by_id: dict[str, TaskSheet] = {}
        for task in tasks:
            task_id = str(getattr(task, "id", "")).strip()
            if not task_id:
                continue
            raw_status = str(getattr(task, "status", "")).strip()
            color_status = str(getattr(task, "color_status", raw_status)).strip().lower() or "unknown"
            timing_map: dict[str, list[str]] = {}
            milestones: list[Milestone] = []
            for key, stages in dict(getattr(task, "timing", {}) or {}).items():
                iso = self._to_date_iso(key)
                if not iso:
                    continue
                stage_list = [str(item).strip() for item in list(stages or []) if str(item).strip()]
                if not stage_list:
                    continue
                timing_map.setdefault(iso, []).extend(stage_list)
            if not timing_map:
                synthetic = date.today().isoformat()
                timing_map[synthetic] = ["start"]
            for iso, stage_list in timing_map.items():
                planned = self._parse_iso(iso)
                for stage in stage_list:
                    milestones.append(Milestone(type=stage, planned=planned, actual=None, status="planned"))
            tasks_by_id[task_id] = TaskSheet(
                task_id=task_id,
                title=str(getattr(task, "name", "")).strip(),
                owner_id=str(getattr(task, "designer", "")).strip(),
                group_id=str(getattr(task, "project_name", "")).strip(),
                brand=str(getattr(task, "brand", "")).strip(),
                format_=str(getattr(task, "format_", "")).strip(),
                customer=str(getattr(task, "customer", "")).strip(),
                raw_timing=str(getattr(task, "raw_timing", "")).strip(),
                status=color_status,
                history=raw_status,
                timing=timing_map,
                milestones=milestones,
            )
        return RawSnapshot(
            source_id=source_id,
            source_hash=source_hash,
            fetched_at_utc=now,
            tasks_by_id=tasks_by_id,
        )

    @staticmethod
    def _to_date_iso(value: Any) -> str:
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if hasattr(value, "date"):
            try:
                maybe_date = value.date()
                if isinstance(maybe_date, date):
                    return maybe_date.isoformat()
            except Exception:
                pass
        text = str(value or "").strip()
        if not text:
            return ""
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d.%m.%y"):
            try:
                return datetime.strptime(text[:10], fmt).date().isoformat()
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(text[:10]).date().isoformat()
        except ValueError:
            return ""

    @staticmethod
    def _parse_iso(value: str) -> date | None:
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None


class TaskSourceSheetsAdapter:
    def __init__(self, task_source: Any) -> None:
        self._task_source = task_source

    @property
    def source_id(self) -> str:
        return str(self._task_source.source_id)

    @property
    def source_sheet_name(self) -> str:
        return str(getattr(self._task_source, "source_sheet_name", ""))

    def fetch_snapshot(self, worksheet_range: str) -> SheetSnapshot:
        data = self._task_source.read_snapshot(worksheet_range)
        values = data.get("values", []) if isinstance(data, dict) else []
        colors = data.get("colors", []) if isinstance(data, dict) else []
        return SheetSnapshot(
            worksheet_range=worksheet_range,
            values=list(values) if isinstance(values, list) else [],
            colors=list(colors) if isinstance(colors, list) else [],
        )

    def build_tasks(self, full_snapshot: SheetSnapshot) -> list[Any]:
        payload = {
            "range": full_snapshot.worksheet_range,
            "values": full_snapshot.values,
            "colors": full_snapshot.colors,
        }
        return list(self._task_source.build_tasks_from_snapshot(payload))

    def read_worksheet_values(self, sheet_key: str, worksheet_range: str) -> list[list[Any]]:
        repo = getattr(self._task_source, "task_repository", None)
        if repo is None:
            return []
        source_info = getattr(repo, "source_sheet_info", None)
        service = getattr(repo, "service", None)
        if source_info is None or service is None:
            return []
        sheet_name_getter = getattr(source_info, "get_sheet_name", None)
        spreadsheet_name = str(getattr(source_info, "spreadsheet_name", "")).strip()
        if not spreadsheet_name or not callable(sheet_name_getter):
            return []
        worksheet_name = str(sheet_name_getter(sheet_key) or "").strip()
        if not worksheet_name:
            return []
        values = service.get_worksheet_values(
            spreadsheet_name=spreadsheet_name,
            worksheet_name=worksheet_name,
            worksheet_range=worksheet_range,
        )
        return list(values or [])


def normalize_person_name(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    return " ".join(text.split())


class PeopleSnapshotUpdater:
    def __init__(self, *, people_store: PeopleStore, source_id: str, people_field_map: dict[str, str]) -> None:
        self._people_store = people_store
        self._source_id = str(source_id).strip()
        self._people_field_map = dict(people_field_map)

    @staticmethod
    def _header_index(values: list[list[Any]]) -> dict[str, int]:
        if not values:
            return {}
        header = [str(item or "").strip() for item in list(values[0] or [])]
        result: dict[str, int] = {}
        for idx, column in enumerate(header):
            if column and column not in result:
                result[column] = idx
        return result

    @staticmethod
    def _cell(row: list[Any], idx: int | None) -> str:
        if idx is None or idx < 0 or idx >= len(row):
            return ""
        return str(row[idx] or "").strip()

    def run(self, source: TaskSourceSheetsAdapter) -> PeopleSnapshot:
        values = source.read_worksheet_values("people", "A1:Z200")
        header_index = self._header_index(values)
        people_by_name: dict[str, PersonView] = {}
        for row in list(values[1:] if len(values) > 1 else []):
            if not isinstance(row, list):
                continue
            name = self._cell(row, header_index.get(self._people_field_map.get("name", "")))
            name_key = normalize_person_name(name)
            if not name_key:
                continue
            person = PersonView(
                name=name,
                chat_id=self._cell(row, header_index.get(self._people_field_map.get("chat_id", ""))),
                vacation=self._cell(row, header_index.get(self._people_field_map.get("vacation", ""))),
                position=self._cell(row, header_index.get(self._people_field_map.get("position", ""))),
                person_id=self._cell(row, header_index.get(self._people_field_map.get("person_id", ""))),
            )
            people_by_name[name_key] = person
        snapshot = PeopleSnapshot(
            source_id=self._source_id,
            fetched_at_utc=datetime.now(timezone.utc),
            people_by_name=people_by_name,
        )
        self._people_store.put(snapshot)
        return snapshot


class UpdateJob:
    def __init__(
        self,
        *,
        source: SheetsSource,
        hasher: Hasher,
        normalizer: Normalizer,
        raw_cache: RawCache,
        prep_cache: PrepCache,
        prep_builder: PrepBuilder,
    ) -> None:
        self._source = source
        self._hasher = hasher
        self._normalizer = normalizer
        self._raw_cache = raw_cache
        self._prep_cache = prep_cache
        self._prep_builder = prep_builder

    def run(self, force: bool = False) -> UpdateResult:
        started_at = perf_counter()

        fetch_started = perf_counter()
        full_snapshot = self._source.fetch_snapshot("A1:Z2000")
        fetch_sheet_ms = (perf_counter() - fetch_started) * 1000.0
        source_hash = self._hasher.hash_sheet_snapshot(full_snapshot)
        try:
            previous_raw = self._raw_cache.get()
        except Exception:
            # Corrupted/legacy cache payload must not block rebuild.
            previous_raw = None
        if previous_raw is not None and previous_raw.source_hash == source_hash and not force:
            try:
                existing_prep = self._prep_cache.get()
            except Exception:
                existing_prep = None
            if existing_prep is None or existing_prep.raw_source_hash != source_hash:
                build_prep_started = perf_counter()
                repaired_prep_result = self._prep_builder.build(previous_raw)
                build_prep_ms = (perf_counter() - build_prep_started) * 1000.0
                write_prep_started = perf_counter()
                self._prep_cache.put(repaired_prep_result.prep)
                write_prep_ms = (perf_counter() - write_prep_started) * 1000.0
                timings_ms = {
                    "fetch_sheet_ms": fetch_sheet_ms,
                    "build_prep_ms": build_prep_ms,
                    "write_prep_ms": write_prep_ms,
                    "total_duration_ms": (perf_counter() - started_at) * 1000.0,
                }
                timings_ms.update(dict(repaired_prep_result.timings_ms))
                return UpdateResult(
                    source_id=self._source.source_id,
                    source_hash=source_hash,
                    changed=True,
                    fetched_at_utc=previous_raw.fetched_at_utc,
                    raw_written=False,
                    prep_written=True,
                    timings_ms=timings_ms,
                )
            return UpdateResult(
                source_id=self._source.source_id,
                source_hash=source_hash,
                changed=False,
                fetched_at_utc=previous_raw.fetched_at_utc,
                raw_written=False,
                prep_written=False,
                timings_ms={
                    "fetch_sheet_ms": fetch_sheet_ms,
                    "total_duration_ms": (perf_counter() - started_at) * 1000.0,
                },
            )
        normalize_started = perf_counter()
        tasks = self._source.build_tasks(full_snapshot)
        raw = self._normalizer.normalize(
            source_id=self._source.source_id,
            source_hash=source_hash,
            snapshot=full_snapshot,
            tasks=tasks,
        )
        normalize_ms = (perf_counter() - normalize_started) * 1000.0
        build_prep_started = perf_counter()
        prep_result = self._prep_builder.build(raw)
        build_prep_ms = (perf_counter() - build_prep_started) * 1000.0
        write_raw_started = perf_counter()
        self._raw_cache.put(raw)
        write_raw_ms = (perf_counter() - write_raw_started) * 1000.0
        write_prep_started = perf_counter()
        self._prep_cache.put(prep_result.prep)
        write_prep_ms = (perf_counter() - write_prep_started) * 1000.0
        timings_ms = {
            "fetch_sheet_ms": fetch_sheet_ms,
            "normalize_ms": normalize_ms,
            "build_prep_ms": build_prep_ms,
            "write_raw_ms": write_raw_ms,
            "write_prep_ms": write_prep_ms,
            "total_duration_ms": (perf_counter() - started_at) * 1000.0,
        }
        timings_ms.update(dict(prep_result.timings_ms))
        return UpdateResult(
            source_id=self._source.source_id,
            source_hash=source_hash,
            changed=True,
            fetched_at_utc=raw.fetched_at_utc,
            raw_written=True,
            prep_written=True,
            timings_ms=timings_ms,
        )
