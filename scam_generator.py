import os
import random
from datetime import datetime

WATERMARK = "[SIMULATION ONLY]"

TEMPLATES = {
    "phishing": {
        "high_neuroticism": [
            "Your account is in danger. Act immediately to avoid loss.",
            "Urgent alert: suspicious activity detected. Verify now."
        ],
        "low_openness": [
            "Your account needs verification. Please confirm details.",
            "Security update required for your account."
        ],
        "default": [
            "Suspicious login detected. Confirm your identity."
        ]
    },
    "investment": {
        "high_extraversion": [
            "Exciting profit opportunity just for you! Join now.",
            "Don’t miss this exclusive investment chance!"
        ],
        "high_conscientiousness": [
            "Verified low-risk investment plan with guaranteed returns.",
            "Secure financial growth opportunity available."
        ],
        "default": [
            "Guaranteed profit opportunity with zero risk."
        ]
    },
    "romance": {
        "high_agreeableness": [
            "I trust you deeply and need your help urgently.",
            "You are the only one I can rely on."
        ],
        "default": [
            "I feel a strong connection with you. Can you help me?"
        ]
    }
}

def generate_message(category: str, target_personality: str = "default") -> str:
    category = category.lower()
    target_personality = target_personality.lower()

    if category not in TEMPLATES:
        raise ValueError("Invalid category")

    personality_templates = TEMPLATES[category]
    messages = personality_templates.get(target_personality,
                                          personality_templates["default"])

    return f"{WATERMARK} {random.choice(messages)}"


def log_interaction(category, target_personality, message, log_path="logs/sim_log.txt"):
    os.makedirs("logs", exist_ok=True)
    with open(log_path, "a") as f:
        f.write(f"{datetime.now()} | {category} | {target_personality} | {message}\n")


def generate_and_log(category, target_personality="default"):
    msg = generate_message(category, target_personality)
    log_interaction(category, target_personality, msg)
    return {"category": category, "target_personality": target_personality, "message": msg}
