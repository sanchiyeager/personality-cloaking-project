import os, re

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"
SAFE_WATERMARK = "[SIMULATION ONLY]"

LINK_RE = re.compile(r"https?://", re.I)
EMAIL_RE = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b")
PHONE_RE = re.compile(r"\b(\+?\d[\d\s-]{7,}\d)\b")
PAYMENT_RE = re.compile(r"(upi|bank|otp|crypto|bitcoin|wallet)", re.I)

def safety_check(text: str):
    if not SIMULATION_MODE:
        return False, "SIMULATION_MODE must be true"
    if SAFE_WATERMARK not in text:
        return False, "Missing watermark"
    if LINK_RE.search(text):
        return False, "Links blocked"
    if EMAIL_RE.search(text):
        return False, "Emails blocked"
    if PHONE_RE.search(text):
        return False, "Phones blocked"
    if PAYMENT_RE.search(text):
        return False, "Payment words blocked"
    return True, "OK"
