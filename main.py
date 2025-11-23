from flask import Flask, render_template, request, redirect, jsonify
import json
import logging

from rfq_logic import process_rfq_data
from email_reader import read_emails

app = Flask(__name__)

# ---------------------------------------------------------
# RUN SHADOW MODE
# ---------------------------------------------------------
@app.route("/run_shadow", methods=["GET"])
def run_shadow():
    try:
        app.logger.info("==== Shadow Mode Started ====")

        # Run RFQ logic (read-only)
        result = process_rfq_data(shadow_mode=True)

        # Log to Render logs
        app.logger.info("Shadow Mode Output: %s", json.dumps(result, indent=2))

        # Return to browser
        return jsonify({
            "status": "Shadow Mode executed",
            "data": result
        })

    except Exception as e:
        app.logger.error("Shadow Mode Error: %s", str(e))
        return f"Shadow Mode Failed: {str(e)}", 500


# ---------------------------------------------------------
# PROCESS EMAILS
# ---------------------------------------------------------
@app.route("/process_emails", methods=["GET"])
def process_emails():
    try:
        app.logger.info("==== Email Processing Started ====")

        # Read emails using your Level-5 logic
        email_data = read_emails()

        # Log to Render logs
        app.logger.info("Email Parser Output: %s", json.dumps(email_data, indent=2))

        # Send clean JSON to browser
        return jsonify({
            "status": "Emails processed successfully",
            "emails": email_data
        })

    except Exception as e:
        app.logger.error("Email Processing Error: %s", str(e))
        return f"Email Processing Failed: {str(e)}", 500
