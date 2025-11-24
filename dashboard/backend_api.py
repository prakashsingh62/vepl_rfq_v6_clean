# backend_api.py
from flask import Blueprint, jsonify
from email_reader import read_emails
from sheet_writer import write_email_to_sheet

api_blueprint = Blueprint("api_blueprint", __name__)

# --------------------------------------------------------
# Test API
# --------------------------------------------------------
@api_blueprint.route("/api/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"}), 200


# --------------------------------------------------------
# PROCESS EMAILS (READ + WRITE)
# --------------------------------------------------------
@api_blueprint.route("/api/process_emails", methods=["GET"])
def process_emails():
    try:
        emails = read_emails()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # if reader returns error
    if isinstance(emails, dict) and "error" in emails:
        return jsonify({"emails": emails, "status": "failed"}), 500

    # Save to Google Sheet (TEST MODE)
    try:
        for mail in emails:
            write_email_to_sheet(mail)
    except Exception as e:
        return jsonify({"error": f"Google Sheet write failed: {str(e)}"}), 500

    return jsonify({
        "emails": emails,
        "status": "Emails processed successfully"
    }), 200
