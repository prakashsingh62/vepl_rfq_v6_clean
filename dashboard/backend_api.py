from flask import Blueprint, jsonify
from email_reader import read_emails
from sheet_writer import write_rfq_rows

api_blueprint = Blueprint("api", __name__)


# ---------------------------------------------------------
# FINAL LEVEL-6 ENDPOINT
# Reads emails → parses RFQs → writes to sheet → returns JSON
# ---------------------------------------------------------
@api_blueprint.route("/process_emails", methods=["GET"])
def process_emails():

    try:
        # 1. FETCH EMAILS (safe email_reader)
        result = read_emails()

        if result.get("status") != "success":
            return jsonify({
                "status": "failed",
                "error": result.get("error", "Email read error"),
                "emails": []
            })

        emails = result.get("emails", [])

        # 2. WRITE RFQ ROWS TO GOOGLE SHEET
        write_status = write_rfq_rows(emails)

        if write_status is not True:
            # write_status will contain error string
            return jsonify({
                "status": "failed",
                "error": f"Sheet write error: {write_status}",
                "emails": emails
            })

        # 3. RETURN CLEAN JSON RESPONSE
        return jsonify({
            "status": "success",
            "written": len(emails),
            "emails": emails
        })

    except Exception as e:
        return jsonify({
            "status": "failed",
            "error": str(e),
            "emails": []
        })
