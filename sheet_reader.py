# sheet_reader.py
from dashboard.auth import get_config

def read_sheet_values():
    """
    Returns list-of-lists representing sheet rows.
    Requires: gspread + service account or other auth.
    This helper is defensive — if not configured, raises a clear error.
    """
    cfg = get_config() or {}
    sheet_id = cfg.get("sheet_id")
    sheet_range = cfg.get("sheet_range")

    if not sheet_id or not sheet_range:
        raise RuntimeError("sheet_id or sheet_range missing from config.json")

    try:
        import gspread
    except ModuleNotFoundError:
        raise RuntimeError("gspread not installed. Run: pip install gspread oauth2client")

    # For quick local dev we try to use gspread's client from environment variable JSON (if available)
    # You must set up gspread authentication (service account or OAuth).
    try:
        gc = gspread.service_account()  # expects GOOGLE_APPLICATION_CREDENTIALS or service_account.json in cwd
        sh = gc.open_by_key(sheet_id)
        # If sheet_range includes sheet name, gspread can fetch range via worksheet
        # Simplest approach: read first worksheet values if range not exact
        try:
            values = sh.sheet1.get(sheet_range)
        except Exception:
            # fallback: get all values
            values = sh.sheet1.get_all_values()
        return values
    except Exception as e:
        raise RuntimeError("Sheet reader error: " + str(e))


# Utility: If you need to extract active RFQs, include the earlier extract_active_rfqs function
def extract_active_rfqs(values):
    if not values or len(values) < 2:
        return []
    headers = [str(h).strip() for h in values[0]]
    rows = values[1:]

    def find(names):
        for n in names:
            if n in headers:
                return headers.index(n)
        return -1

    idx = {
        "rfq": find(["RFQ NO", "RFQ NO.", "RFQ_NO", "INQUIRY NO"]),
        "uid": find(["UID NO"]),
        "client": find(["CUSTOMER NAME", "CLIENT NAME", "CLIENT"]),
        "vendor": find(["VENDOR"]),
        "current": find(["CURRENT STATUS"]),
        "final": find(["FINAL STATUS"])
    }

    def normalize(v):
        return "" if v is None else str(v).strip()

    def is_active(current, final):
        if not current and not final:
            return True
        c = (current or "").lower()
        f = (final or "").lower()
        closed_words = ["submitted", "regret", "closed", "completed", "order", "cancelled"]
        for w in closed_words:
            if w in c or w in f:
                return False
        return True

    active = []
    for r in rows:
        rfq = normalize(r[idx["rfq"]]) if idx["rfq"] != -1 and idx["rfq"] < len(r) else ""
        if not rfq:
            continue
        current = normalize(r[idx["current"]]) if idx["current"] != -1 and idx["current"] < len(r) else ""
        final = normalize(r[idx["final"]]) if idx["final"] != -1 and idx["final"] < len(r) else ""
        if not is_active(current, final):
            continue
        active.append({
            "rfq": rfq,
            "uid": normalize(r[idx["uid"]]) if idx["uid"] != -1 and idx["uid"] < len(r) else "",
            "client": normalize(r[idx["client"]]) if idx["client"] != -1 and idx["client"] < len(r) else "",
            "vendor": normalize(r[idx["vendor"]]) if idx["vendor"] != -1 and idx["vendor"] < len(r) else "",
            "current": current,
            "final": final
        })
    return active
