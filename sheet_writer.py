import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime

# -------------------------------------------------------
# CONFIG — TEST MODE ONLY (SAFE)
# -------------------------------------------------------
TEST_SHEET_ID = "1hKMwlnN3GAE4dxVGvq2WHT2-Om9SJ3P91L8cxioAeoo"
TEST_TAB_NAME = "Sheet1"

# Name of your uploaded service account file
SERVICE_ACCOUNT_FILE = "service_account (1).json"


def get_sheet_service():
    """Authenticate and return Google Sheets service."""
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=creds)


def append_email_row(email_sender, email_subject, email_date):
    """Appends one new RFQ row into TEST Google Sheet.
       Real sheet remains untouched.
    """

    service = get_sheet_service()

    # Convert email date safely
    try:
        parsed_date = datetime.strptime(email_date[:25], "%a, %d %b %Y %H:%M:%S")
        formatted_date = parsed_date.strftime("%d-%m-%Y")
    except:
        formatted_date = email_date

    # -------------------------------------------------------
    # FINAL COLUMN MAPPING — TEST MODE
    # -------------------------------------------------------
    new_row = [
        "",  # SR.NO
        "",  # SALES PERSON
        "",  # CUSTOMER NAME
        "",  # LOCATION
        "",  # RFQ NO
        "",  # RFQ DATE (manual later)
        "",  # PRODUCT
        "",  # UID NO
        "",  # UID DATE
        "",  # DUE DATE
        "",  # VENDOR
        "",  # CONCERN PERSON
        "",  # INQUIRY SENT ON
        "",  # VENDOR STATUS
        "",  # VENDOR QUOTATION NO
        "",  # VENDOR QUOTATION DATE
        "",  # CONCERN PERSON
        "",  # VEPL OFFER NO
        "",  # VEPL OFFER DATE
        "",  # VEPL OFFER VALUE

        "EMAIL RECEIVED",  # CURRENT STATUS
        "Pending",         # FINAL STATUS

        "",  # POST OFFER QUERY
        "",  # POST QUERY DATE

        "Imported from email",  # REMARKS

        "",  # FOLLOWUP PERSON
        "",  # FOLLOWUP DATE

        email_sender,  # FOLLOWUP EMAIL
        "",            # FOLLOWUP CALL
        "",            # REMARKS (2nd)
        "",            # Vendor Follow-up Aging
        "",            # Aging
        "EMAIL",       # SYSTEM CATEGORY

        formatted_date,  # LAST EMAIL DATE
        email_subject    # SYSTEM NOTES
    ]

    # Write row into Test sheet
    request = service.spreadsheets().values().append(
        spreadsheetId=TEST_SHEET_ID,
        range=f"{TEST_TAB_NAME}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [new_row]}
    )

    return request.execute()
