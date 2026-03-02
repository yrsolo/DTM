"""Primary normalization interface."""

from __future__ import annotations

from datetime import date

from src.core.models.contracts import StageNormalized, TaskNormalized, TaskRaw
from src.core.normalize.date_inference import infer_date
from src.core.normalize.stage_parser import parse_stages


def _build_task_id(raw: TaskRaw) -> str:
    return f"{raw.source_file_id}:{raw.source_sheet_name}:{raw.source_row_id}"


def normalize_task(raw: TaskRaw, anchor_date: date, prev_date: date | None = None) -> TaskNormalized:
    """Normalize one raw task.

    This is intentionally minimal for M1-M3 and safe to evolve incrementally.
    """
    task_id = _build_task_id(raw)
    stage_lines = parse_stages(raw.stages_raw)
    stages: list[StageNormalized] = []
    latest_date = prev_date

    for idx, line in enumerate(stage_lines):
        token = line.split()[-1] if line.split() else ""
        inferred = infer_date(token, anchor=anchor_date, prev=latest_date)
        if inferred.value is not None:
            latest_date = inferred.value
        stages.append(
            StageNormalized(
                task_id=task_id,
                idx=idx,
                type="stage",
                planned_at=inferred.value,
                fact_at=None,
                status="planned",
                raw_text=line,
                inference_rule=inferred.rule,
                confidence=inferred.confidence,
            )
        )

    next_due = min((stage.planned_at for stage in stages if stage.planned_at is not None), default=None)
    return TaskNormalized(
        task_id=task_id,
        title=raw.title_raw.strip(),
        project=None,
        designer_id=(raw.designer_raw.strip() or None),
        status=(raw.status_raw.strip() or "work"),
        stages=stages,
        next_due_at=next_due,
        raw_fields={
            "title_raw": raw.title_raw,
            "designer_raw": raw.designer_raw,
            "timings_raw": raw.timings_raw,
            "stages_raw": raw.stages_raw,
            "status_raw": raw.status_raw,
        },
        inference={
            "date_strategy": "year_by_anchor",
            "confidence": min((stage.confidence for stage in stages), default=0.0),
        },
    )

