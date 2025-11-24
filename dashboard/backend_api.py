from flask import request, jsonify
from email_reader import read_emails
from sheet_writer import append_email_row


# ---------------------------------------------------------
# EMAIL → TEST GOOGLE SHEET (STEP-2)
# ---------------------------------------------------------
@app.route("/api/process_emails", methods=["GET"])
def process_emails_api():
    """
    Step-2:
    Read emails → Append rows to TEST Google Sheet.
    REAL RFQ sheet stays untouched.
    """

    # 1. Read emails from Gmail
    emails = read_emails()

    if "emails" not in emails:
        return jsonify({
            "status": "fail",
            "error": "Email read failed",
            "details": emails
        })

    email_list = emails["emails"]
    written = 0

    # 2. Append each email → New row in TEST SHEET
    for e in email_list:
        sender = e.get("from", "")
        subject = e.get("subject", "")
        date = e.get("date", "")

        try:
            append_email_row(sender, subject, date)
            written += 1
        except Exception as ex:
            print("Write error:", ex)

    # 3. Response
    return jsonify({
        "status": "success",
        "emails_processed": len(email_list),
        "rows_written_to_test_sheet": written,
        "preview": email_list
    })
