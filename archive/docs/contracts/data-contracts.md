# Data Contracts (Raw -> Normalized -> Read Models)

## Versioning
- Contract version: `v1`.
- Backward-incompatible changes require new version (`v2`) and migration note.

## Common Rules
1. Keep source identifiers stable.
2. Preserve raw textual fields for debugging (`raw_fields`).
3. Every inferred field must include `inference_rule` and `confidence`.
4. Date/time are ISO-like (`YYYY-MM-DD` or RFC3339 for datetime).

## TaskRaw

### Fields
- `source_file_id: str` (required)
- `source_sheet_name: str` (required)
- `source_row_id: str` (required, stable row key)
- `title_raw: str` (required)
- `designer_raw: str` (optional)
- `timings_raw: str` (optional)
- `stages_raw: str` (optional)
- `status_raw: str` (optional)
- `updated_at_source: str | null` (optional)
- `raw_hash_basis: dict[str, str]` (required; only source-range fields)

### Example
```json
{
  "source_file_id": "1AbCd",
  "source_sheet_name": "ТАБЛИЧКА",
  "source_row_id": "row-248",
  "title_raw": "Промо ролик / проект А",
  "designer_raw": "Ирина",
  "timings_raw": "05.03, 08.03",
  "stages_raw": "Черновик 05.03; Финал 08.03",
  "status_raw": "work",
  "updated_at_source": null,
  "raw_hash_basis": {
    "title_raw": "Промо ролик / проект А",
    "designer_raw": "Ирина",
    "timings_raw": "05.03, 08.03",
    "stages_raw": "Черновик 05.03; Финал 08.03",
    "status_raw": "work"
  }
}
```

## TaskNormalized

### Fields
- `task_id: str` (required, stable; e.g. `source_file_id:sheet:row`)
- `title: str` (required)
- `project: str | null` (optional)
- `designer_id: str | null` (optional)
- `status: str` (required enum-like)
- `stages: StageNormalized[]` (required)
- `next_due_at: str | null` (derived)
- `raw_fields: dict[str, str]` (required)
- `inference: dict[str, object]` (required; includes confidence)

### Example
```json
{
  "task_id": "1AbCd:ТАБЛИЧКА:row-248",
  "title": "Промо ролик / проект А",
  "project": "проект А",
  "designer_id": "designer_irina",
  "status": "work",
  "stages": [
    {
      "task_id": "1AbCd:ТАБЛИЧКА:row-248",
      "idx": 0,
      "type": "draft",
      "planned_at": "2026-03-05",
      "fact_at": null,
      "status": "planned",
      "raw_text": "Черновик 05.03",
      "inference_rule": "dd.mm->year_by_anchor",
      "confidence": 0.9
    }
  ],
  "next_due_at": "2026-03-05",
  "raw_fields": {
    "timings_raw": "05.03, 08.03",
    "stages_raw": "Черновик 05.03; Финал 08.03"
  },
  "inference": {
    "date_strategy": "year_by_anchor",
    "confidence": 0.9
  }
}
```

## StageNormalized

### Fields
- `task_id: str` (required)
- `idx: int` (required)
- `type: str` (required)
- `planned_at: str | null` (optional date)
- `fact_at: str | null` (optional date)
- `status: str` (required)
- `raw_text: str` (required)
- `inference_rule: str` (required if inferred)
- `confidence: float` (required if inferred)

## Read Models

## view_by_designer
- Aggregation for reminder/UI cards by designer.
- Contains ordered nearest tasks and next stages.

### Example
```json
{
  "artifact": "view_by_designer",
  "generated_at_utc": "2026-03-02T20:00:00Z",
  "items": [
    {
      "designer_id": "designer_irina",
      "designer_name": "Ирина",
      "tasks": [
        {
          "task_id": "1AbCd:ТАБЛИЧКА:row-248",
          "title": "Промо ролик / проект А",
          "next_stage_type": "draft",
          "next_due_at": "2026-03-05"
        }
      ]
    }
  ]
}
```

## view_by_tasks
- Flat list optimized for dashboard rendering and API.

### Example
```json
{
  "artifact": "view_by_tasks",
  "generated_at_utc": "2026-03-02T20:00:00Z",
  "tasks": [
    {
      "task_id": "1AbCd:ТАБЛИЧКА:row-248",
      "title": "Промо ролик / проект А",
      "designer_name": "Ирина",
      "status": "work",
      "next_due_at": "2026-03-05"
    }
  ]
}
```

## Normalization Rules (Critical)
1. `dd.mm` without year:
   - infer year by anchor date (run date and previous parsed date),
   - record `inference_rule=dd.mm->year_by_anchor`,
   - record `confidence` (high when monotonic, medium when boundary crossing).
2. Stages in one cell:
   - split by `;`, newlines, and bullet-like delimiters,
   - preserve `raw_text` for each stage line,
   - parse stage type and date independently.
3. Unknown/invalid pieces:
   - keep in `raw_fields`,
   - do not drop records silently,
   - emit parse issues to quality report.

## Hash Gate Contract
- `source_hash` is computed only from source range fields (`raw_hash_basis`).
- Target sheet render updates are not part of hash basis.
- Initial hash-basis field set for migration (`M3`):
  - `id`
  - `brand`
  - `format_`
  - `project_name`
  - `customer`
  - `designer`
  - `raw_timing`
  - `status`
- State object:
```json
{
  "source_id": "google-sheet:<file-id>:<sheet>",
  "source_hash": "sha256:...",
  "updated_at_utc": "2026-03-02T20:00:00Z"
}
```
