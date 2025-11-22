from flask import Flask, request, jsonify, render_template, session, redirect
import json
import os

# App
app = Flask(
    __name__,
    template_folder="dashboard/templates",
    static_folder="dashboard/static"
)

# --------------------------------------------------
# Load config.json
# --------------------------------------------------
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

# Login credentials (use the keys from config.json per Option B)
LOGIN_USER = CONFIG.get("username", "")
LOGIN_PASS = CONFIG.get("password", "")

# Secret key for sessions (simple for local dev; replace for production)
app.secret_key = CONFIG.get("flask_secret", "rfq_secret_123")

# Initialize dashboard.auth (no circular import)
from dashboard import auth as dashboard_auth
dashboard_auth.init_auth(CONFIG)

# Import require_login after init to avoid circular problems
from dashboard.auth import require_login

# Import other modules
from email_reader import fetch_latest_emails
from sheet_reader import read_sheet_values
from dashboard.backend_api import api_blueprint

# --- STEP 3 IMPORTS (Email Parser + Sheet Writer) ---
from email_parser import parse_email
from sheet_writer import SheetWriter


# --------------------------------------------------
# LOGIN PAGE
# --------------------------------------------------
@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_submit():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    if username == LOGIN_USER and password == LOGIN_PASS:
        session["logged_in"] = True
        return redirect("/dashboard")

    return "Invalid credentials", 401


# --------------------------------------------------
# DASHBOARD PAGE
# --------------------------------------------------
@app.route("/dashboard")
@require_login
def dashboard_home():
    return render_template("index.html")


# --------------------------------------------------
# Shadow Mode Trigger
# --------------------------------------------------
@app.route("/run_shadow")
@require_login
def run_shadow_mode():
    try:
        emails = fetch_latest_emails()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"emails_found": len(emails), "emails": emails})


# --------------------------------------------------
# Register backend API
# --------------------------------------------------
app.register_blueprint(api_blueprint, url_prefix="/api")


# --------------------------------------------------
# STEP-3: PROCESS EMAILS (FULL AUTOMATION)
# --------------------------------------------------
@app.route("/process_emails", methods=["GET"])
@require_login
def process_emails():
    try:
        # Initialize Sheet Writer
        sheet_id = CONFIG.get("sheet_id")
        writer = SheetWriter(sheet_id)

        # Fetch emails from Gmail
        emails = fetch_latest_emails()

        results = []
        for mail in emails:
            subject = mail.get("subject", "")
            body = mail.get("body", "")
            sender_name = mail.get("sender_name", "")
            sender_email = mail.get("sender_email", "")
            attachments = mail.get("attachments", [])

            # Parse into JSON (Step-1 logic)
            parsed = parse_email(
                subject=subject,
                body=body,
                sender_name=sender_name,
                sender_email=sender_email,
                attachments=attachments
            )

            # Write to Google Sheet (Step-2 logic)
            result = writer.write_email(parsed)

            results.append({
                "email_subject": subject,
                "type": parsed.get("type"),
                "uid": parsed.get("uid"),
                "rfq_no": parsed.get("rfq_no"),
                "sheet_result": result
            })

        return jsonify({
            "status": "success",
            "processed": len(results),
            "results": results
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# --------------------------------------------------
# SERVER START
# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
