import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime

# ----------------------------
# TEST SHEET CONFIG
# ----------------------------
TEST_SHEET_ID = "1hKMwlnN3GAE4dxVGvq2WHT2-Om9SJ3P91L8cxioAeoo"
TEST_TAB_NAME = "Sheet1"
SERVICE_ACCOUNT_FILE = "service_account (1).json"


def get_sheet_service():
    """Authenticate using service account and return sheets service."""
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    service = build("sheets", "v4", credentials=creds)
    return service.spreadsheets()


def write_email_to_sheet_test_mode(emails):
    """
    Writes emails to TEST GOOGLE SHEET.
    Each email becomes one row.
    """
    sheet = get_sheet_service()

    rows = []
    for email in emails:
        rows.append([
            "",                     # SR.NO (blank)
            "",                     # SALES PERSON
            email.get("from", ""),  # CUSTOMER NAME
            "",                     # LOCATION
            "",                     # RFQ NO
            "",                     # RFQ DATE
            "",                     # PRODUCT
            "",                     # UID NO
            "",                     # UID DATE
            "",                     # DUE DATE
            "",                     # VENDOR
            "",                     # CONCERN PERSON
            "",                     # INQUIRY SENT ON
            "",                     # VENDOR STATUS
            "",                     # VENDOR QUOTATION NO
            "",                     # VENDOR QUOTATION DATE
            "",                     # CONCERN PERSON
            "",                     # VEPL OFFER NO
            "",                     # VEPL OFFER DATE
            "",                     # VEPL OFFER VALUE
            "EMAIL RECEIVED",       # CURRENT STATUS
            "Pending",              # FINAL STATUS
            "",                     # POST OFFER QUERY
            "",                     # POST QUERY DATE
            "Imported from email",  # REMARKS
            "",                     # FOLLOWUP PERSON
            "",                     # FOLLOWUP DATE
            email.get("from", ""),  # FOLLOWUP EMAIL
            "",                     # FOLLOWUP CALL
            "",                     # REMARKS (2nd)
            "",                     # Vendor Follow-up Aging
            "",                     # Aging
            "EMAIL",                # SYSTEM CATEGORY
            email.get("date", ""),  # LAST EMAIL DATE
            email.get("subject", "")# SYSTEM NOTES
        ])

    sheet.values().append(
        spreadsheetId=TEST_SHEET_ID,
        range=f"{TEST_TAB_NAME}!A2",
        valueInputOption="RAW",
        body={"values": rows}
    ).execute()

    return True
