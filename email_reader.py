# ------------------------------
# SAFE BODY DECODER (FINAL FIX)
# ------------------------------
import base64

def safe_decode(payload):
    try:
        return payload.decode()
    except:
        pass

    try:
        return base64.b64decode(payload + b'===').decode('utf-8', errors='ignore')
    except:
        return "(Unable to decode email body)"
