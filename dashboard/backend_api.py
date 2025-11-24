from flask import Blueprint, jsonify
from email_reader import read_emails
from email_parser import parse_email_list
from sheet_writer import write_parsed_rows_test_mode
import os

api_blueprint = Blueprint("api_blueprint", __name__)


@api_blueprint.route("/api/process_emails", methods=["GET"])
def process_emails():
    """
    Step-2 TEST MODE:
    1. Read emails
    2. Parse them
    3. Write parsed rows to TEST Google Sheet
    """
    try:
        # Get IMAP credentials from Render environment
        imap_user = os.getenv("IMAP_USER")
        imap_pass = os.getenv("IMAP_PASS")

        if not imap_user or not imap_pass:
            return jsonify({
                "status": "failed",
                "error": "IMAP credentials missing"
            })

        # 1. READ EMAILS (returns dictionary)
        email_data = read_emails(imap_user, imap_pass)

        if email_data.get("status") != "success":
            return jsonify({
                "status": "failed",
                "error": email_data.get("error", "Unknown IMAP error")
            })

        emails = email_data.get("emails", [])

        if not emails:
            return jsonify({
                "status": "success",
                "message": "No new emails found",
                "count": 0
            })

        # 2. PARSE EMAILS into sheet rows
        parsed_rows = parse_email_list(emails)

        # 3. WRITE ROWS to TEST SHEET
        write_result = write_parsed_rows_test_mode(parsed_rows)

        if write_result is not True:
            return jsonify({
                "status": "failed",
                "error": f"Sheet write error: {write_result}"
            })

        # SUCCESS
        return jsonify({
            "status": "success",
            "message": "Emails processed and written to test sheet",
            "emails_written": len(parsed_rows)
        })

    except Exception as e:
        return jsonify({
            "status": "failed",
            "error": str(e)
        })
