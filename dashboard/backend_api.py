from flask import Blueprint, jsonify
from email_reader import read_emails
from sheet_writer import write_email_to_sheet_test_mode

api_blueprint = Blueprint("api_blueprint", __name__)

@api_blueprint.route("/process_emails", methods=["GET"])
def process_emails():
    try:
        result = read_emails()
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)})
