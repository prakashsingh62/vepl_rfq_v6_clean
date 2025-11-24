from flask import Blueprint, request, jsonify
from email_reader import read_emails
from sheet_writer import write_email_to_sheet_test_mode

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route("/api/process_emails", methods=["GET"])
def process_emails():
    try:
        # Read IMAP credentials
        imap_user = request.args.get("imap_user")
        imap_pass = request.args.get("imap_pass")

        if not imap_user or not imap_pass:
            return jsonify({"status": "failed", "error": "IMAP credentials missing"})

        # Read emails
        data = read_emails(imap_user, imap_pass)

        if isinstance(data, list):
            # Write to test sheet
            write_email_to_sheet_test_mode(data)
            return jsonify({"status": "success", "message": "Emails processed", "count": len(data)})

        return jsonify({"status": "failed", "error": "Unexpected response type"})

    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)})
