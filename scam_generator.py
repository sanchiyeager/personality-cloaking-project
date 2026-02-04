# scam_generator.py
import random
def generate_scam():
    """Generate a scam message"""
    scams = [
        "URGENT: Your bank account has been hacked! Click here to secure it!",
        "Congratulations! You've won a free iPhone! Just pay $50 shipping.",
        "I'm a Nigerian prince and need your help transferring $10 million.",
        "Your computer has a virus! Download this software immediately.",
        "Limited time offer: 90% discount on Amazon gift cards!",
        "Your package delivery failed. Click here to reschedule.",
        "You've been selected for a remote job paying $5000/month!"
    ]
    return random.choice(scams)
# For backward compatibility
class ScamGenerator:
    def generate(self):
        return generate_scam()
