import imaplib
import email
from email.header import decode_header
import os

# -------------------------------------------------------------
# READ EMAILS USING ENVIRONMENT VARIABLES
# -------------------------------------------------------------
def read_emails(imap_user, imap_pass):
    try:
        # Fetch from Render env
        imap_user = os.getenv("IMAP_USER")
        imap_pass = os.getenv("IMAP_PASS")

        if not imap_user or not imap_pass:
            return {"status": "failed", "error": "IMAP credentials missing", "emails": []}

        imap_server = "imap.gmail.com"

        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(imap_user, imap_pass)
        mail.select("inbox")

        _, message_numbers_raw = mail.search(None, "ALL")
        message_numbers = message_numbers_raw[0].split()

        emails_list = []

        for num in message_numbers[-10:]:  # Last 10 emails
            _, msg_data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            date = msg.get("Date")
            subject, encoding = decode_header(msg.get("Subject"))[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors="ignore")

            from_ = msg.get("From")

            emails_list.append({
                "date": date,
                "from": from_,
                "subject": subject
            })

        mail.logout()

        return {
            "status": "success",
            "emails": emails_list
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "emails": []
        }
