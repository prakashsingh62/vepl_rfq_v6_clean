import imaplib
import email
from email.header import decode_header
import os

def read_emails(imap_user, imap_pass):
    try:
        imap_user = os.getenv("IMAP_USER")
        imap_pass = os.getenv("IMAP_PASS")

        if not imap_user or not imap_pass:
            return {"status": "failed", "error": "IMAP credentials missing", "emails": []}

        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(imap_user, imap_pass)
        mail.select("inbox")

        _, data = mail.search(None, "ALL")
        ids = data[0].split()

        emails_list = []

        for num in ids[-10:]:
            _, msg_data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            date = msg.get("Date")

            subject, enc = decode_header(msg.get("Subject"))[0]
            if isinstance(subject, bytes):
                subject = subject.decode(enc or "utf-8", errors="ignore")

            sender = msg.get("From")

            emails_list.append({
                "date": date,
                "from": sender,
                "subject": subject
            })

        mail.logout()

        return {"status": "success", "emails": emails_list}

    except Exception as e:
        return {"status": "failed", "error": str(e), "emails": []}
