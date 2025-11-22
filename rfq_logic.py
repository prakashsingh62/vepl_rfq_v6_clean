from datetime import datetime

def process_rfq_data(sheet_values):
    # Shadow mode basic placeholder
    # Real Level-5 logic will be inserted later

    summary = {
        "high": 0,
        "medium": 0,
        "low": 0,
        "vendor_pending": 0,
        "quotation_received": 0,
        "clarification": 0,
        "post_offer": 0,
        "overdue": 0,
        "client_followup": 0
    }

    return {
        "summary": summary,
        "high": [],
        "medium": [],
        "low": [],
        "vendor_pending": [],
        "quotation_received": [],
        "clarification": [],
        "post_offer": [],
        "overdue": [],
        "client_followup": []
    }
