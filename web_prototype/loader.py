"""Stage 8 prototype artifact loader with schema gate."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.read_model import validate_read_model_contract


class PrototypeSchemaError(RuntimeError):
    """Raised when read-model contract validation fails."""


@dataclass(frozen=True)
class PrototypePayload:
    """Container for validated prototype payload artifacts."""

    read_model: dict[str, Any]
    schema_snapshot: dict[str, Any]
    fixture_bundle: dict[str, Any]


def _load_json_from_file(path: Path) -> dict[str, Any]:
    """Load JSON payload from local filesystem path."""
    return json.loads(path.read_text(encoding="utf-8"))


def _load_json(source_mode: str, *, path: Path | None = None, s3_key: str = "") -> dict[str, Any]:
    """Load JSON payload either from filesystem path or Object Storage key."""
    mode = (source_mode or "filesystem").strip().lower()
    if mode == "filesystem":
        if path is None:
            raise ValueError("filesystem mode requires path")
        return _load_json_from_file(path)
    if mode == "object_storage":
        if not s3_key:
            raise ValueError("object_storage mode requires s3_key")
        from utils.storage import S3SnapshotStorage

        return S3SnapshotStorage().download_json(s3_key)
    raise ValueError(f"unsupported source_mode={source_mode!r}")


def _validate_schema_snapshot(read_model: dict[str, Any], schema_snapshot: dict[str, Any]) -> list[str]:
    """Validate lightweight schema snapshot compatibility against read model."""
    errors: list[str] = []
    if schema_snapshot.get("schema_version") != read_model.get("schema_version"):
        errors.append("schema_version_mismatch")
    required = schema_snapshot.get("required_top_level_fields", [])
    if isinstance(required, list):
        for field in required:
            if field not in read_model:
                errors.append(f"missing_required_field:{field}")
    else:
        errors.append("invalid_required_top_level_fields")
    return errors


def load_prototype_payload(
    *,
    source_mode: str,
    read_model_path: Path | None = None,
    schema_snapshot_path: Path | None = None,
    fixture_bundle_path: Path | None = None,
    read_model_s3_key: str = "",
    schema_snapshot_s3_key: str = "",
    fixture_bundle_s3_key: str = "",
) -> PrototypePayload:
    """Load and validate prototype payload bundle for web consumer flows."""
    read_model = _load_json(
        source_mode,
        path=read_model_path,
        s3_key=read_model_s3_key,
    )
    schema_snapshot = _load_json(
        source_mode,
        path=schema_snapshot_path,
        s3_key=schema_snapshot_s3_key,
    )
    fixture_bundle = _load_json(
        source_mode,
        path=fixture_bundle_path,
        s3_key=fixture_bundle_s3_key,
    )

    errors = validate_read_model_contract(read_model)
    errors.extend(_validate_schema_snapshot(read_model, schema_snapshot))
    if errors:
        raise PrototypeSchemaError(";".join(errors))

    return PrototypePayload(
        read_model=read_model,
        schema_snapshot=schema_snapshot,
        fixture_bundle=fixture_bundle,
    )

