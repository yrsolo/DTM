"""
Module provides services for working with Google Sheets, including getting and updating sheet data.
"""

from typing import Optional, List
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pandas as pd

from config import SHEET_NAMES
from utils.func import color_to_str, color_to_rgb, parse_range


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
        self.sheets_service = build('sheets', 'v4', credentials=credentials)
        self.drive_service = build('drive', 'v3', credentials=credentials)
        self.requests = []
        self.sheet_id_cache = {}
        self.get_spreadsheet_id_cache = {}

    def get_spreadsheet_id_by_name(self, spreadsheet_name: str) -> str:
        """Get spreadsheet id by name.

        Args:
            spreadsheet_name (str): Spreadsheet name.

        Returns:
            str: Spreadsheet id.
        """
        if spreadsheet_name in self.get_spreadsheet_id_cache:
            return self.get_spreadsheet_id_cache[spreadsheet_name]
        results = self.drive_service.files().list(q=f"name='{spreadsheet_name}'", fields="files(id, name)").execute()
        files = results.get('files', [])

        if not files:
            raise ValueError(f"Spreadsheet '{spreadsheet_name}' not found.")

        spreadsheet_id = files[0]['id']
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
        print(f"Getting sheet id for {spreadsheet_name} {worksheet_name}")
        spreadsheet_id = self.get_spreadsheet_id_by_name(spreadsheet_name)
        result = self.sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        for sheet in result['sheets']:
            if sheet["properties"]["title"] == worksheet_name:
                sheet_id = sheet["properties"]["sheetId"]
                self.sheet_id_cache[cache_key] = sheet_id
                return sheet_id

    def get_worksheet_values(self, spreadsheet_name, worksheet_name, worksheet_range='A1:Z1000'):
        """Get worksheet values by name.

        Args:
            spreadsheet_name (str): Spreadsheet name.
            worksheet_name (str): Worksheet name.
            worksheet_range (str): sdfg.

        Returns:
            list: List of values.
        """
        spreadsheet_id = self.get_spreadsheet_id_by_name(spreadsheet_name)
        result = self.sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f'{worksheet_name}!{worksheet_range}',
        ).execute()
        return result.get('values', [])

    def get_dataframe(self, spreadsheet_name, worksheet_name, worksheet_range='A1:Z1000'):
        """Get DataFrame by spreadsheet name and worksheet name.

        Args:
            spreadsheet_name (str): Spreadsheet name.
            worksheet_name (str): Worksheet name.
            worksheet_range (str): Range of cells.

        Returns:
            pd.DataFrame: DataFrame with data from worksheet.
        """
        spreadsheet_id = self.get_spreadsheet_id_by_name(spreadsheet_name)
        result = self.sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f'{worksheet_name}!{worksheet_range}',
        ).execute()
        worksheet_values = result.get('values', [])
        df = pd.DataFrame(worksheet_values[1:], columns=worksheet_values[0]) # expected header in first row
        return df

    def get_cell_colors(self, spreadsheet_name, worksheet_name, worksheet_range='A1:Z1000'):
        """Get cell colors by spreadsheet name and worksheet name.

        Args:
            spreadsheet_name (str): Spreadsheet name.
            worksheet_name (str): Worksheet name.
            worksheet_range (str): Range of cells.

        Returns:
            list: List of colors.
        """
        spreadsheet_id = self.get_spreadsheet_id_by_name(spreadsheet_name)

        result = self.sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields='sheets(data.rowData.values.userEnteredFormat.backgroundColor,properties.title)',
        ).execute()

        sheet = next(item for item in result['sheets'] if item['properties']['title'] == worksheet_name)
        rows = sheet['data'][0].get('rowData', [])

        start_col, start_row, end_col, end_row = parse_range(worksheet_range)

        colors = []
        for r, row in enumerate(rows[start_row:end_row + 1]):
            for c, cell in enumerate(row['values'][start_col:end_col + 1]):
                color = cell['userEnteredFormat']['backgroundColor']
                colors.append(color_to_str(color))

        return colors

    def update_cell(self, spreadsheet_name: str, sheet_name: str, row: int, col: int, *args, **kwargs):
        """Add update cell request to batch.

        Args:
            spreadsheet_name (str): Spreadsheet name.
            sheet_name (str): Worksheet name.
            row (int): Row index.
            col (int): Column index.
            *args: Cell data.
            **kwargs: Cell data.
        """
        # disable clearing main table sheet
        if sheet_name == SHEET_NAMES['tasks']:
            return

        fields = []
        cell_data = {}

        if "value" in kwargs:
            value = kwargs["value"]
            if pd.isna(value):
                value = ""
            cell_data["userEnteredValue"] = {"stringValue": value}
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
                cell_data["userEnteredFormat"] = {"backgroundColor": rgb}
                fields.append("userEnteredFormat.backgroundColor")

        if "text_color" in kwargs:
            rgb = color_to_rgb(kwargs["text_color"])
            if isinstance(rgb, dict):
                cell_data["userEnteredFormat"] = {"textFormat": {"foregroundColor": rgb}}
                fields.append("userEnteredFormat.textFormat.foregroundColor")

        fields.append("userEnteredFormat.textFormat.foregroundColor")

        sheet_id = self.get_sheet_id_by_name(spreadsheet_name, sheet_name)

        request = [spreadsheet_name, {
            "updateCells": {
                "rows": {
                    "values": [cell_data]
                },
                "fields": ",".join(fields),
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": row - 1,
                    "endRowIndex": row,
                    "startColumnIndex": col - 1,
                    "endColumnIndex": col
                }
            }
        }]
        self.requests.append(request)

    def execute_updates(self, spreadsheet_name: str, requests: Optional[List] = None):
        """ Выполнить пакетное обновление """
        if requests is None:
            req_list = [req[1] for req in self.requests if req[0] == spreadsheet_name]
        else:
            req_list = requests

        spreadsheet_id = self.get_spreadsheet_id_by_name(spreadsheet_name)

        try:
            batch_update_request = self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": req_list}
            )
            batch_update_request.execute()
            if requests is None:
                self.requests = [req for req in self.requests if req[0] != spreadsheet_name]
        except Exception as e:
            print(f"Error executing batch update: {e}")

    def clear_requests(self):
        """ Очистить пакет обновлений """
        self.requests = []

    def clear_cells(self, spreadsheet_name, sheet_name, range_='A1:BB1000'):
        """Очистить заданный диапазон ячеек от значений и заметок."""
        # запрещаем очишать лист с главной таблицей
        if sheet_name == SHEET_NAMES['tasks']:
            return

        sheet_id = self.get_sheet_id_by_name(spreadsheet_name, sheet_name)

        # Переводим диапазон в индексы
        start_col, start_row, end_col, end_row = parse_range(range_)

        request = {
            "updateCells": {
                "fields": "userEnteredValue,note",
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": start_row,
                    "endRowIndex": end_row + 1,
                    "startColumnIndex": start_col,
                    "endColumnIndex": end_col + 1
                }
            }
        }

        self.execute_updates(spreadsheet_name, [request])
