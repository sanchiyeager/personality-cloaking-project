# scam_templates.py
# SAFE SIMULATION templates (watermarked)

import random

SAFE_WATERMARK = "[SIMULATION ONLY]"

TEMPLATES = {
    "phishing": [
        {
            "subject": f"{SAFE_WATERMARK} Account verification alert",
            "message": f"{SAFE_WATERMARK}\nThis is a simulated phishing-style message for training.\nTraining tip: verify sender domain and avoid sharing passwords."
        }
    ],
    "romance": [
        {
            "subject": f"{SAFE_WATERMARK} Thinking of you",
            "message": f"{SAFE_WATERMARK}\nThis is a simulated romance-scam style message for awareness.\nTraining tip: watch for quick emotional bonding and secrecy."
        }
    ],
    "investment": [
        {
            "subject": f"{SAFE_WATERMARK} Limited-time investment offer",
            "message": f"{SAFE_WATERMARK}\nThis is a simulated investment-scam style message.\nTraining tip: beware guaranteed returns and pressure tactics."
        }
    ]
}

def generate_template(kind: str):
    kind = kind.lower().strip()
    if kind not in TEMPLATES:
        raise ValueError(f"Unknown kind: {kind}. Use one of: {list(TEMPLATES.keys())}")
    return random.choice(TEMPLATES[kind])
