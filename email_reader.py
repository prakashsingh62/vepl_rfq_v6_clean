import imaplib
import email
from email.header import decode_header
import base64

# ==================================================================
# SAFE DECODER — FIXES "Short substrate on input" and all bad emails
# ==================================================================

def safe_decode(payload):
    if payload is None:
        return ""

    # Try normal UTF-8 decode
    try:
        return payload.decode("utf-8")
    except:
        pass

    # Try base64 decode with padding
    try:
        padded = payload + b"==="
        return base64.b64decode(padded).decode("utf-8", errors="ignore")
    except:
        pass

    # Last fallback
    return "(Unable to decode email body)"

# ================================================================
# EMAIL CLEANER
# ================================================================

def clean_text(raw):
    if isinstance(raw, str):
        return raw
    try:
        decoded, charset = decode_header(raw)[0]
        if isinstance(decoded, bytes):
            return decoded.decode(charset or "utf-8", errors="ignore")
        return decoded
    except:
        return str(raw)

# ================================================================
# MAIN EMAIL READER FUNCTION
# ================================================================

def read_emails(imap_user, imap_pass, imap_server="imap.gmail.com"):
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(imap_user, imap_pass)
        mail.select("inbox")

        _, msgnums = mail.search(None, "ALL")
        emails = []

        for num in msgnums[0].split():
            try:
                _, msg_data = mail.fetch(num, "(RFC822)")
                if not msg_data or msg_data[0] is None:
                    continue

                msg = email.message_from_bytes(msg_data[0][1])

                # HEADER DETAILS
                from_address = clean_text(msg.get("From"))
                subject = clean_text(msg.get("Subject"))
                date_str = clean_text(msg.get("Date"))

                # BODY EXTRACTION (SAFE)
                body = ""

                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            payload = part.get_payload(decode=True)
                            body = safe_decode(payload)
                else:
                    payload = msg.get_payload(decode=True)
                    body = safe_decode(payload)

                emails.append({
                    "from": from_address,
                    "subject": subject,
                    "date": date_str,
                    "body": body
                })

            except Exception as inner_error:
                emails.append({
                    "from": "(error)",
                    "subject": "(error)",
                    "date": "",
                    "body": f"Error reading email: {str(inner_error)}"
                })

        mail.logout()

        return {
            "status": "success",
            "emails": emails
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
