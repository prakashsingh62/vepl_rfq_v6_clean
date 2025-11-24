import imaplib
import email
from email.header import decode_header
import os


def read_emails(imap_user: str, imap_pass: str):
    """
    Reads unread emails from Gmail IMAP.
    ALWAYS returns a DICTIONARY so backend_api.py never breaks.
    """

    try:
        if not imap_user or not imap_pass:
            return {
                "emails": [],
                "error": "IMAP credentials missing",
                "status": "failed"
            }

        # -----------------------------------------
        # CONNECT TO IMAP SERVER
        # -----------------------------------------
        mail = imaplib.IMAP4_SSL("imap.gmail.com")

        try:
            mail.login(imap_user, imap_pass)
        except Exception as e:
            return {
                "emails": [],
                "error": f"Login failed: {str(e)}",
                "status": "failed"
            }

        # -----------------------------------------
        # FETCH UNREAD EMAILS
        # -----------------------------------------
        mail.select("inbox")

        _, message_numbers_raw = mail.search(None, 'UNSEEN')

        messages = message_numbers_raw[0].split()
        email_list = []

        for num in messages:
            _, msg_data = mail.fetch(num, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject, encoding = decode_header(msg.get("Subject", ""))[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors="ignore")

            from_email = msg.get("From", "")

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    if ctype == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        except:
                            body = ""
            else:
                try:
                    body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                except:
                    body = ""

            email_list.append({
                "subject": subject,
                "from": from_email,
                "body": body.strip()
            })

        mail.logout()

        # -----------------------------------------
        # FINAL FIXED RETURN (DICT)
        # -----------------------------------------
        return {
            "emails": email_list,
            "count": len(email_list),
            "status": "success"
        }

    except Exception as e:
        return {
            "emails": [],
            "error": str(e),
            "status": "failed"
        }
