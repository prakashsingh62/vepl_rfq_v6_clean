from flask import Blueprint, jsonify
from email_reader import read_emails
from sheet_writer import write_email_to_sheet_test_mode
import os

api_blueprint = Blueprint("api_blueprint", __name__)

@api_blueprint.route("/process_emails", methods=["GET"])
def process_emails():
    try:
        imap_user = os.getenv("IMAP_USER")
        imap_pass = os.getenv("IMAP_PASS")

        if not imap_user or not imap_pass:
            return jsonify({"status": "failed", "error": "IMAP credentials missing"})

        # 1. Read emails
        email_data = read_emails(imap_user, imap_pass)

        if email_data.get("status") != "success":
            return jsonify({"status": "failed", "error": email_data.get("error")})

        emails = email_data.get("emails", [])

        # 2. Write to TEST MODE sheet
        write_email_to_sheet_test_mode(emails)

        return jsonify({
            "status": "success",
            "written_rows": len(emails),
            "emails": emails
        })

    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)})
