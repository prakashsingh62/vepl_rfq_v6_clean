import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ---------------------------------------------------------
# TEST SHEET CONFIG
# ---------------------------------------------------------
TEST_SHEET_ID = "1hKMwlnN3GAE4dxVGvq2WHT2-Om9SJ3P91L8cxioAeoo"
TEST_TAB_NAME = "Sheet1"
SERVICE_ACCOUNT_FILE = "service_account.json"


# ---------------------------------------------------------
# Google Sheets Service
# ---------------------------------------------------------
def get_sheet_service():
    """
    Returns authenticated Google Sheets API service.
    """
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=creds).spreadsheets()


# ---------------------------------------------------------
# OLD TEST MODE FUNCTION (KEEP AS IS)
# DO NOT DELETE — used earlier
# ---------------------------------------------------------
def write_email_to_sheet_test_mode(emails):
    """
    Writes RAW email dicts to test sheet.
    Format:
    [
        {"from": "", "subject": "", "date": "", "body": ""},
        ...
    ]
    """

    sheet = get_sheet_service()
    rows = []

    for email in emails:
        rows.append([
            email.get("date", ""),
            email.get("from", ""),
            email.get("subject", ""),
            "",
            "",
            "",
            "",
            "",
            email.get("body", "")[:200]
        ])

    sheet.values().append(
        spreadsheetId=TEST_SHEET_ID,
        range=f"{TEST_TAB_NAME}!A2",
        valueInputOption="RAW",
        body={"values": rows}
    ).execute()

    return True


# ---------------------------------------------------------
# NEW STEP-2 FUNCTION
# Writes PARSED rows from email_parser
# ---------------------------------------------------------
def write_parsed_rows_test_mode(rows):
    """
    Writes parsed RFQ rows into TEST sheet.
    Expected row format:
    [
        [date, from, subject, rfq_no, uid, category, priority, status, notes],
        ...
    ]
    """

    try:
        sheet = get_sheet_service()

        sheet.values().append(
            spreadsheetId=TEST_SHEET_ID,
            range=f"{TEST_TAB_NAME}!A2",
            valueInputOption="RAW",
            body={"values": rows}
        ).execute()

        return True

    except Exception as e:
        return str(e)

# ---------------------------------------------------------
# LEVEL-6 PRODUCTION RFQ WRITER
# ---------------------------------------------------------
PROD_SHEET_ID = "PUT-YOUR-PRODUCTION-SHEET-ID-HERE"
PROD_TAB_NAME = "Sheet1"      # or your real tab name


def write_rfq_rows(emails):
    """
    Writes structured RFQ emails into the production sheet.
    Each email dict must contain:
    date, from, subject, body, rfq_no, qty, part, description
    """

    try:
        sheet = get_sheet_service()
        rows = []

        for em in emails:

            rows.append([
                em.get("date", ""),
                em.get("from", ""),
                em.get("subject", ""),
                em.get("rfq_no", ""),
                em.get("qty", ""),
                em.get("part", ""),
                em.get("description", ""),
                em.get("body", ""),
                "IMAP"
            ])

        sheet.values().append(
            spreadsheetId=PROD_SHEET_ID,
            range=f"{PROD_TAB_NAME}!A2",
            valueInputOption="RAW",
            body={"values": rows}
        ).execute()

        return True

    except Exception as e:
        return {"status": "failed", "error": str(e)}
# ---------------------------------------------------------
# LEVEL-6 PRODUCTION RFQ WRITER (FINAL)
# ---------------------------------------------------------
PROD_SHEET_ID = "1hKMwlnN3GAE4dxVGvq2WHT2-Om9SJ3P91L8cxioAeoo"
PROD_TAB_NAME = "RFQ TEST SHEET"


def write_rfq_rows(emails):
    """
    Writes structured RFQ emails into the production sheet.
    Each email dict must contain:
    date, from, subject, body, rfq_no, qty, part, description
    """

    try:
        sheet = get_sheet_service()
        rows = []

        for em in emails:

            rows.append([
                em.get("date", ""),
                em.get("from", ""),
                em.get("subject", ""),
                em.get("rfq_no", ""),
                em.get("qty", ""),
                em.get("part", ""),
                em.get("description", ""),
                em.get("body", ""),
                "IMAP"
            ])

        sheet.values().append(
            spreadsheetId=PROD_SHEET_ID,
            range=f"{PROD_TAB_NAME}!A2",
            valueInputOption="RAW",
            body={"values": rows}
        ).execute()

        return True

    except Exception as e:
        return {"status": "failed", "error": str(e)}


