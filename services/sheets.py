import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict, Optional
from config import (
    SPREADSHEET_ID,
    CREDENTIALS_FILE,
    SHEET_NAME_EVENTS,
    SHEET_NAME_ACCELERATOR,
)

# Заголовки для листа «Мероприятия»
HEADERS_EVENTS = [
    "ID пользователя",
    "ФИО",
    "Вы из ВШЭ",
    "Образовательная программа",
    "Тг-аккаунт",
    "Вопрос спикерам",
    "Дата регистрации",
]

# Заголовки для листа «Акселератор»
HEADERS_ACCELERATOR = [
    "ID пользователя",
    "ФИО",
    "Название проекта",
    "Email",
    "Тг-аккаунт",
    "Направление (трек)",
    "Этап реализации",
    "Описание проекта",
    "PizzaPitch/Прожарка",
    "Ссылка на презентацию",
    "ФИО и роль команды",
    "Вы из НИУ ВШЭ",
    "Дата регистрации",
]


class GoogleSheetsService:
    def __init__(self):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE, scope
        )
        self.client = gspread.authorize(credentials)
        self._spreadsheet = self.client.open_by_key(SPREADSHEET_ID)

    def _get_sheet(self, name: str):
        return self._spreadsheet.worksheet(name)

    def _ensure_headers(self, sheet, headers: List[str]) -> None:
        if not sheet.get_all_values():
            sheet.append_row(headers)

    def save_registration(self, event_type: str, user_data: Dict) -> bool:
        """
        Сохраняет регистрацию в лист по типу события.
        event_type: "accelerator" | "events"
        """
        try:
            if event_type == "events":
                sheet = self._get_sheet(SHEET_NAME_EVENTS)
                self._ensure_headers(sheet, HEADERS_EVENTS)
                row = [
                    user_data["user_id"],
                    user_data["full_name"],
                    user_data.get("hse", ""),
                    user_data.get("edu_program", ""),
                    user_data.get("contact", ""),
                    user_data.get("question", ""),
                    user_data["registration_date"],
                ]
            else:
                sheet = self._get_sheet(SHEET_NAME_ACCELERATOR)
                self._ensure_headers(sheet, HEADERS_ACCELERATOR)
                row = [
                    user_data["user_id"],
                    user_data["full_name"],
                    user_data.get("project_name", ""),
                    user_data.get("email", ""),
                    user_data.get("contact", ""),
                    user_data.get("track", ""),
                    user_data.get("stage", ""),
                    user_data.get("description", ""),
                    user_data.get("pizzapitch", ""),
                    user_data.get("presentation_url", ""),
                    user_data.get("team", ""),
                    user_data.get("hse", ""),
                    user_data["registration_date"],
                ]
            sheet.append_row(row)
            return True
        except Exception as e:
            print(f"Error saving to Google Sheets: {e}")
            return False

    def get_user_ids(self, audience: str) -> List[int]:
        """
        Возвращает список Telegram user_id для рассылки.
        audience: "all" | "accelerator" | "events"
        """
        user_ids: List[int] = []
        try:
            if audience in ("all", "events"):
                sheet = self._get_sheet(SHEET_NAME_EVENTS)
                rows = sheet.get_all_records()
                for row in rows:
                    uid = row.get("ID пользователя")
                    if uid is not None and str(uid).strip():
                        try:
                            user_ids.append(int(uid))
                        except (ValueError, TypeError):
                            pass
            if audience in ("all", "accelerator"):
                sheet = self._get_sheet(SHEET_NAME_ACCELERATOR)
                rows = sheet.get_all_records()
                for row in rows:
                    uid = row.get("ID пользователя")
                    if uid is not None and str(uid).strip():
                        try:
                            user_ids.append(int(uid))
                        except (ValueError, TypeError):
                            pass
            if audience == "all":
                user_ids = list(dict.fromkeys(user_ids))
        except Exception as e:
            print(f"Error getting user ids from Google Sheets: {e}")
        return user_ids
