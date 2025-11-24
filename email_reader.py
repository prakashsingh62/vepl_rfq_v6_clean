import imaplib
import email
from email.header import decode_header

import os


# ---------------------------------------------------------
# READ EMAILS USING ENVIRONMENT VARIABLES
# ---------------------------------------------------------
def read_emails():
    try:
        imap_user = os.getenv("EMAIL_USER")
        imap_pass = os.getenv("EMAIL_APP_PASSWORD")

        if not imap_user or not imap_pass:
            return {"error": "IMAP credentials missing", "emails": []}

        imap_server = "imap.gmail.com"

        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(imap_user, imap_pass)
        mail.select("inbox")

        status, messages = mail.search(None, "ALL")
        email_list = []

        for num in messages[0].split()[-10:]:  # last 10 emails only
            status, msg_data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            from_ = msg["From"]
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")

            date = msg["Date"]

            email_list.append({
                "from": from_,
                "subject": subject,
                "date": date
            })

        mail.logout()
        return email_list

    except Exception as e:
        return {"error": str(e), "emails": []}
