# dashboard/backend_api.py

from flask import Blueprint, jsonify
import json

from rfq_logic import process_rfq_data
from email_reader import read_emails

api_blueprint = Blueprint("api", __name__)

# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------
@api_blueprint.route("/health")
def health():
    return jsonify({"status": "ok"})


# ---------------------------------------------------------
# RUN SHADOW MODE
# ---------------------------------------------------------
@api_blueprint.route("/run_shadow", methods=["GET"])
def run_shadow():
    try:
        result = process_rfq_data(shadow_mode=True)

        return jsonify({
            "status": "Shadow Mode executed",
            "data": result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------
# PROCESS EMAILS
# ---------------------------------------------------------
@api_blueprint.route("/process_emails", methods=["GET"])
def process_emails():
    try:
        email_data = read_emails()

        return jsonify({
            "status": "Emails processed successfully",
            "emails": email_data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
