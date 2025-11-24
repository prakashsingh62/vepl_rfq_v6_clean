from flask import Blueprint, jsonify, request
import os
from email_reader import read_emails
from sheet_writer import write_email_to_sheet_test_mode

api_blueprint = Blueprint("api", __name__)

@api_blueprint.route("/process_emails", methods=["GET"])
def process_emails():

    try:
        # 1. Read IMAP credentials from environment
        imap_user = os.getenv("IMAP_USER")
        imap_pass = os.getenv("IMAP_PASS")

        if not imap_user or not imap_pass:
            return jsonify({
                "status": "failed",
                "error": "IMAP credentials missing"
            })

        # 2. Read emails (email_reader.py)
        email_data = read_emails(imap_user, imap_pass)

        if email_data.get("status") != "success":
            return jsonify({
                "status": "failed",
                "error": email_data.get("error")
            })

        emails = email_data.get("emails", [])

        # 3. Write to TEST sheet only
        write_email_to_sheet_test_mode(emails)

        return jsonify({
            "status": "success",
            "count": len(emails),
            "emails": emails
        })

    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)})
