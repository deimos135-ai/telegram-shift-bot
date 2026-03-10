from __future__ import annotations

import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import gspread
from google.oauth2.service_account import Credentials

TIMEZONE = os.getenv("TIMEZONE", "Europe/Kyiv")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "")
GOOGLE_WORKSHEET_NAME = os.getenv("GOOGLE_WORKSHEET_NAME", "")

ADMIN_NAMES = {"Попович", "Семеніг"}

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def _get_credentials() -> Credentials:
    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

    if credentials_json:
        info = json.loads(credentials_json)
        return Credentials.from_service_account_info(info, scopes=SCOPES)

    credentials_path = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    return Credentials.from_service_account_file(credentials_path, scopes=SCOPES)


def _get_client() -> gspread.Client:
    creds = _get_credentials()
    return gspread.authorize(creds)


def _get_worksheet():
    if not GOOGLE_SHEET_NAME:
        raise ValueError("GOOGLE_SHEET_NAME is not set")

    client = _get_client()
    spreadsheet = client.open(GOOGLE_SHEET_NAME)

    if GOOGLE_WORKSHEET_NAME:
        return spreadsheet.worksheet(GOOGLE_WORKSHEET_NAME)

    return spreadsheet.sheet1


def _find_day_column(header_row: list[str], day: int) -> int | None:
    target = str(day).strip()

    for index, cell in enumerate(header_row):
        if str(cell).strip() == target:
            return index

    return None


def get_schedule_for_date(target_date: datetime | None = None) -> dict | None:
    tz = ZoneInfo(TIMEZONE)
    now = target_date or datetime.now(tz)

    worksheet = _get_worksheet()
    values = worksheet.get_all_values()

    if len(values) < 3:
        return None

    # Очікуємо:
    # values[0] = дні тижня / верхній службовий рядок
    # values[1] = числа місяця
    # values[2:] = працівники
    days_row = values[1]
    day_col = _find_day_column(days_row, now.day)

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

        if name in ADMIN_NAMES:
            if mark in {"8", "8/д", "8/Д"}:
                admins_working.append(name)

            if mark in {"8/д", "8/Д"}:
                duty_admin = name

            continue

        if mark == "1":
            first_shift.append(name)
        elif mark == "2":
            second_shift.append(name)

    return {
        "date": now.strftime("%d.%m.%Y"),
        "day": now.day,
        "first_shift": first_shift,
        "second_shift": second_shift,
        "admins_working": admins_working,
        "duty_admin": duty_admin,
    }


def get_today_schedule() -> dict | None:
    return get_schedule_for_date()


def get_tomorrow_schedule() -> dict | None:
    tz = ZoneInfo(TIMEZONE)
    tomorrow = datetime.now(tz).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    from datetime import timedelta
    tomorrow = tomorrow + timedelta(days=1)
    return get_schedule_for_date(tomorrow)
