# backend_api.py
from flask import Blueprint, jsonify
from email_reader import read_emails
from sheet_writer import write_email_to_sheet_test_mode   # FIXED NAME

api_blueprint = Blueprint("api_blueprint", __name__)

@api_blueprint.route("/api/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"}), 200

@api_blueprint.route("/api/process_emails", methods=["GET"])
def process_emails():
    try:
        emails = read_emails()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if isinstance(emails, dict) and "error" in emails:
        return jsonify({"emails": emails, "status": "failed"}), 500

    try:
        for mail in emails:
            write_email_to_sheet_test_mode(mail)   # FIXED
    except Exception as e:
        return jsonify({"error": f"Google Sheet write failed: {str(e)}"}), 500

    return jsonify({
        "emails": emails,
        "status": "Emails processed successfully"
    }), 200
