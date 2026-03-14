# API v2 parity for Snapshot Engine

This document defines the current API v2 query and payload expectations for the snapshot-engine read path.

## Query parity
- `statuses`: comma-separated list, default `work,pre_done`.
- `designer`: exact-name filter (case-insensitive behavior preserved).
- `limit`: max returned tasks (default `200`).
- `include_people`: include/exclude `entities.people` block.
- `window_start` + `window_end`: intersects-mode window filter.

## Field semantics
- `tasks[].status`: normalized status derived from sheet color/status normalization.
- `tasks[].history`: raw textual status/history from source sheet status text.
- `tasks[].date.start|end|nextDue`: normalized date fields from prep snapshot.

## Response parity
- Response blocks stay: `meta`, `filters`, `summary`, `entities`, `tasks`.
- `milestones` remain full for selected tasks; window affects task selection only.

## Source-of-truth
- Runtime API v2 source is `PrepSnapshot` from Snapshot Engine.
