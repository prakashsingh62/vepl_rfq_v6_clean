from flask import Blueprint, jsonify
from email_reader import read_emails
from sheet_writer import write_email_to_sheet_test_mode

api_blueprint = Blueprint("api", __name__)

@api_blueprint.route("/process_emails", methods=["GET"])
def process_emails():
    try:
        # 1. Read emails
        email_data = read_emails()

        # If email_reader returned an error
        if "error" in email_data:
            return jsonify({"error": email_data["error"], "status": "failed"}), 500

        # 2. Write all emails to TEST SHEET
        write_email_to_sheet_test_mode(email_data.get("emails", []))

        return jsonify({
            "emails": email_data,
            "status": "Emails processed successfully"
        })

    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"}), 500
