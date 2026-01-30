import random
from datetime import datetime
import os

# Create logs folder if it does not exist
os.makedirs("logs", exist_ok=True)

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

print("\n--- Scam Simulation Generator ---")
print("Categories: phishing, investment, romance")

category = input("Enter category: ").strip().lower()

if category not in TEMPLATES:
    print("\nInvalid category. Please choose from: phishing, investment, romance")
else:
    message = random.choice(TEMPLATES[category])
    final_message = "[SIMULATION ONLY] " + message

    print("\nGenerated Message:\n", final_message)

    # Log the interaction
    with open("logs/sim_log.txt", "a") as f:
        f.write(f"{datetime.now()} | {category} | {final_message}\n")
