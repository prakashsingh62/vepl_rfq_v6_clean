import imaplib
import email
import os
import json

def read_emails():

    # 1️⃣ Try environment variables first
    gmail_user = os.getenv("GMAIL_USER")
    email_app_password = os.getenv("EMAIL_APP_PASSWORD")

    # 2️⃣ If environment variables missing → load config.json
    if not gmail_user or not email_app_password:
        try:
            with open("config.json") as f:
                config = json.load(f)

            gmail_user = gmail_user or config.get("gmail_user")
            email_app_password = email_app_password or config.get("email_app_password")

        except Exception as e:
            return {"error": f"Unable to load config.json: {str(e)}"}

    # 3️⃣ If still missing → return error
    if not gmail_user or not email_app_password:
        return {"error": "Gmail credentials not set in environment or config.json."}

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(gmail_user, email_app_password)
        mail.select("inbox")

        status, messages = mail.search(None, "ALL")

        email_list = []
        for num in messages[0].split()[-10:]:
            status, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])

            email_list.append({
                "from": msg["From"],
                "subject": msg["Subject"],
                "date": msg["Date"]
            })

        mail.close()
        mail.logout()

        return {"status": "success", "emails": email_list}

    except Exception as e:
        return {"error": str(e)}
