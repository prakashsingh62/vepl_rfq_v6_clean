import imaplib
import email
from email.header import decode_header
import os
import re
from bs4 import BeautifulSoup
print("### LOADED EMAIL_READER FROM:", __file__)
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

        print("DEBUG: IMAP_USER =", imap_user)
        print("DEBUG: IMAP_PASS =", "(hidden)")
        print("DEBUG: Attempting IMAP login...")

        if not imap_user or not imap_pass:
            return {"status": "failed", "error": "IMAP credentials missing", "emails": []}

        # START IMAP
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            login_result = mail.login(imap_user, imap_pass)
            print("DEBUG: LOGIN RESULT =", login_result)
        except Exception as e:
            print("DEBUG: LOGIN ERROR =", str(e))
            return {"status": "failed", "error": f"LOGIN FAILED: {e}", "emails": []}

        # SELECT INBOX
        try:
            status, inbox_msg = mail.select("INBOX")
            print("DEBUG: SELECT RESULT =", status, inbox_msg)
        except Exception as e:
            print("DEBUG: SELECT ERROR =", str(e))
            return {"status": "failed", "error": f"SELECT FAILED: {e}", "emails": []}

        # SEARCH EMAILS
        try:
            status, data = mail.search(None, "ALL")
            print("DEBUG: SEARCH RESULT =", status, data)
        except Exception as e:
            print("DEBUG: SEARCH ERROR =", str(e))
            return {"status": "failed", "error": f"SEARCH FAILED: {e}", "emails": []}

        ids = data[0].split()
        emails_list = []

        return {"status": "success", "emails": emails_list}

    except Exception as e:
        print("FATAL ERROR:", str(e))
        return {"status": "failed", "error": str(e), "emails": []}
