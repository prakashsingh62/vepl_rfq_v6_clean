import re
from datetime import datetime

# ============================================================
# TEXT CLEANER
# ============================================================
def preprocess_email(body: str) -> str:
    if not body:
        return ""
    text = body.replace("\r", " ").replace("\n", " ").strip()

    signature_keys = [
        "regards", "thanks", "thank you", "best wishes", "warm regards",
        "sent from my iphone", "sent from my android", "confidentiality notice"
    ]
    for key in signature_keys:
        idx = text.lower().find(key)
        if idx != -1:
            text = text[:idx]

    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ============================================================
# EXTRACT UID — (VEPLXXXXXXXXD)
# ============================================================
def extract_uid(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"(VEPL[0-9]{8,14}D)", text, re.IGNORECASE)
    return m.group(1).upper() if m else ""


# ============================================================
# RFQ No MUST be FIRST FIELD
# ============================================================
def extract_rfq_no(text: str) -> str:
    if not text:
        return ""

    patterns = [
        r"RFQ[\s:\-]*([0-9]{6,20})",
        r"ENQUIRY[\s:\-]*NO[\s:\-]*([0-9]{6,20})",
        r"INQUIRY[\s:\-]*NO[\s:\-]*([0-9]{6,20})",
        r"REF[\s:\-]*([0-9]{6,20})"
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return ""


# ============================================================
# DUE DATE EXTRACTION
# ============================================================
def extract_due_date(text: str) -> str:
    if not text:
        return ""
    patterns = [
        r"due[\s\-]*date[\s:\-]*([0-9]{1,2}[\-\/][A-Za-z]{3,10}[\-\/][0-9]{2,4})",
        r"due[\s\-]*date[\s:\-]*([0-9]{1,2}[\-\/][0-9]{1,2}[\-\/][0-9]{2,4})"
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return ""


# ============================================================
# CUSTOMER / VENDOR NAME
# ============================================================
def extract_customer_name(sender_name: str, text: str) -> str:
    if sender_name:
        return sender_name.strip()

    patterns = [
        r"from[\s:\-]*([A-Za-z0-9 &.,\-]{3,50})",
        r"customer[\s:\-]*([A-Za-z0-9 &.,\-]{3,50})"
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ""


def extract_vendor_name(sender_name: str, text: str) -> str:
    if sender_name:
        return sender_name.strip()

    patterns = [
        r"from[\s:\-]*([A-Za-z0-9 &.,\-]{3,50})",
        r"vendor[\s:\-]*([A-Za-z0-9 &.,\-]{3,50})"
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ""


# ============================================================
# PRICE LINES
# ============================================================
def extract_price_lines(text: str):
    if not text:
        return []
    patt = r"(Rs\.?|INR|₹)\s*[0-9,]+(\.[0-9]+)?"
    return [m.group(0) for m in re.finditer(patt, text, re.IGNORECASE)]


# ============================================================
# CATEGORY DETECTOR — 9 TYPES
# ============================================================
def detect_email_type(text: str, subject: str) -> str:
    full = f"{subject} {text}".lower()

    # 1 → RFQ
    if any(k in full for k in ["rfq", "enquiry", "inquiry", "kindly quote", "requirement"]):
        return "RFQ"

    # 2 → QUOTATION
    if any(k in full for k in ["quotation attached", "please find quote", "our quote", "offer attached", "quotation", "quote attached"]):
        return "QUOTATION"

    # 3 → VENDOR_CLARIFICATION
    if any(k in full for k in [
        "send photo", "need photo", "send image", "share model", "send model",
        "need technical", "share datasheet", "need drawing", "more details required"
    ]):
        return "VENDOR_CLARIFICATION"

    # 4 → CLIENT_CLARIFICATION
    if any(k in full for k in [
        "need discount", "final discount", "delivery period", "need delivery",
        "share gad", "need revised quote", "need final price", "send documents"
    ]):
        return "CLIENT_CLARIFICATION"

    # 5 → REVISED_QUOTATION_VENDOR
    if any(k in full for k in ["revised quotation attached", "revised quote attached", "updated quotation"]):
        return "REVISED_QUOTATION_VENDOR"

    # 6 → REVISED_QUOTATION_CLIENT_REQUEST
    if any(k in full for k in [
        "send revised quote", "revise your quotation", "need updated quote",
        "need updated offer", "send revised offer"
    ]):
        return "REVISED_QUOTATION_CLIENT_REQUEST"

    # 7 → TECHNICAL_MODIFICATION_REQUEST
    if any(k in full for k in [
        "change to on/off", "change the valve", "modify valve", "change actuator",
        "change size", "change material", "change end connection", "technical change"
    ]):
        return "TECHNICAL_MODIFICATION_REQUEST"

    # 8 → POST_DISPATCH_DOCUMENTS
    if any(k in full for k in [
        "send tc", "send test certificate", "send warranty", "need invoice",
        "packing list", "dispatch documents", "send report"
    ]):
        return "POST_DISPATCH_DOCUMENTS"

    # 9 → MATERIAL_REJECTION
    if any(k in full for k in [
        "material rejected", "rejected due to", "ncr", "quality issue",
        "technical issue", "failed test"
    ]):
        return "MATERIAL_REJECTION"

    return "UNKNOWN"


# ============================================================
# MAIN PARSER
# ============================================================
def parse_email(subject: str, body: str, sender_name: str,
                sender_email: str, attachments: list):

    clean = preprocess_email(body)
    combined = f"{subject} {clean}"

    rfq_no = extract_rfq_no(combined)       # ALWAYS FIRST
    uid = extract_uid(combined)             # ALWAYS SECOND
    email_type = detect_email_type(clean, subject)

    customer = extract_customer_name(sender_name, combined)
    vendor = extract_vendor_name(sender_name, combined)
    due_date = extract_due_date(combined)
    price_lines = extract_price_lines(combined)

    return {
        "rfq_no": rfq_no,
        "uid": uid,
        "type": email_type,
        "subject": subject.strip(),
        "sender_name": sender_name.strip() if sender_name else "",
        "sender_email": sender_email.strip() if sender_email else "",
        "customer_name": customer,
        "vendor_name": vendor,
        "due_date": due_date,
        "price_lines": price_lines,
        "body_clean": clean,
        "attachments": attachments,
        "flags": {
            "is_rfq": email_type == "RFQ",
            "is_quotation": email_type == "QUOTATION",
            "is_vendor_clarification": email_type == "VENDOR_CLARIFICATION",
            "is_client_clarification": email_type == "CLIENT_CLARIFICATION",
            "is_revised_quote_vendor": email_type == "REVISED_QUOTATION_VENDOR",
            "is_revised_quote_client": email_type == "REVISED_QUOTATION_CLIENT_REQUEST",
            "is_modification": email_type == "TECHNICAL_MODIFICATION_REQUEST",
            "is_post_dispatch": email_type == "POST_DISPATCH_DOCUMENTS",
            "is_rejection": email_type == "MATERIAL_REJECTION"
        }
    }
