import imaplib
import email
from email.header import decode_header
import os


def read_emails(imap_user=None, imap_pass=None):
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

            raw_subject = msg.get("Subject")
            if raw_subject:
                subject, enc = decode_header(raw_subject)[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(enc or "utf-8", errors="ignore")
            else:
                subject = ""

            # NEW: Always-return-safe-body
            body = ""
            try:
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        if ctype == "text/plain":
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            break
                else:
                    body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
            except:
                body = ""

            emails_list.append({
                "date": msg.get("Date"),
                "from": msg.get("From"),
                "subject": subject,
                "body": body       # REQUIRED ✔ FIXED
            })

        mail.logout()

        return {"status": "success", "emails": emails_list}

    except Exception as e:
        return {"status": "failed", "error": str(e), "emails": []}
