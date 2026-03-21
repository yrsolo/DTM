"""Google Sheets service wrapper for read/write operations and render requests."""

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

from src.config.loader import load_config


_CFG = load_config()
_SHEET_NAMES = dict(_CFG.tables.sheet_names)


def _color_to_str(color: Mapping[str, float]) -> str:
    return "#{:02X}{:02X}{:02X}".format(
        int(color["red"] * 255),
        int(color["green"] * 255),
        int(color["blue"] * 255),
    )


def _color_to_rgb(
    color: Mapping[str, float] | str | tuple[float, float, float] | list[float],
) -> dict[str, float]:
    if isinstance(color, dict):
        rgb = color
    elif isinstance(color, str):
        color = color.lstrip("#")
        hlen = len(color)
        rgb = {
            "red": int(color[0 : hlen // 3], 16) / 255,
            "green": int(color[hlen // 3 : 2 * hlen // 3], 16) / 255,
            "blue": int(color[2 * hlen // 3 : hlen], 16) / 255,
        }
    elif isinstance(color, (list, tuple)):
        rgb = {"red": color[0], "green": color[1], "blue": color[2]}
    else:
        rgb = _color_to_rgb(str(color))
    return rgb


def _cell_to_indices(cell: str) -> tuple[int, int]:
    col = 0
    row = 0
    for item in cell:
        if item.isalpha():
            col = col * 26 + ord(item.upper()) - 64
        else:
            row = row * 10 + int(item)
    return col - 1, row - 1


def _parse_range(range_: str) -> tuple[int, int, int, int]:
    start, end = range_.split(":")
    start_col, start_row = _cell_to_indices(start)
    end_col, end_row = _cell_to_indices(end)
    return start_col, start_row, end_col, end_row


def dataframe_from_worksheet_values(
    worksheet_values: list[list[str]],
    *,
    header: bool = True,
) -> pd.DataFrame:
    """Build DataFrame from raw worksheet values with tolerant row/header normalization."""
    if not worksheet_values:
        return pd.DataFrame()

    if not header:
        return pd.DataFrame(worksheet_values)

    raw_columns = list(worksheet_values[0] or [])
    data_rows = [list(row or []) for row in worksheet_values[1:]]
    if not data_rows:
        return pd.DataFrame(columns=raw_columns)

    target_width = max(len(raw_columns), max((len(row) for row in data_rows), default=0))

    normalized_columns = list(raw_columns)
    if len(normalized_columns) < target_width:
        for idx in range(len(normalized_columns), target_width):
            normalized_columns.append(f"__extra_col_{idx + 1}")
    else:
        normalized_columns = normalized_columns[:target_width]

    normalized_rows: list[list[str]] = []
    for row in data_rows:
        if len(row) < target_width:
            row = row + [""] * (target_width - len(row))
        elif len(row) > target_width:
            row = row[:target_width]
        normalized_rows.append(row)

    return pd.DataFrame(normalized_rows, columns=normalized_columns)


class GoogleSheetInfo:
    """Information about Google Spreadsheet."""

    def __init__(self, spreadsheet_name: str, sheet_names: dict[str, str]):
        self.spreadsheet_name = spreadsheet_name
        self.sheets = sheet_names

    def get_sheet_name(self, key: str) -> str | None:
        return self.sheets.get(key)


class GoogleSheetsService:
    """Service for working with Google Sheets."""

    def __init__(self, credentials_path: str, dry_run: bool = False) -> None:
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Google Sheets support requires google-api-python-client and "
                "google-auth to be installed."
            ) from exc

        credentials = Credentials.from_service_account_file(credentials_path)
        self.sheets_service = build("sheets", "v4", credentials=credentials)
        self.drive_service = build("drive", "v3", credentials=credentials)
        self.requests = []
        self.dry_run = dry_run
        self._dry_run_counters = {}
        self.sheet_id_cache = {}
        self.get_spreadsheet_id_cache = {}
        self.spreadsheet_name = None
        self.worksheet_name = None

    def _dry_run_log(self, action: str, details: str = "") -> None:
        if self.dry_run:
            count = self._dry_run_counters.get(action, 0) + 1
            self._dry_run_counters[action] = count
            if action in {"update_cell", "update_borders"} and count > 5 and count % 500 != 0:
                return
            safe_details = details.encode("ascii", "backslashreplace").decode("ascii")
            count_info = f" count={count}"
            suffix = f"{count_info} | {safe_details}" if safe_details else count_info
            print(f"[DRY-RUN] GoogleSheetsService::{action}{suffix}")

    def set_spreadsheet_and_worksheet(self, spreadsheet_name: str, worksheet_name: str) -> None:
        self.spreadsheet_name = spreadsheet_name
        self.worksheet_name = worksheet_name

    def get_spreadsheet_id_by_name(self, spreadsheet_name: str) -> str:
        if spreadsheet_name in self.get_spreadsheet_id_cache:
            return self.get_spreadsheet_id_cache[spreadsheet_name]
        results = (
            self.drive_service.files()
            .list(q=f"name='{spreadsheet_name}'", fields="files(id, name)")
            .execute()
        )
        files = results.get("files", [])

        if not files:
            raise ValueError(f"Spreadsheet '{spreadsheet_name}' not found.")

        spreadsheet_id = files[0]["id"]
        self.get_spreadsheet_id_cache[spreadsheet_name] = spreadsheet_id

        return spreadsheet_id

    def get_sheet_id_by_name(self, spreadsheet_name: str, worksheet_name: str) -> int | None:
        cache_key = f"{spreadsheet_name}_{worksheet_name}"
        if cache_key in self.sheet_id_cache:
            return self.sheet_id_cache[cache_key]
        spreadsheet_id = self.get_spreadsheet_id_by_name(spreadsheet_name)
        result = self.sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        for sheet in result["sheets"]:
            if sheet["properties"]["title"] == worksheet_name:
                sheet_id = sheet["properties"]["sheetId"]
                self.sheet_id_cache[cache_key] = sheet_id
                return sheet_id
        return None

    def get_worksheet_values(
        self,
        spreadsheet_name: str,
        worksheet_name: str,
        worksheet_range: str = "A1:Z1000",
    ) -> list[list[str]]:
        spreadsheet_id = self.get_spreadsheet_id_by_name(spreadsheet_name)
        result = (
            self.sheets_service.spreadsheets()
            .values()
            .get(
                spreadsheetId=spreadsheet_id,
                range=f"{worksheet_name}!{worksheet_range}",
            )
            .execute()
        )
        return result.get("values", [])

    def get_dataframe(
        self,
        spreadsheet_name: str,
        worksheet_name: str,
        worksheet_range: str = "A1:Z1000",
        header: bool = True,
    ) -> pd.DataFrame:
        spreadsheet_id = self.get_spreadsheet_id_by_name(spreadsheet_name)
        result = (
            self.sheets_service.spreadsheets()
            .values()
            .get(
                spreadsheetId=spreadsheet_id,
                range=f"{worksheet_name}!{worksheet_range}",
            )
            .execute()
        )
        worksheet_values = result.get("values", [])
        return dataframe_from_worksheet_values(worksheet_values, header=header)

    def get_cell_colors(
        self,
        spreadsheet_name: str,
        worksheet_name: str,
        worksheet_range: str = "A1:Z1000",
    ) -> list[str]:
        spreadsheet_id = self.get_spreadsheet_id_by_name(spreadsheet_name)

        result = (
            self.sheets_service.spreadsheets()
            .get(
                spreadsheetId=spreadsheet_id,
                fields="sheets(data.rowData.values.userEnteredFormat.backgroundColor,properties.title)",
            )
            .execute()
        )

        sheet = next(
            item for item in result["sheets"] if item["properties"]["title"] == worksheet_name
        )
        rows = sheet["data"][0].get("rowData", [])

        start_col, start_row, end_col, end_row = _parse_range(worksheet_range)

        colors = []
        for r, row in enumerate(rows[start_row : end_row + 1]):
            try:
                for c, cell in enumerate(row["values"][start_col : end_col + 1]):
                    color = cell["userEnteredFormat"]["backgroundColor"]
                    colors.append(_color_to_str(color))
            except KeyError as ex:
                colors.extend(
                    [_color_to_str({"red": 1, "green": 1, "blue": 1})] * (end_col + 1 - start_col)
                )
                err = f"KeyError in |get_cell_colors|. {r, row} range: {worksheet_range} \n {ex} \n"
                print(err)

        return colors

    def update_borders(
        self,
        spreadsheet_name: str | None = None,
        sheet_name: str | None = None,
        row: int | None = None,
        col: int | None = None,
        border_data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        if self.dry_run:
            self._dry_run_log("update_borders", f"sheet={sheet_name or self.worksheet_name}")
            return
        if spreadsheet_name is None:
            spreadsheet_name = self.spreadsheet_name
        if sheet_name is None:
            sheet_name = self.worksheet_name

        if sheet_name == _SHEET_NAMES["tasks"]:
            return

        sheet_id = self.get_sheet_id_by_name(spreadsheet_name, sheet_name)

        _ = row, col
        if border_data:
            kwargs.update(border_data)
        start_col, start_row, end_col, end_row = _parse_range(kwargs["worksheet_range"])

        request = [
            spreadsheet_name,
            {
                "updateBorders": {
                    kwargs["side"]: {
                        "style": "SOLID_THICK",
                        "width": kwargs["width"],
                        "color": _color_to_rgb(kwargs["color"]),
                    },
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": start_row,
                        "endRowIndex": end_row,
                        "startColumnIndex": start_col,
                        "endColumnIndex": end_col,
                    },
                },
            },
        ]
        self.requests.append(request)

    def update_cell(
        self,
        spreadsheet_name: str | None = None,
        sheet_name: str | None = None,
        row: int | None = None,
        col: int | None = None,
        cell_data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        if self.dry_run:
            self._dry_run_log("update_cell", f"sheet={sheet_name or self.worksheet_name}")
            return
        if spreadsheet_name is None:
            spreadsheet_name = self.spreadsheet_name
        if sheet_name is None:
            sheet_name = self.worksheet_name

        if sheet_name == _SHEET_NAMES["tasks"]:
            return
        if cell_data:
            kwargs.update(cell_data)

        fields: list[str] = []
        payload = {
            "userEnteredValue": {},
            "userEnteredFormat": {},
        }

        if "col" in kwargs:
            col = kwargs["col"]

        if "row" in kwargs:
            row = kwargs["row"]

        if "value" in kwargs:
            value = kwargs["value"]
            if pd.isna(value):
                value = ""
            payload["userEnteredValue"]["stringValue"] = value
            fields.append("userEnteredValue")

        if "note" in kwargs:
            value = kwargs["note"]
            if pd.isna(value):
                value = ""
            payload["note"] = value
            fields.append("note")

        if "color" in kwargs:
            rgb = _color_to_rgb(kwargs["color"])
            if isinstance(rgb, dict):
                payload["userEnteredFormat"]["backgroundColor"] = rgb
                fields.append("userEnteredFormat.backgroundColor")

        if "text_color" in kwargs:
            rgb = _color_to_rgb(kwargs["text_color"])
            if isinstance(rgb, dict):
                payload["userEnteredFormat"].setdefault("textFormat", {})
                payload["userEnteredFormat"]["textFormat"]["foregroundColor"] = rgb
                fields.append("userEnteredFormat.textFormat.foregroundColor")

        if "font_size" in kwargs:
            size = kwargs["font_size"]
            payload["userEnteredFormat"].setdefault("textFormat", {})
            payload["userEnteredFormat"]["textFormat"]["fontSize"] = int(size)
            fields.append("userEnteredFormat.textFormat.fontSize")

        if "bold" in kwargs:
            bold_val = kwargs["bold"]
            payload["userEnteredFormat"].setdefault("textFormat", {})
            payload["userEnteredFormat"]["textFormat"]["bold"] = bool(bold_val)
            fields.append("userEnteredFormat.textFormat.bold")

        if "italic" in kwargs:
            italic_val = kwargs["italic"]
            payload["userEnteredFormat"].setdefault("textFormat", {})
            payload["userEnteredFormat"]["textFormat"]["italic"] = bool(italic_val)
            fields.append("userEnteredFormat.textFormat.italic")

        fields.append("userEnteredFormat.textFormat.foregroundColor")

        sheet_id = self.get_sheet_id_by_name(spreadsheet_name, sheet_name)

        request = [
            spreadsheet_name,
            {
                "updateCells": {
                    "rows": {"values": [payload]},
                    "fields": ",".join(fields),
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": row - 1,
                        "endRowIndex": row,
                        "startColumnIndex": col - 1,
                        "endColumnIndex": col,
                    },
                }
            },
        ]
        self.requests.append(request)

    def execute_updates(
        self,
        spreadsheet_name: str | None = None,
        requests: list[dict[str, Any]] | None = None,
    ) -> None:
        if spreadsheet_name is None:
            spreadsheet_name = self.spreadsheet_name

        if requests is None:
            req_list = [req[1] for req in self.requests if req[0] == spreadsheet_name]
        else:
            req_list = requests

        if self.dry_run:
            self._dry_run_log(
                "execute_updates",
                f"spreadsheet={spreadsheet_name} requests={len(req_list)}",
            )
            if requests is None:
                self.requests = [req for req in self.requests if req[0] != spreadsheet_name]
            return

        spreadsheet_id = self.get_spreadsheet_id_by_name(spreadsheet_name)

        try:
            batch_update_request = self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body={"requests": req_list}
            )
            batch_update_request.execute()
            if requests is None:
                self.requests = [req for req in self.requests if req[0] != spreadsheet_name]
        except Exception as e:
            print(f"Error executing batch update: {e}")

    def clear_requests(self) -> None:
        self.requests = []

    def clear_cells(
        self,
        spreadsheet_name: str | None = None,
        sheet_name: str | None = None,
        range_: str = "A1:ZZ1000",
    ) -> None:
        if spreadsheet_name is None:
            spreadsheet_name = self.spreadsheet_name
        if sheet_name is None:
            sheet_name = self.worksheet_name

        if self.dry_run:
            self._dry_run_log("clear_cells", f"sheet={sheet_name} range={range_}")
            return

        if sheet_name == _SHEET_NAMES["tasks"]:
            return

        sheet_id = self.get_sheet_id_by_name(spreadsheet_name, sheet_name)

        start_col, start_row, end_col, end_row = _parse_range(range_)

        request = {
            "updateCells": {
                "fields": "userEnteredValue,note,userEnteredFormat",
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": start_row,
                    "endRowIndex": end_row + 1,
                    "startColumnIndex": start_col,
                    "endColumnIndex": end_col + 1,
                },
            }
        }

        self.execute_updates(spreadsheet_name, [request])
