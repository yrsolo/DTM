"""Update job: Sheets -> normalize -> raw/prep snapshots."""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from typing import Any

from src.snapshot_engine.interfaces import Hasher, Normalizer, PrepCache, RawCache, SheetsSource
from src.snapshot_engine.model import Milestone, RawSnapshot, SheetSnapshot, TaskSheet, UpdateResult
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
        full_snapshot = self._source.fetch_snapshot("A1:Z2000")
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
                repaired_prep = self._prep_builder.build(previous_raw)
                self._prep_cache.put(repaired_prep)
                return UpdateResult(
                    source_id=self._source.source_id,
                    source_hash=source_hash,
                    changed=True,
                    fetched_at_utc=previous_raw.fetched_at_utc,
                    raw_written=False,
                    prep_written=True,
                )
            return UpdateResult(
                source_id=self._source.source_id,
                source_hash=source_hash,
                changed=False,
                fetched_at_utc=previous_raw.fetched_at_utc,
                raw_written=False,
                prep_written=False,
            )
        tasks = self._source.build_tasks(full_snapshot)
        raw = self._normalizer.normalize(
            source_id=self._source.source_id,
            source_hash=source_hash,
            snapshot=full_snapshot,
            tasks=tasks,
        )
        prep = self._prep_builder.build(raw)
        self._raw_cache.put(raw)
        self._prep_cache.put(prep)
        return UpdateResult(
            source_id=self._source.source_id,
            source_hash=source_hash,
            changed=True,
            fetched_at_utc=raw.fetched_at_utc,
            raw_written=True,
            prep_written=True,
        )
