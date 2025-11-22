# email_reader.py
import imaplib
import email
from email.header import decode_header
import re
from dashboard.auth import get_config

def _safe_decode(header_value):
    if not header_value:
        return ""
    decoded = decode_header(header_value)
    parts = []
    for text, enc in decoded:
        if isinstance(text, bytes):
            try:
                parts.append(text.decode(enc or "utf-8", errors="ignore"))
            except:
                parts.append(text.decode("utf-8", errors="ignore"))
        else:
            parts.append(text)
    return "".join(parts).strip()

def fetch_latest_emails(mailbox="INBOX", limit=10):
    """
    Connects to Gmail IMAP using credentials from config and returns
    a list of recent messages (limited).
    """
    cfg = get_config() or {}
    user = cfg.get("gmail_user")
    app_password = cfg.get("email_app_password")

    if not user or not app_password:
        raise RuntimeError("Gmail credentials not set in config.json (gmail_user/email_app_password).")

    IMAP_HOST = "imap.gmail.com"
    try:
        imap = imaplib.IMAP4_SSL(IMAP_HOST)
        imap.login(user, app_password)
        imap.select(mailbox)
        # search for all emails, newest first
        status, data = imap.search(None, "ALL")
        if status != "OK":
            imap.logout()
            return []

        ids = data[0].split()
        ids = ids[-limit:] if len(ids) > limit else ids
        results = []

        for mail_id in reversed(ids):
            status, msg_data = imap.fetch(mail_id, "(RFC822)")
            if status != "OK":
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            subject = _safe_decode(msg.get("Subject"))
            frm = _safe_decode(msg.get("From"))
            date = msg.get("Date")
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    disp = str(part.get("Content-Disposition"))
                    if ctype == "text/plain" and "attachment" not in disp:
                        charset = part.get_content_charset() or "utf-8"
                        try:
                            body = part.get_payload(decode=True).decode(charset, errors="ignore")
                        except:
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
            else:
                charset = msg.get_content_charset() or "utf-8"
                body = msg.get_payload(decode=True).decode(charset, errors="ignore")

            results.append({
                "id": mail_id.decode() if isinstance(mail_id, bytes) else str(mail_id),
                "subject": subject,
                "from": frm,
                "date": date,
                "snippet": (body or "")[:800]
            })
        imap.logout()
        return results
    except imaplib.IMAP4.error as e:
        raise RuntimeError("IMAP error: " + str(e))
    except Exception as e:
        raise RuntimeError("Email reader error: " + str(e))
