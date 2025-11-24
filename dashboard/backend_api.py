from flask import Blueprint, jsonify
from email_reader import read_emails

api_blueprint = Blueprint("api", __name__)

@api_blueprint.route("/process_emails", methods=["GET"])
def process_emails():
    try:
        result = read_emails()

        # If IMAP reader failed, show safe fallback
        if result.get("status") != "success":
            return jsonify({
                "status": "failed",
                "error": result.get("error", "Email fetch error"),
                "emails": []
            })

        emails = result.get("emails", [])

        # SAFE minimal response (no heavy parsing)
        return jsonify({
            "status": "success",
            "count": len(emails),
            "emails": emails
        })

    except Exception as e:
        # Absolute catch-all safety
        return jsonify({
            "status": "failed",
            "error": str(e),
            "emails": []
        })
