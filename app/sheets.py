from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import gspread
from google.oauth2.service_account import Credentials

from app.config import GOOGLE_SHEET_ID, GOOGLE_WORKSHEET_NAME, TIMEZONE

ADMIN_NAMES = {"Попович", "Семеніг"}
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def _get_credentials() -> Credentials:
    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

    if credentials_json:
        credentials_json = credentials_json.strip()
        info = json.loads(credentials_json)

        if not isinstance(info, dict):
            raise ValueError("GOOGLE_CREDENTIALS_JSON must be a JSON object")

        return Credentials.from_service_account_info(info, scopes=SCOPES)

    credentials_path = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    return Credentials.from_service_account_file(credentials_path, scopes=SCOPES)


def _get_client() -> gspread.Client:
    print("DEBUG: _get_client called")
    creds = _get_credentials()
    return gspread.authorize(creds)


def _get_worksheet():
    print("DEBUG: _get_worksheet called")
    print(f"DEBUG: GOOGLE_SHEET_ID={GOOGLE_SHEET_ID}")
    print(f"DEBUG: GOOGLE_WORKSHEET_NAME={GOOGLE_WORKSHEET_NAME}")

    if not GOOGLE_SHEET_ID:
        raise ValueError("GOOGLE_SHEET_ID is not set")

    client = _get_client()
    spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)

    print(f"DEBUG: spreadsheet opened, title={spreadsheet.title}")

    if GOOGLE_WORKSHEET_NAME:
        worksheet = spreadsheet.worksheet(GOOGLE_WORKSHEET_NAME)
        print(f"DEBUG: worksheet selected by name, title={worksheet.title}")
        return worksheet

    worksheet = spreadsheet.sheet1
    print(f"DEBUG: worksheet selected as sheet1, title={worksheet.title}")
    return worksheet


def _find_day_column(header_row: list[str], day: int) -> int | None:
    target = str(day).strip()
    print(f"DEBUG: searching day column for day={target}")
    print(f"DEBUG: header_row={header_row}")

    for index, cell in enumerate(header_row):
        if str(cell).strip() == target:
            print(f"DEBUG: found day column index={index}")
            return index

    print("DEBUG: day column not found")
    return None


def get_schedule_for_date(target_date: datetime | None = None) -> dict | None:
    print("DEBUG: get_schedule_for_date called")

    tz = ZoneInfo(TIMEZONE)
    now = target_date or datetime.now(tz)

    print(f"DEBUG: target date={now.strftime('%d.%m.%Y')} day={now.day}")

    worksheet = _get_worksheet()
    values = worksheet.get_all_values()

    print(f"DEBUG: rows count={len(values)}")

    if len(values) < 3:
        print("DEBUG: not enough rows in worksheet")
        return None

    for i, row in enumerate(values[:8]):
        print(f"DEBUG: row {i} = {row}")

    # зараз очікуємо, що рядок з числами днів - values[1]
    days_row = values[1]
    print(f"DEBUG: days_row={days_row}")

    day_col = _find_day_column(days_row, now.day)
    print(f"DEBUG: resulting day_col={day_col}")

    if day_col is None:
        print("DEBUG: could not find current day in days_row")
        return None

    first_shift: list[str] = []
    second_shift: list[str] = []
    admins_working: list[str] = []
    duty_admin: str | None = None

    for idx, row in enumerate(values[2:], start=2):
        if not row:
            print(f"DEBUG: row {idx} skipped because empty")
            continue

        name = row[0].strip() if len(row) > 0 else ""
        mark = row[day_col].strip() if len(row) > day_col else ""

        print(f"DEBUG: processing row {idx}: name='{name}', mark='{mark}'")

        if not name:
            print(f"DEBUG: row {idx} skipped because name empty")
            continue

        if name in ADMIN_NAMES:
            if mark in {"8", "8/д", "8/Д"}:
                admins_working.append(name)
                print(f"DEBUG: admin working added -> {name}")

            if mark in {"8/д", "8/Д"}:
                duty_admin = name
                print(f"DEBUG: duty admin set -> {name}")

            continue

        if mark == "1":
            first_shift.append(name)
            print(f"DEBUG: first shift added -> {name}")
        elif mark == "2":
            second_shift.append(name)
            print(f"DEBUG: second shift added -> {name}")

    result = {
        "date": now.strftime("%d.%m.%Y"),
        "day": now.day,
        "first_shift": first_shift,
        "second_shift": second_shift,
        "admins_working": admins_working,
        "duty_admin": duty_admin,
    }

    print(f"DEBUG: final result={result}")
    return result


def get_today_schedule() -> dict | None:
    print("DEBUG: get_today_schedule called")
    return get_schedule_for_date()


def get_tomorrow_schedule() -> dict | None:
    print("DEBUG: get_tomorrow_schedule called")
    tz = ZoneInfo(TIMEZONE)
    tomorrow = datetime.now(tz) + timedelta(days=1)
    return get_schedule_for_date(tomorrow)
