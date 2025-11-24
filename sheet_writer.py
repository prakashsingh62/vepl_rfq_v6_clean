# ---------------------------------------------------------
# NEW FUNCTION FOR STEP-2 TEST MODE (PARSED ROWS)
# ---------------------------------------------------------
def write_parsed_rows_test_mode(rows):
    """
    Writes parsed email rows (Step-2) into the TEST Google Sheet.
    Expects rows in this format:
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
