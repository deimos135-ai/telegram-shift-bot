from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import gspread
from google.oauth2.service_account import Credentials

from app.config import GOOGLE_SHEET_ID, TIMEZONE

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# оператори КЦ
CALL_CENTER_OPERATORS = {
    "Козуб Юлія",
    "Писанка Руслана",
    "Тищенко Яна",
    "Бессмертна Евеліна",
}

# адміністратори
ADMIN_NAMES = {
    "Попович Андрій",
    "Семеніг Вадим",
}

MONTH_NAMES_UA = {
    1: "Січень",
    2: "Лютий",
    3: "Березень",
    4: "Квітень",
    5: "Травень",
    6: "Червень",
    7: "Липень",
    8: "Серпень",
    9: "Вересень",
    10: "Жовтень",
    11: "Листопад",
    12: "Грудень",
}


def _get_credentials() -> Credentials:
    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

    if credentials_json:
        info = json.loads(credentials_json.strip())
        return Credentials.from_service_account_info(info, scopes=SCOPES)

    credentials_path = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    return Credentials.from_service_account_file(credentials_path, scopes=SCOPES)


def _get_client() -> gspread.Client:
    creds = _get_credentials()
    return gspread.authorize(creds)


def _get_worksheet_for_date(target_date: datetime):
    client = _get_client()
    spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)

    worksheet_name = f"{MONTH_NAMES_UA[target_date.month]} {target_date.year}"
    return spreadsheet.worksheet(worksheet_name)


def _find_day_column(header_row: list[str], target_date: datetime) -> int | None:
    variants = {
        str(target_date.day),
        f"{target_date.day:02d}",
        target_date.strftime("%d.%m"),
    }

    variants = {v.strip() for v in variants}

    for index, cell in enumerate(header_row):
        if str(cell).strip() in variants:
            return index

    return None


def get_schedule_for_date(target_date: datetime | None = None) -> dict | None:
    tz = ZoneInfo(TIMEZONE)
    now = target_date or datetime.now(tz)

    worksheet = _get_worksheet_for_date(now)
    values = worksheet.get_all_values()

    if len(values) < 3:
        return None

    days_row = values[1]
    day_col = _find_day_column(days_row, now)

    if day_col is None:
        return None

    first_shift: list[str] = []
    second_shift: list[str] = []
    admins_working: list[str] = []
    duty_admin: str | None = None

    for row in values[2:]:
        if not row:
            continue

        name = row[0].strip() if len(row) > 0 else ""
        mark = row[day_col].strip() if len(row) > day_col else ""

        if not name:
            continue

        # адміністратори
        if name in ADMIN_NAMES:
            if mark in {"8", "8/д", "8/Д"}:
                admins_working.append(name)

            if mark in {"8/д", "8/Д"}:
                duty_admin = name

            continue

        # оператори
        if name not in CALL_CENTER_OPERATORS:
            continue

        if mark == "1":
            first_shift.append(name)

        elif mark == "2":
            second_shift.append(name)

    return {
        "date": now.strftime("%d.%m.%Y"),
        "first_shift": first_shift,
        "second_shift": second_shift,
        "admins_working": admins_working,
        "duty_admin": duty_admin,
    }


def get_today_schedule():
    return get_schedule_for_date()


def get_tomorrow_schedule():
    tz = ZoneInfo(TIMEZONE)
    tomorrow = datetime.now(tz) + timedelta(days=1)
    return get_schedule_for_date(tomorrow)
