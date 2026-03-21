"""
Module provides services for working with Google Sheets, including getting and updating sheet data.
"""

from typing import List, Optional

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from config import SHEET_NAMES
from core.reminder import TelegramNotifier
from utils.func import color_to_rgb, color_to_str, parse_range

t = TelegramNotifier()


class GoogleSheetInfo:
    """Information about Google Spreadsheet."""

    def __init__(self, spreadsheet_name: str, sheet_names: dict):
        """Information about Google Spreadsheet.

        Args:
            spreadsheet_name (str): Spreadsheet name.
            sheet_names (dict): Dictionary with sheet names.
        """
        self.spreadsheet_name = spreadsheet_name
        self.sheets = sheet_names

    def get_sheet_name(self, key: str) -> str:
        """Get sheet name by key.

        Args:
            key (str): Key for sheet name.

        Returns:
            str: Sheet name.
        """
        return self.sheets.get(key)


class GoogleSheetsService:
    """Service for working with Google Sheets."""

    def __init__(self, credentials_path: str):
        """Service for working with Google Sheets.

        Args:
            credentials_path (str): Path to credentials file.
        """
        credentials = Credentials.from_service_account_file(credentials_path)
        self.sheets_service = build("sheets", "v4", credentials=credentials)
        self.drive_service = build("drive", "v3", credentials=credentials)
        self.requests = []
        self.sheet_id_cache = {}
        self.get_spreadsheet_id_cache = {}
        self.spreadsheet_name = None
        self.worksheet_name = None

    def set_spreadsheet_and_worksheet(self, spreadsheet_name, worksheet_name):
        self.spreadsheet_name = spreadsheet_name
        self.worksheet_name = worksheet_name

    def get_spreadsheet_id_by_name(self, spreadsheet_name: str) -> str:
        """Get spreadsheet id by name.

        Args:
            spreadsheet_name (str): Spreadsheet name.

        Returns:
            str: Spreadsheet id.
        """
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

    def get_sheet_id_by_name(self, spreadsheet_name, worksheet_name):
        """Get sheet id by name.

        Args:
            spreadsheet_name (str): Spreadsheet name.
            worksheet_name (str): Worksheet name.

        Returns:
            str: Sheet id.
        """
        cache_key = f"{spreadsheet_name}_{worksheet_name}"
        if cache_key in self.sheet_id_cache:
            return self.sheet_id_cache[cache_key]
        # print(f"Getting sheet id for {spreadsheet_name} {worksheet_name}")
        spreadsheet_id = self.get_spreadsheet_id_by_name(spreadsheet_name)
        result = self.sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        for sheet in result["sheets"]:
            if sheet["properties"]["title"] == worksheet_name:
                sheet_id = sheet["properties"]["sheetId"]
                self.sheet_id_cache[cache_key] = sheet_id
                return sheet_id

    def get_worksheet_values(self, spreadsheet_name, worksheet_name, worksheet_range="A1:Z1000"):
        """Get worksheet values by name.

        Args:
            spreadsheet_name (str): Spreadsheet name.
            worksheet_name (str): Worksheet name.
            worksheet_range (str): sdfg.

        Returns:
            list: List of values.
        """
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
        self, spreadsheet_name, worksheet_name, worksheet_range="A1:Z1000", header=True
    ):
        """Get DataFrame by spreadsheet name and worksheet name.

        Args:
            spreadsheet_name (str): Spreadsheet name.
            worksheet_name (str): Worksheet name.
            worksheet_range (str): Range of cells.
            header (bool): Flag to use first row as header.

        Returns:
            pd.DataFrame: DataFrame with data from worksheet.
        """
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
        columns = worksheet_values[0] if header else None
        df = pd.DataFrame(worksheet_values[1:], columns=columns)  # expected header in first row
        return df

    def get_cell_colors(self, spreadsheet_name, worksheet_name, worksheet_range="A1:Z1000"):
        """Get cell colors by spreadsheet name and worksheet name.

        Args:
            spreadsheet_name (str): Spreadsheet name.
            worksheet_name (str): Worksheet name.
            worksheet_range (str): Range of cells.

        Returns:
            list: List of colors.
        """
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

        start_col, start_row, end_col, end_row = parse_range(worksheet_range)

        colors = []
        for r, row in enumerate(rows[start_row : end_row + 1]):
            try:
                for c, cell in enumerate(row["values"][start_col : end_col + 1]):
                    color = cell["userEnteredFormat"]["backgroundColor"]
                    colors.append(color_to_str(color))
            except KeyError as ex:
                colors.extend(
                    [color_to_str({"red": 1, "green": 1, "blue": 1})] * (end_col + 1 - start_col)
                )
                err = f"KeyError in |get_cell_colors|. {r, row} range: {worksheet_range} \n {ex} \n"
                print(err)
                # t.log(err)

        return colors

    def update_borders(
        self,
        spreadsheet_name: str = None,
        sheet_name: str = None,
        row: int = None,
        col: int = None,
        border_data: dict = None,
        **kwargs,
    ):
        """Add update cell request to batch.

        Args:
            spreadsheet_name (str): Spreadsheet name.
            sheet_name (str): Worksheet name.
            row (int): Row index.
            col (int): Column index.
            cell_data: Cell data.
            **kwargs: Cell data.
        """
        # disable clearing main table sheet
        if spreadsheet_name is None:
            spreadsheet_name = self.spreadsheet_name
        if sheet_name is None:
            sheet_name = self.worksheet_name

        if sheet_name == SHEET_NAMES["tasks"]:
            return

        sheet_id = self.get_sheet_id_by_name(spreadsheet_name, sheet_name)

        if border_data:
            kwargs.update(border_data)
        start_col, start_row, end_col, end_row = parse_range(kwargs["worksheet_range"])

        request = [
            spreadsheet_name,
            {
                "updateBorders": {
                    kwargs["side"]: {
                        "style": "SOLID_THICK",
                        "width": kwargs["width"],
                        "color": color_to_rgb(kwargs["color"]),
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
        spreadsheet_name: str = None,
        sheet_name: str = None,
        row: int = None,
        col: int = None,
        cell_data: dict = None,
        **kwargs,
    ):
        """Add update cell request to batch.

        Args:
            spreadsheet_name (str): Spreadsheet name.
            sheet_name (str): Worksheet name.
            row (int): Row index.
            col (int): Column index.
            cell_data: Cell data.
            **kwargs: Cell data.
        """
        # disable clearing main table sheet
        if spreadsheet_name is None:
            spreadsheet_name = self.spreadsheet_name
        if sheet_name is None:
            sheet_name = self.worksheet_name

        if sheet_name == SHEET_NAMES["tasks"]:
            return
        if cell_data:
            kwargs.update(cell_data)
            # kwargs = cell_data

        fields = []
        cell_data = {}
        cell_data = {
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
            cell_data["userEnteredValue"]["stringValue"] = value
            fields.append("userEnteredValue")

        if "note" in kwargs:
            value = kwargs["note"]
            if pd.isna(value):
                value = ""
            cell_data["note"] = value
            fields.append("note")

        if "color" in kwargs:
            rgb = color_to_rgb(kwargs["color"])
            if isinstance(rgb, dict):
                cell_data["userEnteredFormat"]["backgroundColor"] = rgb
                fields.append("userEnteredFormat.backgroundColor")

        if "text_color" in kwargs:
            rgb = color_to_rgb(kwargs["text_color"])
            if isinstance(rgb, dict):
                cell_data["userEnteredFormat"].setdefault("textFormat", {})
                cell_data["userEnteredFormat"]["textFormat"]["foregroundColor"] = rgb
                fields.append("userEnteredFormat.textFormat.foregroundColor")

        if "font_size" in kwargs:
            # fontSize должен быть числом
            size = kwargs["font_size"]
            cell_data["userEnteredFormat"].setdefault("textFormat", {})
            cell_data["userEnteredFormat"]["textFormat"]["fontSize"] = int(size)
            fields.append("userEnteredFormat.textFormat.fontSize")

        if "bold" in kwargs:
            # bold – это булево значение
            bold_val = kwargs["bold"]
            cell_data["userEnteredFormat"].setdefault("textFormat", {})
            cell_data["userEnteredFormat"]["textFormat"]["bold"] = bool(bold_val)
            fields.append("userEnteredFormat.textFormat.bold")

        if "italic" in kwargs:
            # italic – это булево значение
            italic_val = kwargs["italic"]
            cell_data["userEnteredFormat"].setdefault("textFormat", {})
            cell_data["userEnteredFormat"]["textFormat"]["italic"] = bool(italic_val)
            fields.append("userEnteredFormat.textFormat.italic")

        fields.append("userEnteredFormat.textFormat.foregroundColor")

        sheet_id = self.get_sheet_id_by_name(spreadsheet_name, sheet_name)

        request = [
            spreadsheet_name,
            {
                "updateCells": {
                    "rows": {"values": [cell_data]},
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

    def execute_updates(self, spreadsheet_name: str = None, requests: Optional[List] = None):
        """Выполнить пакетное обновление"""

        if spreadsheet_name is None:
            spreadsheet_name = self.spreadsheet_name

        if requests is None:
            req_list = [req[1] for req in self.requests if req[0] == spreadsheet_name]
        else:
            req_list = requests

        spreadsheet_id = self.get_spreadsheet_id_by_name(spreadsheet_name)

        try:
            # print(req_list)
            batch_update_request = self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body={"requests": req_list}
            )
            batch_update_request.execute()
            if requests is None:
                self.requests = [req for req in self.requests if req[0] != spreadsheet_name]
        except Exception as e:
            print(f"Error executing batch update: {e}")

    def clear_requests(self):
        """Очистить пакет обновлений"""
        self.requests = []

    def clear_cells(self, spreadsheet_name: str = None, sheet_name: str = None, range_="A1:ZZ1000"):
        """Очистить заданный диапазон ячеек от значений и заметок."""

        if spreadsheet_name is None:
            spreadsheet_name = self.spreadsheet_name
        if sheet_name is None:
            sheet_name = self.worksheet_name

        # запрещаем очишать лист с главной таблицей
        if sheet_name == SHEET_NAMES["tasks"]:
            return

        sheet_id = self.get_sheet_id_by_name(spreadsheet_name, sheet_name)

        # Переводим диапазон в индексы
        start_col, start_row, end_col, end_row = parse_range(range_)

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
