import random

SIMULATION_TAG = "[SIMULATED TRAINING]"

templates = {
    "phishing": [
        "Your account needs verification.",
        "Suspicious login attempt detected."
    ],
    "romance": [
        "I trust you deeply but need help urgently."
    ],
    "investment": [
        "Guaranteed profit opportunity!"
    ]
}

def generate_scam():
    category = random.choice(list(templates.keys()))
    message = SIMULATION_TAG + " " + random.choice(templates[category])
    return message, category
