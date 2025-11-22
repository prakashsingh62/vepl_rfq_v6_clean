from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import datetime

# --------------------------------------------------------------
# GOOGLE SHEETS CONFIG
# --------------------------------------------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "service_account.json"   # make sure this file exists

# Load credentials
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# --------------------------------------------------------------
# WRITE TO SHEET
# --------------------------------------------------------------
class SheetWriter:

    def __init__(self, sheet_id):
        self.sheet_id = sheet_id
        self.service = build("sheets", "v4", credentials=creds)
        self.sheet = self.service.spreadsheets()

        # Column index mapping (1-based indexing)
        self.COL_RFQ_NO = 5      # E
        self.COL_UID_NO = 8      # H
        self.COL_CUSTOMER = 3    # C
        self.COL_VENDOR = 11     # K
        self.COL_DUE_DATE = 10   # J
        self.COL_STATUS = 21     # U (CURRENT STATUS)
        self.COL_REMARKS = 26    # Z (first remarks)
        self.COL_SYS_CATEGORY = 34  # AH
        self.COL_SYS_LAST_EMAIL = 35  # AI
        self.COL_SYS_NOTES = 36  # AJ

    # ----------------------------------------------------------
    # READ ENTIRE SHEET INTO MEMORY
    # ----------------------------------------------------------
    def read_sheet(self, range_name="A1:AJ2000"):
        result = self.sheet.values().get(
            spreadsheetId=self.sheet_id,
            range=range_name
        ).execute()

        return result.get("values", [])

    # ----------------------------------------------------------
    # FIND ROW BY UID (primary), RFQ as secondary
    # ----------------------------------------------------------
    def find_row(self, data, uid, rfq_no):
        for index, row in enumerate(data):
            if len(row) >= self.COL_UID_NO:
                existing_uid = row[self.COL_UID_NO - 1].strip() if row[self.COL_UID_NO - 1] else ""
                existing_rfq = row[self.COL_RFQ_NO - 1].strip() if row[self.COL_RFQ_NO - 1] else ""

                # UID takes priority
                if uid and existing_uid == uid:
                    return index + 1

                # RFQ fallback
                if rfq_no and existing_rfq == rfq_no:
                    return index + 1

        return None

    # ----------------------------------------------------------
    # FORMAT SAFE STRING
    # ----------------------------------------------------------
    def safe(self, value):
        return value if value else ""

    # ----------------------------------------------------------
    # WRITE ONE PARSED EMAIL INTO SHEET
    # ----------------------------------------------------------
    def write_email(self, parsed):

        rfq_no = self.safe(parsed.get("rfq_no"))
        uid = self.safe(parsed.get("uid"))
        category = self.safe(parsed.get("type"))
        customer = self.safe(parsed.get("customer_name"))
        vendor = self.safe(parsed.get("vendor_name"))
        due_date = self.safe(parsed.get("due_date"))
        notes = self.safe(parsed.get("body_clean")[:200])   # short summary
        email_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        # Load sheet
        data = self.read_sheet()

        # Find row to update
        row_index = self.find_row(data, uid, rfq_no)

        # ------------------------------------------------------
        # IF ROW NOT FOUND → INSERT NEW ROW
        # ------------------------------------------------------
        if not row_index:
            row_data = [""] * 36  # A to AJ

            row_data[self.COL_RFQ_NO - 1] = rfq_no
            row_data[self.COL_UID_NO - 1] = uid
            row_data[self.COL_CUSTOMER - 1] = customer
            row_data[self.COL_VENDOR - 1] = vendor
            row_data[self.COL_DUE_DATE - 1] = due_date
            row_data[self.COL_STATUS - 1] = category
            row_data[self.COL_SYS_CATEGORY - 1] = category
            row_data[self.COL_SYS_LAST_EMAIL - 1] = email_date
            row_data[self.COL_SYS_NOTES - 1] = notes

            self.sheet.values().append(
                spreadsheetId=self.sheet_id,
                range="A1",
                valueInputOption="USER_ENTERED",
                body={"values": [row_data]},
            ).execute()

            return {"status": "inserted", "uid": uid, "rfq_no": rfq_no}

        # ------------------------------------------------------
        # IF ROW FOUND → UPDATE IT
        # ------------------------------------------------------
        update_range = f"A{row_index}:AJ{row_index}"

        row_data = [""] * 36
        row_data[self.COL_RFQ_NO - 1] = rfq_no
        row_data[self.COL_UID_NO - 1] = uid
        row_data[self.COL_CUSTOMER - 1] = customer
        row_data[self.COL_VENDOR - 1] = vendor
        row_data[self.COL_DUE_DATE - 1] = due_date
        row_data[self.COL_STATUS - 1] = category
        row_data[self.COL_SYS_CATEGORY - 1] = category
        row_data[self.COL_SYS_LAST_EMAIL - 1] = email_date
        row_data[self.COL_SYS_NOTES - 1] = notes

        self.sheet.values().update(
            spreadsheetId=self.sheet_id,
            range=update_range,
            valueInputOption="USER_ENTERED",
            body={"values": [row_data]},
        ).execute()

        return {"status": "updated", "uid": uid, "rfq_no": rfq_no}
