from flask import Blueprint, jsonify
from email_reader import read_emails
from sheet_writer import write_email_to_sheet

api_blueprint = Blueprint("api_blueprint", __name__)

# ----------------------------------------------------------
# API: Process Emails + Write to Test Google Sheet
# ----------------------------------------------------------
@api_blueprint.route("/api/process_emails", methods=["GET"])
def process_emails_api():
    try:
        emails_data = read_emails()

        if "error" in emails_data:
            return jsonify({"status": "failed", "error": emails_data["error"]})

        # Write each email into Google Sheet (TEST MODE)
        results = []
        for email in emails_data["emails"]:
            row_status = write_email_to_sheet(email)
            results.append({"email": email, "sheet_update": row_status})

        return jsonify({
            "status": "success",
            "emails": emails_data["emails"],
            "sheet_results": results
        })

    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)})
