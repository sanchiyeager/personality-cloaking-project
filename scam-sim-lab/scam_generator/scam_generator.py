import os
import random
from datetime import datetime
from typing import Dict

WATERMARK = "[SIMULATION ONLY]"

TEMPLATES = {
    "phishing": [
        "Suspicious login detected. Confirm your identity.",
        "Your bank account has been locked. Verify immediately.",
        "Unusual activity found on your account. Please validate your details."
    ],
    "investment": [
        "Guaranteed profit opportunity with zero risk!",
        "Exclusive crypto investment plan for selected users.",
        "Limited time offer: double your money fast."
    ],
    "romance": [
        "I trust you deeply but I need help urgently.",
        "I feel a strong connection with you. Can you help me?",
        "I am stuck in a foreign country and need assistance."
    ]
}

def generate_message(category: str) -> str:
    """
    Generate a simulation-only scam message for the given category.
    Valid categories: phishing, investment, romance
    """
    category = (category or "").strip().lower()
    if category not in TEMPLATES:
        raise ValueError("Invalid category. Use: phishing, investment, romance")

    return f"{WATERMARK} {random.choice(TEMPLATES[category])}"

def log_interaction(category: str, message: str, log_path: str = "logs/sim_log.txt") -> None:
    """
    Log an interaction to a file (creates logs folder if missing).
    """
    folder = os.path.dirname(log_path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {category} | {message}\n")

def generate_and_log(category: str, log_path: str = "logs/sim_log.txt") -> Dict[str, str]:
    """
    Convenience function: generate a message and log it.
    """
    msg = generate_message(category)
    log_interaction(category, msg, log_path=log_path)
    return {"category": category.strip().lower(), "message": msg}
