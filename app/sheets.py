import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from app.config import GOOGLE_SHEET_NAME

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

def get_client():

    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )

    return gspread.authorize(creds)


def get_today_shift():

    gc = get_client()

    sheet = gc.open(GOOGLE_SHEET_NAME).sheet1

    rows = sheet.get_all_records()

    today = datetime.now().strftime("%d.%m.%Y")

    for row in rows:
        if row["date"] == today:
            return row

    return None
