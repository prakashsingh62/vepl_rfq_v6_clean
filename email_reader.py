import imaplib
import email
from email.header import decode_header
import os
import re
from bs4 import BeautifulSoup
print("USING NEW EMAIL_READER")
# ---------------------------------------------------------
# HTML → CLEAN TEXT (Medium Clean)
# ---------------------------------------------------------
def clean_html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")

    # Remove script/style/img
    for tag in soup(["script", "style", "img"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    # Remove tracking / huge URLs
    text = re.sub(r'http\S+', '', text)

    # Remove excessive blank lines
    text = re.sub(r'\n{2,}', '\n', text)

    return text.strip()


# ---------------------------------------------------------
# CLEAN ONLY THE LATEST MESSAGE FROM EMAIL THREAD
# ---------------------------------------------------------
def extract_latest_message(text):
    if not text:
        return ""

    text = text.replace("\r", "")

    # Remove reply history
    text = re.split(r"\nOn .*wrote:", text, flags=re.IGNORECASE)[0]

    # Remove "From:" blocks
    text = re.split(r"\nFrom: ", text)[0]

    # Remove original message header
    text = re.split(r"Original Message", text, flags=re.IGNORECASE)[0]

    # Remove signatures
    text = re.split(r"Regards,|Warm Regards,|Best Regards,|Thanks,|Thank you", text)[0]

    # Remove reply markers >, >>>
    text = re.sub(r"^>+ ?", "", text, flags=re.MULTILINE)

    # Remove blank lines
    text = re.sub(r"\n{2,}", "\n", text)

    return text.strip()


# ---------------------------------------------------------
# RFQ EXTRACTOR
# ---------------------------------------------------------
def extract_rfq_data(subject, body):
    text = f"{subject}\n{body}"

    rfq_patterns = [
        r'\bRFQ[:\s-]*([A-Za-z0-9-_/]+)',
        r'\bEnquiry[:\s-]*([A-Za-z0-9-_/]+)',
        r'\bEnq[:\s-]*([A-Za-z0-9-_/]+)',
        r'\bInquiry[:\s-]*([A-Za-z0-9-_/]+)',
        r'\b2800\d{5,}\b'
    ]

    rfq_no = ""
    for p in rfq_patterns:
        match = re.search(p, text, re.IGNORECASE)
        if match:
            rfq_no = match.group(1)
            break

    qty = ""
    qty_match = re.search(r'\b(Qty|Quantity)[:\s]*([\d\.]+)', text, re.IGNORECASE)
    if qty_match:
        qty = qty_match.group(2)

    part = ""
    part_match = re.search(r'(Part\s*Number|Model|PN|Item Code)[:\s-]*([A-Za-z0-9-_/]+)', text, re.IGNORECASE)
    if part_match:
        part = part_match.group(2)

    desc = ""
    desc_match = re.search(r'(Description|Desc)[:\s-]*(.*)', text, re.IGNORECASE)
    if desc_match:
        desc = desc_match.group(2).strip()

    return {
        "rfq_no": rfq_no,
        "qty": qty,
        "part": part,
        "description": desc
    }


# ---------------------------------------------------------
# SAFE IMAP EMAIL READER (HTML + TEXT VERSION)
# ---------------------------------------------------------
def read_emails(imap_user=None, imap_pass=None):
    try:
        imap_user = os.getenv("IMAP_USER")
        imap_pass = os.getenv("IMAP_PASS")

        if not imap_user or not imap_pass:
            return {"status": "failed", "error": "IMAP credentials missing", "emails": []}

        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(imap_user, imap_pass)
        mail.select("INBOX")

        _, data = mail.search(None, "ALL")
        ids = data[0].split()

        emails_list = []

        for num in ids[-10:]:
            _, msg_data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            # SUBJECT
            raw_subject = msg.get("Subject")
            subject = ""
            if raw_subject:
                try:
                    s, enc = decode_header(raw_subject)[0]
                    subject = s.decode(enc or "utf-8", errors="ignore") if isinstance(s, bytes) else s
                except:
                    subject = raw_subject

            # FROM / DATE
            sender = msg.get("From") or ""
            date = msg.get("Date") or ""

            # BODY (HTML or TEXT)
            body = ""
            try:
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()

                        if ctype == "text/plain":
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            break

                        if ctype == "text/html":
                            html_content = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            body = clean_html_to_text(html_content)
                            break

                else:
                    if msg.get_content_type() == "text/html":
                        html_content = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                        body = clean_html_to_text(html_content)
                    else:
                        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

            except:
                body = ""

            # CLEAN latest message
            body = extract_latest_message(body)

            # PARSE RFQ DETAILS
            parsed = extract_rfq_data(subject, body)

            emails_list.append({
                "date": date,
                "from": sender,
                "subject": subject,
                "body": body,
                "rfq_no": parsed["rfq_no"],
                "qty": parsed["qty"],
                "part": parsed["part"],
                "description": parsed["description"]
            })

        mail.logout()
        return {"status": "success", "emails": emails_list}

    except Exception as e:
        return {"status": "failed", "error": str(e), "emails": []}
