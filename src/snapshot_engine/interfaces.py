"""Snapshot engine protocol interfaces."""

from __future__ import annotations

from typing import Protocol

from src.snapshot_engine.model import ExtraSnapshot, PeopleSnapshot, PrepSnapshot, RawSnapshot, SheetSnapshot


class SheetsSource(Protocol):
    @property
    def source_id(self) -> str: ...

    @property
    def source_sheet_name(self) -> str: ...

    def fetch_snapshot(self, worksheet_range: str) -> SheetSnapshot: ...

    def build_tasks(self, full_snapshot: SheetSnapshot) -> list[object]: ...


class Hasher(Protocol):
    def hash_sheet_snapshot(self, snapshot: SheetSnapshot) -> str: ...


class Normalizer(Protocol):
    def normalize(self, *, source_id: str, source_hash: str, snapshot: SheetSnapshot) -> RawSnapshot: ...


class RawCache(Protocol):
    def get(self) -> RawSnapshot | None: ...
    def put(self, raw: RawSnapshot) -> None: ...


class PrepCache(Protocol):
    def get(self) -> PrepSnapshot | None: ...
    def put(self, prep: PrepSnapshot) -> None: ...


class ExtraStore(Protocol):
    def get_snapshot(self) -> ExtraSnapshot: ...
    def put_snapshot(self, snapshot: ExtraSnapshot) -> None: ...


class PeopleStore(Protocol):
    def get(self) -> PeopleSnapshot | None: ...
    def put(self, snapshot: PeopleSnapshot) -> None: ...
