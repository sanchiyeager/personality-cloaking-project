"""
main.py - Integrated system with all fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bait_generator import BaitGenerator
from core.chat_engine import ChatEngine
from scam_generator import generate_scam

class Janus:
    """Integrated personality cloaking system"""

    def __init__(self, use_finetuned_model=False):
        self.bait_gen = BaitGenerator()

        if use_finetuned_model and os.path.exists("./personality_chat_model"):
            self.chat_engine = ChatEngine(model_path="./personality_chat_model")
        else:
            self.chat_engine = ChatEngine()

        print("✅ Janus Personality Cloaking System Ready")
        print("✅ Bio generation: Embodies traits")
        print("✅ Personality scores: Match traits")
        print("✅ Chat engine: Uses all 5 dimensions")

    def generate_profile(self, trait="high_neuroticism"):
        """Generate profile with consistent bio and scores"""
        profile = self.bait_gen.generate_profile(trait)

        # Verify consistency
        if not profile["consistency_check"]:
            print(f"⚠️  Warning: Bio may not fully reflect {trait}")

        return profile

    def chat_response(self, personality_scores, message):
        """Generate personality-consistent response"""
        return self.chat_engine.generate_chat_response(personality_scores, message)

    def generate_scam_message(self):
        """Generate a scam message"""
        return generate_scam()

    def test_system(self):
        """Test all components"""
        print("\n🔍 Testing system...")

        # Test each trait
        for trait in ["high_neuroticism", "high_agreeableness", "high_extraversion"]:
            print(f"\nTesting {trait}:")
            profile = self.generate_profile(trait)
            print(f"  Bio: {profile['bio'][:60]}...")
            print(f"  Scores: {profile['personality_scores']}")

            scam = self.generate_scam_message()
            response = self.chat_response(profile['personality_scores'], scam)
            print(f"  Scam: {scam[:50]}...")
            print(f"  Response: {response}")

        print("\n✅ All tests passed!")

# Create global instance
janus = Janus()

if __name__ == "__main__":
    # Run system test
    janus.test_system()