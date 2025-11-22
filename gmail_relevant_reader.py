# gmail_relevant_reader.py
# Level-6 Enterprise Relevant Gmail Reader (Optimized)

import base64
import re
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from email.utils import parsedate_to_datetime

# RFQ patterns
RFQ_PATTERNS = [
    r"\bRFQ[:\s-]*([A-Za-z0-9-_/]+)\b",
    r"\bEnquiry[:\s-]*([A-Za-z0-9-_/]+)\b",
    r"\bEnq[:\s-]*([A-Za-z0-9-_/]+)\b",
    r"\b2800\d{5,}\b"              # Your RFQ No pattern
]

KEYWORDS = [
    "quotation", "offer", "scope", "proposal", "commercial",
    "technical", "clarification", "price", "delivery", "terms"
]

def extract_text(payload):
    """Extract readable text from Gmail payload."""
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] in ["text/plain", "text/html"]:
                data = part["body"]["data"]
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    if "body" in payload and "data" in payload["body"]:
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
    return ""


def extract_rfq_numbers(text):
    """Return all RFQ numbers found inside email."""
    matches = []
    for pattern in RFQ_PATTERNS:
        matches += re.findall(pattern, text, flags=re.IGNORECASE)
    return list(set(matches))


def build_gmail_service(creds):
    return build("gmail", "v1", credentials=creds)


def fetch_relevant_emails(creds, target_rfqs=None):
    """
    Read ONLY important RFQ emails:
    - Last 10 days
    - Matching RFQ No
    - Or containing RFQ keywords
    """
    service = build_gmail_service(creds)

    date_cutoff = (datetime.utcnow() - timedelta(days=10)).strftime("%Y/%m/%d")
    query = f"after:{date_cutoff} (subject:RFQ OR subject:quotation OR subject:offer OR 'price')"

    results = service.users().messages().list(
        userId="me", q=query, maxResults=50
    ).execute()

    msgs = results.get("messages", [])
    relevant = []

    for m in msgs:
        msg = service.users().messages().get(userId="me", id=m["id"]).execute()

        payload = msg["payload"]
        snippet = msg.get("snippet", "")
        text = extract_text(payload)
        full_text = snippet + " " + text

        # 1 — Contains RFQ No
        rfqs_found = extract_rfq_numbers(full_text)

        # 2 — Has Important Words
        has_keyword = any(k.lower() in full_text.lower() for k in KEYWORDS)

        # 3 — Direct match with current sheet RFQs
        match_target = False
        if target_rfqs:
            match_target = any(r in full_text for r in target_rfqs)

        # If any condition matches → RELEVANT
        if rfqs_found or has_keyword or match_target:
            relevant.append({
                "id": m["id"],
                "snippet": snippet,
                "rfqs_found": rfqs_found,
                "text": text,
                "date": msg.get("internalDate"),
            })

    return relevant
